# AirTravel duplicate and stripped-file adjudication

The inventory contains 143 files: 110 generated-result candidates, 27
filename-marked stripped/derived records, two reference-model records, one
domain description, one metadata file, and two visualization-only files.
Eleven generated records are zero bytes and are inadmissible. Records whose
filename contains `_stripped` are retained for provenance but excluded from
the candidate subset because the upstream naming declares them derived views,
not independent generations.

Exact byte-duplicate groups observed by SHA-256 include:

- `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`: eleven zero-byte result records (`result_cot2_*` plus `result_cot_*`, `result_few_*`, `result_one_*`, and `result_*` Falcon/DeepSeek variants).
- `01098956641fc205d3db6efee4cd262e41f7b4542ba1c9bce2afbf11215168df`: `result_deepseek-ai_DeepSeek-R1-Distill-Qwen-7B.txt` and its stripped variant.
- `70845f1be7069e62dc51eecb3987aa0bb590bd7107f49bbff84119dfd686af54`: the few-shot DeepSeek result and stripped variant.
- `78323ed153a038160495ca8fd9c20dc340d30cc865dae0d89f1cc089c75b856c`: the few-shot Qwen 2.5 result and stripped variant.
- `6bf49af1ccdd5bc7379117c2a5be01a64644151fb89f28656abfab9f1cf379e2`: the few-shot Qwen 3.5 result and stripped variant.
- `786fa79f56dea0e3af5d0c4df0c18838fe88f20615a155949b7c04faec3ffea5`: the one-shot DeepSeek result and stripped variant.
- `2a7de3f3aad9ce230d0bda92f3660e8f403ef2c79447ff80262b5ab052865093`: the one-shot Qwen 2.5 result and stripped variant.
- `83f4f2c7d481a13b2fe3c805531213199e0245e7b86a41ab959eeac98e69a57f`: the one-shot Qwen 3.5 result and stripped variant.
- `5e73998ff02a52b17a04ea0fec699abadb1afce9b90f6f2cae28105b4d0c4d01`: the zero-shot Qwen 2.5 result and stripped variant.
- `5cdfb200358c1932db66b61c5c77b63f2f8b3edc311e7143bf341fe90a8ff437`: the zero-shot Qwen 3.5 result and stripped variant.

The four proposed one-shot files in `candidate-subset-proposal.md` have
distinct nonempty hashes and no stripped relationship. They remain
`PROPOSED_NOT_FROZEN`; Claude must approve the exact selection before any
execution.
