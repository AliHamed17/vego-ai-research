"""Evidence-bounded multi-dataset Study 1 preparation utilities.

This package deliberately contains no provider client, model invocation, or
scientific-result generator. It prepares dataset admission, leakage-safe case
projection, and offline engineering checks only.
"""

from .admission import AdmissionError, build_qure_data_card, build_vego_se_archive_card

__all__ = [
    "AdmissionError",
    "build_qure_data_card",
    "build_vego_se_archive_card",
]
