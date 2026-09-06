# BASELINE_SINGLE_MODEL_NO_VEGO — frozen prompt template

Perform the same structured UML-review objective as the VEGO-AI condition for
one supplied AirTravel case. Return the declared output schema only: a parsed
case assessment, a completion state, and evidence references. Do not delegate
to other agents, ask inter-agent questions, maintain a VEGO-AI Q&A registry,
run a feedback loop, or emit Detector-v1 input. The case identifier and source
bytes are supplied by the controlled runner; this template contains no case
content and no reference model.
