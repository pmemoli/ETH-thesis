# Pre-Start Notes

This is my note-taking space for the runway before formally starting on July 29th on ETH Zurich.

## July 9th

Reading:

[4] TRAIL: Trace Reasoning and Agentic Issue Localization

### TRAIL

TRAIL presents a taxonomy of agentic errors and a benchmark of 148 traces annotated by humans according to the taxonomy. They find LLMs pretty poor at annotating traces for monitoring.

Traces were produced by running claude 3.7 sonnet on GAIA and SWE-Bench-Lite, and organically introduce errors by "instruction constraints and force exploration via prompts".

Most interestingly one taxonomy level is "System Execution Errors" which comes in 3 sublevels:

- Configuration Issues:
    - Incorrect Tool Definition
    - Environment Setup Errors

- API And System Issues:
    - Rate Limits
    - Auth Errors
    - Service Errors
    - Resource Not Found

- Resource management:
    - Resource Exhaustion
    - Timeout issues

We can absolutely use this taxonomy to guide our studies and understanding model behaviour in each case (RQ3).

But we can't use this to answer RQ1 since the traces force errors. I want some actual model traces in online use...

Looking into actual traces I found BurstGPT which provides 10 million traces from a regional Azure OpenAI GPT service. This LOGS ERORRS!! So it's a cute analysis to start working on RQ1 (understanding infra noise/error sources and their distribution)!!

Also found 2 papers on other source of infra noise which is transient hardware faults:

- Resilience Assessment of Large Language Models under Transient Hardware Faults
- Analysis of LLM Vulnerability to GPU Soft Errors: An Instruction-Level Fault Injection Study 

Basically:

Observable:

- API errors, Resource management and timeouts.

I can measure these by looking at traces. I can also inject these and study their behaviour

- Config issues and environment setup errors.

These I can cite as relevant, I can also study their behaviour, but injecting them is not trivial.

Unobservable:

- Transient hardware faults and floating point non-determinism from system configuration.

These I can cite as relevant.

Next step is to read BurstGPT and look into the traces.

## July 8th

Long day today, so I'm just stating the research questions I want to answer through literature review.

- RQ1: What are the infra noise sources in agentic systems.

The anthropic blog post, [3] and tangentially [2] are relevant here. From those papers, we find that External API errors/limits, floating point precision and resource limitations are the main sources. There may be others!

TRAIL here is super relevant. It provides a taxonomy of errors and annotated traces which I can analize right now.

- RQ2: Can we quantify the infra noise impact on agentic systems?

This consists in basically building the evaluation harness... The anthropic blog post looks like the only relevant one.

- RQ3: When agentic systems fail due external errors, how do they react?

Tools Fail: Detecting Silent Errors in Faulty Tools
Hell or High Water: Evaluating Agentic Recovery from External Failures
AgentNoiseBench: Benchmarking Robustness of Tool-Using LLM Agents Under Noisy Condition
"Failing Tools: Benchmarking LLM Agent Recovery Under Runtime Tool Failures" 

- RQ4: What are some recovery policies for external errors:

CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing
PALADIN: Self-Correcting Language Model Agents to Cure Tool-Failure Cases
SHIELDA: Structured Handling of Exceptions in LLM-Driven Agentic Workflows
Reflexion: Language Agents with Verbal Reinforcement Learning

Our provisional goal for the thesis is:

1. Understanding infra noise sources, and how agents react to them.
2. Creating a benchmark to quantify model behaviour under infra noise by injecting disturbances.
3. Understanding current recovery policies and potentially proposing others.

## July 7th

Today I'm reading:

- [3] Yuan et al. Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference. NeurIPS 2025.

## Mitigating Numerical Sources of Nondeterminism in LLM Inference [3]

Fascinating paper about how different system configurations for LLM inference (Batch size, GPU count, GPU architecture, etc.) introduces variance even in greedy decoding settings. They mainly attribute this to floating point non-associativity due to the effect being noticable particularily with FP16 and BP16, whereas FP32 presents much lower variance. Variance is also considerable for pass@1 in non-greedy settings for different system configurations.

They focus on traditional benchmarks (non agentic), but the principle very much still applies to agentic benchmarks.

### What are we getting from this

The paper basically introduces a third source of infra noise orthogonal to allocated resources and external API rate limits. Unlike the other two sources, I don't think there are any recovery policies for it... 

