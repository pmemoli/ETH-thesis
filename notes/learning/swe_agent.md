## SWE Agent (original paper)

The paper is from the same people as SWE-bench.

They introduce the SWE-Agent harness, which is a system composed of an instruct-LM and an ACI (agent-computer interface) for the LLM to interact with its environment. They base their prompting strategy from REACT (reason, act and incorporate env feedback).

The agent harness consists of a bunch of software tools and the following prompts:

- System prompt (tool definitions and problem explanation).
- A full correct example.
- Concrete problem.

And after each LLM response, the corresponding tool is run to completion.

## SWE Agent Mini

This is a 100-line simple agent harness
