# Master Thesis Proposal

Agentic benchmarks run inside live infrastructure: containerized sandboxes, code executors, and tool back-ends whose transient failures (timeouts, rate limits, resource contention, nondeterministic returns) are orthogonal to model capability yet are folded into the reported score [1]. This problem goes deeper than the environment they are run in, since intrinsic non-associativity of floating point operations can vary performance by up to 9% [2], and hardware faults are ever-present [3, 4]. This is the LLM-era analogue of flaky tests in software engineering, where outcomes alternate between pass and fail with no change to the artifact under test [5]. 

Rather than treating the noise as something to eliminate [2, 3], this thesis aims to understand how different LLMs react to it and quantify it by injecting noise, and potentially implement novel mitigation policies.

## Research Questions

- RQ1: What are the infra noise sources in agentic systems.
- RQ2: When agentic systems fail due external errors, how do they react?
- RQ3: Can we quantify the infra noise impact on agentic systems?
- RQ4: What are some recovery policies for external errors?

## Objectives

Our provisional goal for the thesis is:

1. Understanding infra noise sources, and how agents react to them (RQ1, RQ2).
2. Creating a benchmark to quantify model behaviour under infra noise by injecting disturbances (RQ3).
3. Understanding current recovery policies and potentially proposing others (RQ4).

## Tech Stack

TODO.

## References

- [1] Zhu et al. Establishing Best Practices for Building Rigorous Agentic Benchmarks. NeurIPS 2025 Datasets and Benchmarks Track.

- [2] Yuan et al. Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference. NeurIPS 2025.

- [3] Resilience Assessment of Large Language Models under Transient Hardware Faults

- [4] Analysis of LLM Vulnerability to GPU Soft Errors: An Instruction-Level Fault Injection Study 

- [5] Luo, Hariri, Eloussi, Marinov. An Empirical Analysis of Flaky Tests. FSE 2014.