From the 3 papers we have the following infra noise sources:

- **API limits & availability**
- **Resource ceilings**
- **System configuration non-determinism**

I want to see some actual traces for the sources of errors in agentic systems (or just LLMS equiped with tools)... Thinking of these 2 research questions:

RQ4: When agentic systems fail, what is the source of errors?
RQ5: When LLMs face API limits, lack of availability or limited resource (in the non-preempted case, opposite to anthropic), how do they react?

Claude found these papers (also relevant to the original RQs)

RQ4: 
- TRAIL: Trace Reasoning and Agentic Issue Localization

RQ5:
- Tools Fail: Detecting Silent Errors in Faulty Tools
- Hell or High Water: Evaluating Agentic Recovery from External Failures
- AgentNoiseBench: Benchmarking Robustness of Tool-Using LLM Agents Under Noisy Condition
- "Failing Tools: Benchmarking LLM Agent Recovery Under Runtime Tool Failures" 

For recovery from tool errors (RQ1 and RQ3):
- CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing
- PALADIN: Self-Correcting Language Model Agents to Cure Tool-Failure Cases
- SHIELDA: Structured Handling of Exceptions in LLM-Driven Agentic Workflows
- Reflexion: Language Agents with Verbal Reinforcement Learning

There is also this one which relates to system design errors, rather than infra errors, but it is still relevant:
- MAST: "Why Do Multi-Agent LLM Systems Fail?"

I think its super super relevant to read these over the next few days, and summarize the state of the art and current research regarding:

1. Error distribution in agentic systems
2. Effects & non-determinism of Infra noise on agentic systems
3. Recovery policies when possible (also on agentic systems)

It feels like 2. is the most unexplored one. After that I can more clearly plan the thesis RQs and objectives.

## July 6th

Today I'm reading in depth:

- [1] Zhu et al. Establishing Best Practices for Building Rigorous Agentic Benchmarks. NeurIPS 2025 Datasets and Benchmarks Track.
- [2] https://www.anthropic.com/engineering/infrastructure-noise

### Best practices paper [1]

This paper proposes an Agentic Benchmark Checklist for rigorous evaluation and design of Agentic Benchmarks. As opposed with traditional multiple choice (e.g. MMLU) and language modeling benchmarks, agentic benchmarks can be quite complex to set up. These consist of the following:

**The task setup**

- Task description (just a markdown prompt)
- An environment (containerized)
- Tools (api calls, wolfram alpha, whatever)

**The outcome evaluation**

- evaluating the task E2E and finally comparing in the result in some way (LLM as a judge, string/substring matching, etc.).

They notice 2 recurrent issues on many benchmarks:

- **task validity**: The model is perfectly capable of solving the task but the benchmark fails (or viceversa), such as through rate limits or accessing ground truth labels. 

- **outcome validity**: It is not the case that the evaluation returns true IFF it is actually true. The outcomes can be evaluated as true or false when thats not the case, such as with faulty or incomplete unit testing.

And then propose a checklist to tackle these two issues (and another one relating to presenting the results) and evaluate the checklist over 17 benchmarks + experiment with applying changes based on it.

#### What are we getting from this

The authors present 17 agentic benchmarks chosen by popularity. It really makes sense to work with some of these at the start, maybe 2 or 3.

| Benchmark | Evaluated Capability | Evaluation Design |
|---|---|---|
| SWE-bench | Software Engineering | Unit Testing |
| SWE-Lancer | Software Engineering | End-to-end Testing |
| KernelBench | Software Engineering | Fuzz Testing |
| BIRD | Software Engineering | End-to-end Testing |
| Aider-Edit | Software Engineering | Unit Testing |
| Codeforces | Software Engineering | Unit Testing |
| LiveBench Coding | Software Engineering | Unit Testing |
| Aider-Polyglot | Software Engineering | Unit Testing |
| FrontierMath | Challenging Math Problem-solving | Answer Match |
| MLE-bench | ML Engineering | Quality Measure |
| RE-bench | ML Engineering | Quality Measure |
| τ-bench | Environment Interaction | Substring Matching, State Matching |
| WebArena | Environment Interaction | Whole String Matching, Substring Matching, LLM-as-a-Judge, State Matching |
| OSWorld | Environment Interaction | State Matching |
| WebVoyager | Environment Interaction | LLM-as-a-Judge |
| Cybench | Cybersecurity | Answer Matching |
| GAIA | General Assistant | Answer Matching |

