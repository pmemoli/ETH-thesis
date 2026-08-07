# Journal

The journal contains what I did and thought for each day. Markdowns that accompany tools and papers are found in `notes/learning/`.

## August 7, 2026

Last day of the week! Checked to make sure the curl is available on the microVMs, and agentENV sets it up by default, epic. 

The goal for today is to run swe-bench-verified on the mini-swe-agent harness using harbor, and maybe build (as in, vibecode) some streamlit UI to just look at the traces. I must also think of next steps for next week and what to say in the presentation.

What I want to do right now and for the next week is to quantify how much variance can be attributed to the environment rather than general LLM non-determinism, and what are the *observable* variance sources from our fixed-budget traces. To isolate this, I'm thinking of running 30 samples of swe-bench-verified on some harness 10 times each for 2 LLMs (a big and small one, so 600 runs) with temperature 0, so that way the variability is attributable to the environment (i mean, mostly, non-associativity from floating point operations inevitably makes generation non-deterministic). 

Looking at the [swe-bench](https://www.swebench.com/verified.html) docs, they specify that the version 2.x.x leaderboards don't set any temperature (do they use model defaults?), and there is no mention anywhere of multiple runs, so there is no CI control over the variability from BOTH the LLM and the environment. Terminal-bench official leaderboards also uses the model defaults, but at least they run each (harness, benchmark, model) triplet >= 5 times. In either case, variance from the environment is not controlled for.

For a smoke test, I ran swe-bench-verified on 2 samples 10 times on the mini-swe-agent harness using harbor and agentENV, on [Apertus](https://arxiv.org/pdf/2509.14233) 8B and 70B (job is specified at `src/harbor_jobs/env_variability_smoke_test.yaml`). I didn't set any timeouts or max-turns for simplicity.

### Summary of the work done on the week

- Connected to the CloudLab infra and wrote some scripts to sync the local directory with mutagen, alles gut.

- Read on firecracker, the KVM, hypervisors and how the VMs are interfaced with an API through a port. Also found out they can be easily interacted with, since AgentENV provides an E2B-compatible API which has a bunch of sdks.

- Read the swe-bench, swe-agent and the terminal-bench papers (among others, but they aren't relevant) to get a proper feel for what harnesses are used in the leaderboards, what these are, and how they are ran. Noticed quite a lot of issues with the way the leaderboards are presented. There are just a few runs per sample, which makes it really hard to say which model is best. 

- Spent like 2 days forking and modifying mini-swe-agent to use our AgentENV vms through a custom Environment adapter. I ran one sample but it was very buggy and realized it wasn't worth the effort. Found by reading the terminal-bench paper that there is a framework specifically made for this (harbor), that can be set up with a custom E2B environment for tool execution, rather than docker which is what most frameworks use.

- Ran a 10 sample smoke test to ensure stuff is working correctly.

So I basically read a minimal subset of literature, found some issues, connected to the infra, and ran a smoke test on Apertus 8B. 

### For the next week

1. Analyze traces left generating over the weekend. The goal is to understand the variability attributable to the environment in a specific configuration, and **if existing**, to track down the sources of **observable** variability and generate a taxonomy. I'll probably make a UI with streamlit to look at the traces.

2. Pick a **single** probe based on the results, and inject noise, exploring how metrics (pass rate, token consumption, turns, etc.) increase/decrease.

Based on that I will have a good justification and motivation on the presence of environment noise (1.), and why its worthwhile to study it (2.).

I'm most interested rn in tackling **RQ1: What are the infra noise sources in agentic systems**, by reading literature and doing a larger scale experiment. There is a lot of literature relating to the problem of agentic tools failing. A really cool paper I found before arriving is TRAIL, which provides traces for agentic runs and a taxonomy of errors. I'd be curious on reading it and properly looking at the traces, with the main objective of defining a taxonomy of errors that I can then:

1. study how they distribute in a larger experiment.
2. inject different noise sources.

## August 6, 2026

I was able to run a sample of swe-bench-verified on the mini-swe-agent harness using the cloudlab infra, the swissai serving api and the agentENV microVMs, only issue is that its taking SO much time and the traces don't have the infromation I mostly care about. Wiring everything up with minisweagent is also being such a pain, we are basically rewriting 2/3 of the codebase which mostly works with yaml configs. It will also be a pain to run other benchmarks, configurations and harnesses this way...

Right now I JUST want to analyze a bunch of traces from swebench runs on our infra... The environment can easily be integrated through e2b and the serving api is OpenAI-compatible. Looking at the [original anthropic post](https://www.anthropic.com/engineering/infrastructure-noise) which inspired the thesis proposal, they evaluate on [terminal bench 2.0](https://arxiv.org/pdf/2601.11868) which comes with a [harbor framework](https://www.harborframework.com/) to evaluate agents in sandboxed environments, and we can wire everything up without issue. Read the terminal bench paper and the harbor docs, and it seems like a much better approach than hacking mini-swe-agent. I will try to wire up harbor with agentENV and the serving api, and run swe-bench-verified on it (hopefully by tomorrow I have some traces). Kinda lost 1 1/2 days forking mini-swe-agent, pity, but i guess I learned a lot.

Tomorrow I'm running a bunch of traces on harbor and our infra, it should be super easy. The difficulty will be injecting stuff but on a reverse proxy I should be able to cook something.

 Already setup the makefile target to run swe-bench and ran a sample with it, alles gut. I ran it with Apertus 70B and it was really fast, all thats left now is to run many samples and analyze the variability and traces. To reduce the variance from the model outputs, maybe I can fix a seed... 

 Also, I used the terminus-2 harness (very similar to swe-agent-mini) and noticed it runs tools. The papers I've read are previous to the massive incorporation and post training of tool use in LLMs, so I think I'll read the key tool related papers while the benchmark runs. 

## August 5, 2026

Decided on using [swe-agent-mini](https://github.com/swe-agent/mini-swe-agent) as the swe-bench harness since that is realistic, and Xiao already saw some variance running some samples with it. I do worry a bit that it is not representative of the variance in proper harnesses like claude-code, since it doesn't have websearch capabilities unless the agent chooses to use curl. 

It's not priority at all but I'm also kinda curious on formalizing the agents and the variance sources with Markov Decision Processes, I found [this book](https://www.amazon.com/dp/1489974903) about it which I will absolutely read in the following months.

My goal for today is setting up the harness and running at least some [swe-bench-verified](https://openai.com/index/introducing-swe-bench-verified/) samples within it. The verified version filters underspecified PRs, those that introduce unit tests that filter valid solutions and others with severe issues. They end up with 500 samples.

For this I first need to:

1. Understand how to interface with the AgentENV MicroVMs
2. Understand mini-swe-agent

### 1)

The key thing with AgentENV is that it exposes an E2B compatible API through a port, so I just have to start the server and use an E2B sdk to abstract the booting of VMs. The sdk also lets me specify the env (virtual) resources.

### 2)

mini-swe-agent is a very simple harness to interact with LLMs, while providing scripts to run swe-bench on it. It is organized into three modules, each corresponding to a prototype class that can be hacked to whatever: "agents", "environment" and "models". 

The agent is the proper harness, which I will leave untouched. What I do need to change is the environment class, which needs to connect to agentENV microVMs through the e2b sdk, and the model class which should use the [swissai serving api](https://serving.swissai.svc.cscs.ch). I'll probably have to tweak these two similar modules on other harnesses as well.

## August 4, 2026

Created the cloudlab profile in `profile.py` with [this documentation](https://docs.cloudlab.us/geni-lib.html). I just let the node be whatever is available, and set the image to Ubuntu 24, same as Xiao's `agent-env-baseline` profile. Hardware types are documented [here](https://docs.cloudlab.us/hardware.html), I may need them eventually since they should be an upper bound for agent-env resources. 

Succesfully setup the environment and created the make commands to sync the local-remote folders with mutagen, and to download the runs with rsync. Tested it and everything is working smoothly. I was also able to download agent-env and run a CLI on a microVM on the node.

Before wiring agentenv with swe-bench and running everything, I want to:

1. Understand what harness is most widely used for running [swe-bench](https://arxiv.org/pdf/2310.06770), since what the paper proposes is definitely legacy and not used.
2. Understand how microVMs are interfaced with.

(written August 5, but this was done on August 4) Read the [swe-agent](https://arxiv.org/abs/2405.15793) paper (early 2024), which was written by the same authors as swe-bench. The paper introduces one of the first non-trivial harnesses for LM-agents. I also skimmed [ReAct](https://arxiv.org/abs/2210.03629) (2023) which in a way motivates the harness, but its a very simple idea (reason before acting betters performance) so I don't think there is much value in it. 

Nevertheless, as models became better, the abstracted interface which distinguished the original swe-agent harness became useless, so the authors just recommend using [swe-agent-mini](https://github.com/swe-agent/mini-swe-agent) which has the model iterate a simple reason-actwithshell-readoutput loop. 

## August 3, 2026

Read on [Firecracker](https://www.usenix.org/system/files/nsdi20-paper-agache.pdf), and [OS level virtualization](https://en.wikipedia.org/wiki/OS-level_virtualization). I don't think is worthwhile to get into the implementation details. I've also begun reading on test-time scaling, but it is not a priority right now.  

The TODO as discussed in the weekly meeting is setting up a minimal working environment for running agentic benchmarks:

1. Run swe-bench verified on the sandbox, fixing one sandbox setting and a small model.
2. Look at traces by running it multiple times and find the source of the differences. Document passrate, avg. token use and avg. turns.
3. Propose a minimal taxonomy for the difference sources.
4. Introduce a single probe and look at how the expected metrics change.

I may do something different for 4. based on what I find.

We'll use CloudLAB to run the environment since we need KVM access, and swissai serving api to run the models, at least temporarily. I'm not sure if we'll be able to inject certain types of noise with it, such as resource budget constraints. 

Too jet lagged to finish setting up the CloudLab environment, so I finished the day by reading on [swe-bench](https://arxiv.org/pdf/2310.06770). The benchmark is (originally) basically a bunch of merged PRs (2294) that installs succesfully and contains new previously failing tests that solve after the merge. They use an extremly simple harness which includes relevant files with bm25, or just pass them with an oracle based on modified files. There is also no mention of tool use of any form. Results in the paper are super bad, but this is mostly attributable to the 2023 models they evaluate and the retrieval-based context.

I should look into the verified version, and see what harness it uses in 2026. Found [this paper](https://arxiv.org/pdf/2405.15793) which introduces the v1 harness... I want to look more documentation. 

## July 31, 2026

Today I'm formally starting my master thesis. Pre-start notes are found in `notes/pre_start.md`. 

The main goal right now is connecting to ETH's computers, creating scripts to sync easily and setting up a minimal agent environment. As discussed with Cedric and Xiao, this environment will be Kimi 3's [Agent ENV](https://github.com/kvcache-ai/AgentENV). In parallel, I would like to read on the technical aspects of Firecracker's VMs, and Kimi 3.

I succesfully connected to the destination ${USER}@${DOMAIN_NAME} and synced it with mutagen to my local machine.

I've also read upon hypervisors and the KVM through:

- [Hypervisor](https://en.wikipedia.org/wiki/Hypervisor)
- [KVM](https://northflank.com/blog/what-is-kvm)

And a bunch of other resources. Super interesting.

On monday I'm going to finish reading on Firecracker and KVM. After that I want to setup a Firecracker instance and then some 4B model running its context on Agent ENV.
