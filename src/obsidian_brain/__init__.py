"""Private, local-only storage that presents sanitized notes in an Obsidian vault."""

from .vault import EncryptionUnavailable, ObsidianVault, VaultRecord

__all__ = ["EncryptionUnavailable", "ObsidianVault", "VaultRecord"]