It is also clear that our task relating to studying Agent robustness to disturbances relates to benchmark **task validity**, we don't really care about outcome. Some points of the ABC seem pretty relevant:

##### Checklist for tools

Tools come in two flavors:

- Self-Hosted tools like Python and CLI tools
- API-based tools

ABC for tools are:

1. Versions of self hosted tools are specified
2. Required API tools are consistently accessible (we can inject errors here through **rate limits** or just making it unavailable)
3. Evaluation terminates or handles errors appropiately (in our harness, we may not want to terminate it and rather see how it handles it)

I also notice that self hosted tools can also fail, through say resource contention.

##### Checklist for the environment

ABC for the env is:

1. Residual data can become stale between runs (we can inject this, not quite sure how though) 
    e.g. Relies on an sqlite or something that is not cleared between runs

2. Agent can't access ground truth information (maybe we can inject this and see how "honest" it is? feels too complex)

3. Setup is frozen and does not change over time (we can inject this, not quite sure how though)
    e.g. The benchmark checks for HTML selectors (like class names or page titles) on live web pages, or maybe it relies on a live database in constant change.

#### Possible failure points for task validity

We don't really want to eliminate these, but rather introduce them as a controlled variable. From the checklist I see 4 failure points:

1. Rate limits & inaccesibility on API tools (easy to implement and general)
2. Inaccesibility for CLI tools (resource contention, lack of access requirements)
3. Stale environment data
4. Drifting environment setup

1. and 2. seem recoverable, whereas 3. and 4. relate to task setup that doesn't seem recoverable...

### Anthropic Infra Noise paper [2]

This one is extremely relevant to what we are doing. They found that the runtime environment is very important for agentic benchmarks, and configurations of the environment can shift benchmark % accuracy by more than the difference between top models. 

They faced a lot of infra errors on their run of TerminalBench 2.0 related to exceeding the allocated resources for the agentic environmnet. They found that increasing the resource ceiling (originally ceiling = allocation) greatly **reduced the infra errors** (as expected) and **increased benchmark accuracy**. For 1x-3x ceiling, benchmark scores fluctate between margins of noise (p<0.4) but beyond that the scores increase and become significant (uncapped p < 0.01).  

More resources help agents solve problems they weren't able to before by exploring more aggressive resource-intensive solutions. So in a way the resource ceiling also affects *what is being measured*. Low resources measure efficent solution capabilities whereas high resource measure absolute benchmark capacity in an unrealistic scenario.  

They primarily measure the infra impact by increasing the resource ceiling of environments (which ends up reducing error rates from 6% to 0.5% when going x1 to x6 the original resources), but there are other sources of variance such as time/rate limits from APIs.

#### What are we getting from this

This is very interesting since it provides one very clear tunable parameter (the resource ceiling) which seems to account for a lot of the infraestructure errors.

From the previous paper, another very clear tunable parameter is API errors for the tools. I'm thinking of API rate and time limits, and simple unavailability for unkown reasons. That way I'm covering infra errors self hosted tools, and also API tools. 

What is not so clear to me is what metrics are we getting from this, pass rate is clearly one (for self hosted tools its not hitting the ceiling and for apis its not hitting the time limit) and effect on benchmark accuracy is another. But what about the whole recovery deal?... 

Tomorrow i'm reading the other paper from the proposal, looking at other relevant ones and summarizing my thoughts...

## Goals (written on the 1st day)

The ultimate goal of the thesis is exploring these 3 research questions:

RQ1. Can a model recover from injected infrastructure disturbances, and at what cost (extra steps, tokens, latency, budget)?

RQ2. Up to what noise intensity does recovery remain feasible before performance collapses, and how does that threshold scale with model size and scaffolding?

RQ3. Where recovery fails, especially for small models, can a lightweight mitigation layer close the gap, and by how much?

And building an evaluation harness with tunable disturbers that inject representative infrastructure faults at controlled rates on top of existing agentic tasks. Maybe if time allows (most likely) also build some simple mitigation layer, or maybe even fine tuning the model to make it robust to tool failure.

Right now the priority is **reading the literature**, and becoming familiar with the **tech stack** over which I'm injecting noise. Curious mainly on emulating whatever claude code does for virtualizing its environment. I also want to get a better idea on the concrete infraestructure noise we'd inject.
