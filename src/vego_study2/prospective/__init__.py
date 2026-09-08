"""Study 2 prospective paired VEGO_AI_ON versus VEGO_AI_OFF execution harness.

This package is the only provider-capable Study 2 path.  It is separate from
:mod:`vego_study2.runner`, which stays fixture-only by construction.  Every
module here is additive; none modifies the protected VEGO-AI runtime, the
frozen Detector-v1 rule, or any historical AirTravel evidence.
"""
