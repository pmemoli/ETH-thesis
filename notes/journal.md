# Journal

The journal contains what I did and thought for each day. Markdowns that accompany tools and papers are found in `notes/learning/`.

## August 6, 2026

I was able to run a sample of swe-bench-verified on the mini-swe-agent harness using the cloudlab infra, the swissai serving api and the agentENV microVMs, only issue is that its taking SO much time and the traces don't have the infromation I mostly care about. Wiring everything up with minisweagent is also being such a pain, we are basically rewriting 2/3 of the codebase which mostly works with yaml configs. It will also be a pain to run other benchmarks, configurations and harnesses this way...

Right now I JUST want to analyze a bunch of traces from swebench runs on our infra... The environment can easily be integrated through e2b and the serving api is OpenAI-compatible. Looking at the [original anthropic post](https://www.anthropic.com/engineering/infrastructure-noise) which inspired the thesis proposal, they evaluate on [terminal bench 2.0](https://arxiv.org/pdf/2601.11868) which comes with a [harbor framework](https://www.harborframework.com/) to evaluate agents in sandboxed environments, and we can wire everything up without issue. Read the terminal bench paper and the harbor docs, and it seems like a much better approach than hacking mini-swe-agent. I will try to wire up harbor with agentENV and the serving api, and run swe-bench-verified on it (hopefully by tomorrow I have some traces). Kinda lost 1 1/2 days forking mini-swe-agent, pity, but i guess I learned a lot.

Tomorrow I'm running a bunch of traces on harbor and our infra, it should be super easy. The difficulty will be injecting stuff but on a reverse proxy I should be able to cook something.

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
