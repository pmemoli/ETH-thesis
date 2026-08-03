# Journal

## July 31, 2026

Today I'm formally starting my master thesis. Pre-start notes are found in `notes/pre_start.md`. 

The main goal right now is connecting to ETH's computers, creating scripts to sync easily and setting up a minimal agent environment. As discussed with Cedric and Xiao, this environment will be Kimi 3's [Agent ENV](https://github.com/kvcache-ai/AgentENV). In parallel, I would like to read on the technical aspects of Firecracker's VMs, and Kimi 3.

I succesfully connected to the destination ${USER}@${DOMAIN_NAME} and synced it with mutagen to my local machine.

I've also read upon hypervisors and the KVM through:

- [Hypervisor](https://en.wikipedia.org/wiki/Hypervisor)
- [KVM](https://northflank.com/blog/what-is-kvm)

And a bunch of other resources. Super interesting.

On monday I'm going to finish reading on Firecracker and KVM. After that I want to setup a Firecracker instance and then some 4B model running its context on Agent ENV.

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

