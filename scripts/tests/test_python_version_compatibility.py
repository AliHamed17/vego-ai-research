"""Every tracked script must compile under the oldest Python version CI runs.

CI runs a Python 3.10 job that executes ``pytest scripts/tests``, but its only *compile* step runs
under 3.13. A construct introduced in 3.12 could therefore sit in the tree indefinitely without
any job noticing, and that is exactly what happened: several renderers used PEP 701 nested
same-quote f-strings or backslashes inside f-string expressions, and all of them parsed on 3.13
and failed on 3.10.

The check is `compile()` under the **running** interpreter, so in the 3.10 CI job it is a genuine
3.10 check, and locally it is a check against whatever is installed. That is deliberate: an
earlier draft of this file used ``ast.parse(feature_version=(3, 10))``, which looked like a
version check but silently enforces nothing for f-strings, because 3.12+ parses them in the
tokenizer where ``feature_version`` does not reach. The negative controls below exist to catch
that class of self-deception: if the guard cannot reject a known-bad construct on this
interpreter, it says so rather than reporting a pass.

No provider is contacted, and sources are compiled, not imported or executed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OLDEST_SUPPORTED = (3, 10)
BACKSLASH = chr(92)

NESTED_SAME_QUOTE = 'x = f"{d["key"]}"\n'
BACKSLASH_IN_EXPRESSION = "x = f'{\" a=" + BACKSLASH + '"b' + BACKSLASH + "\"\" if c else \"\"}'\n"


def tracked_python_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "scripts/*.py", "src/*.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [ROOT / line for line in out.stdout.splitlines() if line.strip()]


FILES = tracked_python_files()
RUNNING_ENFORCES_OLD_FSTRING_RULES = sys.version_info < (3, 12)


def test_file_discovery_found_a_meaningful_set():
    assert len(FILES) > 20, "file discovery returned too few files to be meaningful"


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_compiles_under_the_running_interpreter(path: Path):
    source = path.read_text(encoding="utf-8")
    try:
        compile(source, str(path), "exec")
    except SyntaxError as exc:
        pytest.fail(
            f"{path.relative_to(ROOT)} does not compile under Python "
            f"{sys.version_info.major}.{sys.version_info.minor}: line {exc.lineno}: {exc.msg}"
        )


class TestTheGuardActuallyRejectsWhatItIsFor:
    """Negative controls. On 3.12+ these constructs became legal, so the guard is inert there."""

    @pytest.mark.skipif(
        not RUNNING_ENFORCES_OLD_FSTRING_RULES,
        reason="this interpreter is 3.12+, where both constructs are legal; the 3.10 CI job enforces them",
    )
    @pytest.mark.parametrize(
        "source,label",
        [(NESTED_SAME_QUOTE, "nested same-quote f-string"),
         (BACKSLASH_IN_EXPRESSION, "backslash inside an f-string expression")],
    )
    def test_known_bad_construct_is_rejected(self, source, label):
        with pytest.raises(SyntaxError):
            compile(source, "<control>", "exec")

    def test_the_hoisted_equivalent_is_accepted_everywhere(self):
        compile('attr = \' a="b"\' if c else ""\nx = f"{attr}"\n', "<control>", "exec")

    def test_this_file_declares_where_enforcement_actually_happens(self):
        assert OLDEST_SUPPORTED == (3, 10)
        assert __doc__ is not None and "3.10 CI job" in __doc__


@pytest.mark.skipif(sys.platform != "win32", reason="uses the Windows py launcher to find 3.10")
def test_an_installed_old_interpreter_also_compiles_every_file():
    probe = subprocess.run(["py", "-3.10", "-c", "pass"], capture_output=True, check=False)
    if probe.returncode != 0:
        pytest.skip("Python 3.10 is not installed on this machine")
    failures = []
    for path in FILES:
        result = subprocess.run(
            ["py", "-3.10", "-c",
             "import sys,pathlib;compile(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'),sys.argv[1],'exec')",
             str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append(f"{path.name}: {result.stderr.strip().splitlines()[-1]}")
    assert not failures, "files that do not compile under Python 3.10:\n" + "\n".join(failures)
