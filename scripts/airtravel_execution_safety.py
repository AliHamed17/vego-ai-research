"""Reversible guards for trusted Python offline orchestration, not an OS sandbox."""

from __future__ import annotations

import asyncio
import builtins
import io
import logging
import os
import socket
import sys
import time
from pathlib import Path

from airtravel_preflight_contract import MAX_BYTES, MAX_FILES, TIMEOUT, no_links

_ACTIVE = None


def _audit(event, args):
    guard = _ACTIVE
    if guard is None:
        return
    if event.startswith("socket.") and event not in {"socket.__new__"}:
        guard.network_attempt_count += 1
        raise PermissionError("network attempt forbidden")
    if event == "socket.__new__" and args[1] in (socket.AF_INET, socket.AF_INET6):
        guard.network_attempt_count += 1
        raise PermissionError("network socket forbidden")
    if (
        event.startswith(("subprocess.", "ctypes.", "winreg.", "os.exec", "os.spawn"))
        or event == "os.system"
    ):
        guard.violations += 1
        raise PermissionError("external process or credential/native access forbidden")
    if event == "import" and str(args[0]).split(".")[0] in {
        "openai",
        "anthropic",
        "keyring",
        "requests",
        "httpx",
        "urllib",
    }:
        guard.violations += 1
        raise PermissionError("provider/network/credential import forbidden")
    if event == "open":
        raw, mode, flags = args
        if isinstance(raw, int):
            raise PermissionError("unbound file descriptor")
        write = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        guard.check_path(Path(raw), write=write)
    elif event in {
        "os.mkdir",
        "os.remove",
        "os.rename",
        "os.rmdir",
        "os.link",
        "os.symlink",
        "os.chmod",
        "os.truncate",
    }:
        if event != "os.mkdir":
            raise PermissionError("destructive filesystem action forbidden")
        path = Path(args[0]).resolve()
        if not path.is_relative_to(guard.output):
            raise PermissionError("directory outside granted output")


sys.addaudithook(_audit)


class ExecutionGuard:
    def __init__(
        self, output, allowed_files, read_paths, *, max_files=MAX_FILES, max_bytes=MAX_BYTES
    ):
        self.output = output.resolve()
        self.allowed_files = set(allowed_files)
        self.read_paths = {p.resolve() for p in read_paths}
        self.max_files, self.max_bytes = max_files, max_bytes
        self.files = set()
        self.written = 0
        self.network_attempt_count = 0
        self.violations = 0

    def check_path(self, path, *, write):
        no_links(path)
        path = path.resolve()
        if write:
            if (
                not path.is_relative_to(self.output)
                or path.relative_to(self.output).as_posix() not in self.allowed_files
            ):
                self.violations += 1
                raise PermissionError("unexpected or outside output file")
            if path not in self.files and len(self.files) >= self.max_files:
                self.violations += 1
                raise PermissionError("output file quota")
            self.files.add(path)
        elif not path.is_relative_to(self.output) and path not in self.read_paths:
            self.violations += 1
            raise PermissionError("read outside explicit allowlist")

    def __enter__(self):
        global _ACTIVE
        if _ACTIVE is not None:
            raise PermissionError("nested execution guard")
        self.old_open, self.old_io = builtins.open, io.open
        self.old_connect = socket.create_connection
        self.old_bytecode = sys.dont_write_bytecode

        def denied(*args, **kwargs):
            self.network_attempt_count += 1
            raise PermissionError("network attempt forbidden")

        socket.create_connection = denied
        guard = self

        class Writer:
            def __init__(self, handle):
                self.handle = handle

            def write(self, data):
                length = (
                    len(data.encode(self.handle.encoding or "utf-8"))
                    if isinstance(data, str)
                    else len(data)
                )
                if guard.written + length > guard.max_bytes:
                    guard.violations += 1
                    raise PermissionError("output byte quota")
                guard.written += length
                return self.handle.write(data)

            def writelines(self, lines):
                for line in lines:
                    self.write(line)

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.handle.close()

            def __getattr__(self, name):
                return getattr(self.handle, name)

        def wrap(original):
            def opening(file, mode="r", *args, **kwargs):
                handle = original(file, mode, *args, **kwargs)
                return Writer(handle) if any(c in mode for c in "wax+") else handle

            return opening

        builtins.open, io.open = wrap(self.old_open), wrap(self.old_io)
        sys.dont_write_bytecode = True
        _ACTIVE = self
        return self

    def __exit__(self, *args):
        global _ACTIVE
        _ACTIVE = None
        builtins.open, io.open = self.old_open, self.old_io
        socket.create_connection = self.old_connect
        sys.dont_write_bytecode = self.old_bytecode


async def timed_operation(operation, runtime, *, timeout=TIMEOUT):
    """Bound the complete coroutine; cancellation cleanup precedes failure receipt."""
    original_client = runtime.LLMClient
    original_registry = getattr(runtime, "QARegistry", None)
    original_env = dict(os.environ)
    original_handlers = set(logging.getLogger().handlers)
    start = time.monotonic()
    # Environment is restored in finally; values never enter receipts.
    os.environ.clear()
    for name in ("SystemRoot", "WINDIR", "TEMP", "TMP"):
        if name in original_env:
            os.environ[name] = original_env[name]
    try:
        result = await asyncio.wait_for(operation(), timeout)
        return {**result, "timeout": False, "elapsed_seconds": time.monotonic() - start}
    except asyncio.TimeoutError:
        return {
            "status": "TECHNICAL_FAILED",
            "timeout": True,
            "technical_exception": "TimeoutError",
            "elapsed_seconds": time.monotonic() - start,
        }
    except Exception as exc:
        return {
            "status": "TECHNICAL_FAILED",
            "timeout": False,
            "technical_exception": type(exc).__name__,
            "elapsed_seconds": time.monotonic() - start,
        }
    finally:
        runtime.LLMClient = original_client
        if original_registry is not None:
            runtime.QARegistry = original_registry
        for handler in set(logging.getLogger().handlers) - original_handlers:
            logging.getLogger().removeHandler(handler)
            handler.close()
        os.environ.clear()
        os.environ.update(original_env)
