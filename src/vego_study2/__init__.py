"""Evidence-bounded Study 2 ON/OFF comparison tooling.

The package contains only offline, dependency-injected execution support.  A
provider implementation is intentionally not included; callers must supply a
local deterministic fixture client for preflight work.
"""

from .runner import Study2RunError, Study2Runner, validate_case_output

__all__ = ["Study2Runner", "Study2RunError", "config", "fixtures", "paths", "runner", "validate_case_output"]
