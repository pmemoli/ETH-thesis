## Introduction

For most of its development, scaling meant increasing the model parameters [kaplan paper](https://arxiv.org/pdf/2001.08361), which was empirically the main performance driver. Nowadays test-time/inference-time scaling has become a second axis of scaling with the rise of reasoning models, which scales up the RL post-training (train-time compute), thereby making more efficent use of increased compute during inference (test-time compute) by having models think and use tools before answering. Some examples:

- [o-series from gpt](https://openai.com/index/learning-to-reason-with-llms/) scales reasoning and achieves SOTA perf (when it deployed)
- [kimi-k1.5](https://arxiv.org/abs/2501.12599) shows that scaling RL can elicit sophisticated reasoning from strong pre-trained models 
- [kimi-k2.5 agent swarm]() extends scaling by having multiple subagents.

... (I'm continuing reading this after setting up the environment which is the priority)
