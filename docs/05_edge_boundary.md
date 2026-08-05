# Edge-deployment claim boundary

## What is known

- **[PROJECT DECISION]** Jetson Nano is the intended edge device; training/fine-tuning belongs on a server with an RTX 3060.
- **FACT — cited.** A paper can demonstrate embodied tracking without being an edge baseline. For example, TrackVLA is an embodied tracking research system [R5](../references/references.md#r5), but its reported system configuration must not be converted into a Jetson Nano claim.

## What is not known

- No selected tracker has been reproduced on the target Nano.
- No target-device latency, stable FPS, RAM use, thermal behaviour, power, camera-to-output timing, or accuracy loss after export has been measured.
- No required minimum FPS/latency/power threshold has been tied to a finalized robot action and safety envelope.

## The only acceptable route to a Nano-feasibility claim

**PROVISIONAL MEASUREMENT GATE** — all items must be reported on the actual target device and frozen software/configuration:

1. Reproduce a checkpoint on the RTX 3060 and verify valid tracker outputs.
2. Run the same tracker on Jetson Nano using a declared input resolution, precision, runtime, batch size, warm-up, and video replay.
3. Report tracker-only latency and full camera-to-output latency separately, including p50/p95/p99 and stable throughput.
4. Record peak RAM, thermal/throttling observations, and power only when the meter/rail source supports that claim.
5. Compare the exported engine with the desktop/reference model on the same appropriate tracking protocol.

Until this gate is complete, write only **“candidate for Nano profiling”**, never “runs in real time on Jetson Nano.”
