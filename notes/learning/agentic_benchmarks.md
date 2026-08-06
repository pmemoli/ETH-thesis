## SWE Agent (original paper)

The paper is from the same people as SWE-bench.

They introduce the SWE-Agent harness, which is a system composed of an instruct-LM and an ACI (agent-computer interface) for the LLM to interact with its environment. They base their prompting strategy from REACT (reason, act and incorporate env feedback).

The agent harness consists of a bunch of software tools and the following prompts:

- System prompt (tool definitions and problem explanation).
- A full correct example.
- Concrete problem.

And after each LLM response, the corresponding tool is run to completion, and the env response is submitted.

## SWE Agent Mini

This is a 100-line simple agent harness based on the philosophy of [mini-agent](https://minimal-agent.com/). It consists of a simple loop of prompt -> reason + action -> exec action -> pass output -> ...(repeat) -> reason + terminate. It doesn't include tool calls, the action is just parsed from the response. It just needs 3 primitives:

- query_lm
- parse_action
- execute_action

mini-swe-agent just modularizes this and provides reasonable defaults. The loop is run by the Agent class, the query_lm is abstracted through the Model class, and execute_action by the Environment class:

```bash
minisweagent/__init__  # Protocols/interfaces for all base classes
minisweagent/agents  # Agent control flow & loop
minisweagent/environments  # Executing agent actions
minisweagent/models  # LM interfaces
minisweagent/run  # Run scripts that serve as an entry point
minisweagent/config  # Config files for each of the three modules
```

## Terminal-Bench 2.0

Terminal-Bench is a framework to evaluate agents on realistic tasks in command line interfaces. Terminal Bench 2.0 is a concrete set of 89 tasks, where each consists of a:

1. containerized environment 
2. an instruction of the task
3. a set of tests
4. a reference solution
5. a time limit

They run everything with the harbor "harness" which supports many agentic benchmarks ran on different agents (claude code, mini-swe-agent, etc). Note that what they name "agent" we just name "agent-harness", but whatever. This is just what we need, noise can be injected directly through a reverse proxy or something.

They evaluate each (agent, benchmark) pair at least 5 runs (that is actually very little to estimate variance).

Besides that, there is an error taxonomy for commands which looks kinda useful (?.
