"""Run and grade SWE-bench with the mini-swe-agent harness on AgentENV microVMs.

The three stages -- generate, grade, parse -- are independently resumable, so re-invoking
`run` with the same `run_name` picks up wherever the previous invocation stopped.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Literal

# Importing minisweagent prints a banner and loads its own global dotenv.
os.environ.setdefault("MSWEA_SILENT_STARTUP", "1")

from dotenv import load_dotenv  # noqa: E402
from minisweagent.models.litellm_model import LitellmModel  # noqa: E402
from minisweagent.run.benchmarks.swebench import (  # noqa: E402
    filter_instances,
    get_swebench_docker_image_name,
    remove_from_preds_file,
    update_preds_file,
)
from minisweagent.run.benchmarks.utils.batch_progress import (  # noqa: E402
    RunBatchProgressManager,
)
from minisweagent.run.benchmarks.utils.common import ProgressTrackingAgent  # noqa: E402
from minisweagent.utils.log import add_file_handler, logger  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from rich.live import Live  # noqa: E402

from src.benchmarks.swebench.environment import AgentEnvEnvironment  # noqa: E402
from src.types import Command, Message, RunInput, RunOutput, Turn, Usage  # noqa: E402

load_dotenv()

RUNS_DIR = Path("data/runs")

DATASET_BY_BENCHMARK: dict[str, tuple[str, str]] = {
    "swebench-verified": ("SWE-bench/SWE-bench_Verified", "test"),
}

"""Exit statuses where the agent ran to a legitimate conclusion rather than crashing."""
CLEAN_EXIT_STATUSES = {
    "Submitted",
    "LimitsExceeded",
    "TimeExceeded",
    "RepeatedFormatError",
}

# Prompts and templates, inlined from minisweagent/config/benchmarks/swebench.yaml.
# They are jinja templates rendered with StrictUndefined, so every variable must exist.
SYSTEM_TEMPLATE = """\
You are a helpful assistant that can interact with a computer shell to solve programming tasks.
"""

INSTANCE_TEMPLATE = """\
<pr_description>
Consider the following PR description:
{{task}}
</pr_description>

<instructions>
# Task Instructions

## Overview

You're a software engineer interacting continuously with a computer by submitting commands.
You'll be helping implement necessary changes to meet requirements in the PR description.
Your task is specifically to make changes to non-test files in the current directory in order to fix the issue described in the PR description in a way that is general and consistent with the codebase.
<IMPORTANT>This is an interactive process where you will think and issue AT LEAST ONE command, see the result, then think and issue your next command(s).</important>

For each response:

1. Include a THOUGHT section explaining your reasoning and what you're trying to accomplish
2. Provide one or more bash tool calls to execute

## Important Boundaries

- MODIFY: Regular source code files in /testbed (this is the working directory for all your subsequent commands)
- DO NOT MODIFY: Tests, configuration files (pyproject.toml, setup.cfg, etc.)

## Recommended Workflow

1. Analyze the codebase by finding and reading relevant files
2. Create a script to reproduce the issue
3. Edit the source code to resolve the issue
4. Verify your fix works by running your script again
5. Test edge cases to ensure your fix is robust

## Command Execution Rules

You are operating in an environment where

1. You issue at least one command
2. The system executes the command(s) in a subshell
3. You see the result(s)
4. You write your next command(s)

Each response should include:

1. **Reasoning text** where you explain your analysis and plan
2. At least one tool call with your command

**CRITICAL REQUIREMENTS:**

- Your response SHOULD include reasoning text explaining what you're doing
- Your response MUST include AT LEAST ONE bash tool call. You can make MULTIPLE tool calls in a single response when the commands are independent (e.g., searching multiple files, reading different parts of the codebase).
- Directory or environment variable changes are not persistent. Every action is executed in a new subshell.
- However, you can prefix any action with `MY_ENV_VAR=MY_VALUE cd /path/to/working/dir && ...` or write/load environment variables from files

Example of a CORRECT response:
<example_response>
I need to understand the Builder-related code. Let me find relevant files and check the project structure.

[Makes multiple bash tool calls: {"command": "ls -la"}, {"command": "find src -name '*.java' | grep -i builder"}, {"command": "cat README.md | head -50"}]
</example_response>

## Environment Details

- You have a full Linux shell environment
- Always use non-interactive flags (-y, -f) for commands
- Avoid interactive tools like vi, nano, or any that require user input
- You can use bash commands or invoke any tool that is available in the environment
- You can also create new tools or scripts to help you with the task
- If a tool isn't available, you can also install it

## Submission

When you've completed your work, you MUST submit your changes as a git patch.
Follow these steps IN ORDER, with SEPARATE commands:

Step 1: Create the patch file
Run `git diff -- path/to/file1 path/to/file2 > patch.txt` listing only the source files you modified.
Do NOT commit your changes.

<IMPORTANT>
The patch must only contain changes to the specific source files you modified to fix the issue.
Do not submit file creations or changes to any of the following files:

- test and reproduction files
- helper scripts, tests, or tools that you created
- installation, build, packaging, configuration, or setup scripts unless they are directly part of the issue you were fixing (you can assume that the environment is already set up for your client)
- binary or compiled files
</IMPORTANT>

Step 2: Verify your patch
Inspect patch.txt to confirm it only contains your intended changes and headers show `--- a/` and `+++ b/` paths.

Step 3: Submit (EXACT command required)
You MUST use this EXACT command to submit:

```bash
echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT && cat patch.txt
```

If the command fails (nonzero exit status), it will not submit.

<CRITICAL>
- Creating/viewing the patch and submitting it MUST be separate commands (not combined with &&).
- If you modify patch.txt after verifying, you SHOULD verify again before submitting.
- You CANNOT continue working (reading, editing, testing) in any way on this task after submitting.
</CRITICAL>
</instructions>
"""

OBSERVATION_TEMPLATE = """\
{% if output.exception_info -%}
<exception>{{output.exception_info}}</exception>
{% endif -%}
<returncode>{{output.returncode}}</returncode>
{% if output.output | length < 10000 -%}
<output>
{{ output.output -}}
</output>
{%- else -%}
<warning>
The output of your last command was too long.
Please try a different command that produces less output.
If you're looking at a file you can try use head, tail or sed to view a smaller number of lines selectively.
If you're using grep or find and it produced too much output, you can use a more selective search pattern.
If you really need to see something from the full command's output, you can redirect output to a file and then search in that file.
</warning>
{%- set elided_chars = output.output | length - 10000 -%}
<output_head>
{{ output.output[:5000] }}
</output_head>
<elided_chars>
{{ elided_chars }} characters elided
</elided_chars>
<output_tail>
{{ output.output[-5000:] }}
</output_tail>
{%- endif -%}
"""

FORMAT_ERROR_TEMPLATE = """\
{% if finish_reason is defined and (finish_reason == "length" or (finish_reason == "tool_calls" and not has_tool_calls)) -%}
Your previous response reached the output token limit (finish_reason={{ finish_reason }}) before you produced a tool call, so it was cut off. Respond more concisely and finish with exactly one bash tool call. If you need to think more, do so briefly.
{%- else -%}
Tool call error:

<error>
{{error}}
</error>

Here is general guidance on how to submit correct toolcalls:

Every response needs to use the 'bash' tool at least once to execute commands.

Call the bash tool with your command as the argument:
- Tool: bash
- Arguments: {"command": "your_command_here"}

If you have completed your assignment, please consult the first message about how to
submit your solution (you will not be able to continue working on this task after that).
{%- endif %}
"""


class SweBenchConfig(BaseModel):
    # data selection
    dataset_path: str = ""
    """Overrides the dataset derived from `RunInput.benchmark`."""
    split: str = ""
    """Overrides the split derived from `RunInput.benchmark`."""
    filter_spec: str = ""
    """Regex matched against instance ids before slicing."""
    shuffle: bool = False
    workers: int = 1

    # prompts
    system_template: str = SYSTEM_TEMPLATE
    instance_template: str = INSTANCE_TEMPLATE
    observation_template: str = OBSERVATION_TEMPLATE
    format_error_template: str = FORMAT_ERROR_TEMPLATE

    # model
    api_base: str = ""
    """Passed to litellm as `api_base`, e.g. the swissai serving endpoint."""
    model_kwargs: dict[str, Any] = {"drop_params": True, "parallel_tool_calls": True}
    cost_limit: float = 0.0
    """0 disables the limit. litellm has no price data for the swissai models."""
    cost_tracking: Literal["default", "ignore_errors"] = "ignore_errors"
    max_consecutive_format_errors: int = 3

    # environment
    cwd: str = "/testbed"
    env_vars: dict[str, str] = {
        "PAGER": "cat",
        "MANPAGER": "cat",
        "LESS": "-R",
        "PIP_PROGRESS_BAR": "off",
        # Non-login shells skip ~/.bashrc, which is where the image runs `conda activate testbed`.
        "BASH_ENV": "/root/.bashrc",
        "TQDM_DISABLE": "1",
    }
    sandbox_timeout: int = 7200

    # grading
    grade: bool = True
    grade_workers: int = 4
    grade_timeout: int = 1800
    namespace: str = "swebench"
    """Docker registry namespace the harness pulls prebuilt eval images from."""

    # resume
    redo_existing: bool = False
    retry_errored: bool = False
    """Also re-run instances whose exit status is not in `CLEAN_EXIT_STATUSES`."""


class TracedAgent(ProgressTrackingAgent):
    """Adds per-call wall time, which mini-swe-agent does not record anywhere.

    Upstream only stamps `time.time()` *after* a call, and every observation in a step shares
    one stamp, so latencies cannot be recovered from a finished trajectory.
    """

    def query(self) -> dict:
        start = time.time()
        message = super().query()
        message.setdefault("extra", {})["latency"] = time.time() - start
        return message

    def execute_actions(self, message: dict) -> list[dict]:
        actions = message.get("extra", {}).get("actions", [])
        outputs, latencies = [], []
        for action in actions:
            start = time.time()
            try:
                outputs.append(self.env.execute(action))
            finally:
                latencies.append(time.time() - start)
        observations = self.model.format_observation_messages(
            message, outputs, self.get_template_vars()
        )
        for observation, latency in zip(observations, latencies):
            observation.setdefault("extra", {})["latency"] = latency
        return self.add_messages(*observations)


def _dataset(run_input: RunInput, config: SweBenchConfig) -> tuple[str, str]:
    dataset_path, split = DATASET_BY_BENCHMARK[run_input.benchmark]
    return config.dataset_path or dataset_path, config.split or split


def _load_instances(run_input: RunInput, config: SweBenchConfig) -> list[dict]:
    from datasets import load_dataset

    dataset_path, split = _dataset(run_input, config)
    logger.info(f"Loading dataset {dataset_path}, split {split}...")
    instances = list(load_dataset(dataset_path, split=split))
    instances = filter_instances(
        instances, filter_spec=config.filter_spec, shuffle=config.shuffle
    )
    if run_input.slice is not None:
        start, end = run_input.slice
        instances = instances[start:end]
    return instances


def _is_done(traj_path: Path, retry_errored: bool) -> bool:
    if not traj_path.exists():
        return False
    try:
        info = json.loads(traj_path.read_text()).get("info", {})
    except (json.JSONDecodeError, OSError):
        return False
    exit_status = info.get("exit_status") or ""
    if not exit_status:
        return False
    return exit_status in CLEAN_EXIT_STATUSES if retry_errored else True


def _traj_path(raw_dir: Path, instance_id: str) -> Path:
    return raw_dir / instance_id / f"{instance_id}.traj.json"


def _build_model(run_input: RunInput, config: SweBenchConfig) -> LitellmModel:
    model_kwargs = dict(config.model_kwargs)
    if config.api_base:
        model_kwargs["api_base"] = config.api_base
    return LitellmModel(
        model_name=run_input.llm,
        model_kwargs=model_kwargs,
        observation_template=config.observation_template,
        format_error_template=config.format_error_template,
        cost_tracking=config.cost_tracking,
    )


def _build_environment(
    instance: dict, run_input: RunInput, config: SweBenchConfig
) -> AgentEnvEnvironment:
    return AgentEnvEnvironment(
        image=run_input.base_image or get_swebench_docker_image_name(instance),
        cwd=config.cwd,
        env=config.env_vars,
        timeout=run_input.command_timeout,
        sandbox_timeout=config.sandbox_timeout,
        cpu_count=run_input.cpu_count,
        memory_mb=run_input.memory_mb,
    )


def _process_instance(
    instance: dict,
    run_input: RunInput,
    config: SweBenchConfig,
    raw_dir: Path,
    progress_manager: RunBatchProgressManager,
) -> None:
    instance_id = instance["instance_id"]
    traj_path = _traj_path(raw_dir, instance_id)

    # Avoid an inconsistent state if this attempt dies halfway through.
    remove_from_preds_file(raw_dir / "preds.json", instance_id)
    traj_path.unlink(missing_ok=True)

    model = _build_model(run_input, config)
    agent, env = None, None
    exit_status, result, extra_info = None, None, {}

    progress_manager.on_instance_start(instance_id)
    progress_manager.update_instance_status(instance_id, "Starting sandbox")

    try:
        env = _build_environment(instance, run_input, config)
        agent = TracedAgent(
            model,
            env,
            progress_manager=progress_manager,
            instance_id=instance_id,
            system_template=config.system_template,
            instance_template=config.instance_template,
            step_limit=run_input.max_turns,
            cost_limit=config.cost_limit,
            wall_time_limit_seconds=run_input.benchmark_timeout,
            max_consecutive_format_errors=config.max_consecutive_format_errors,
            output_path=traj_path,
        )
        info = agent.run(instance["problem_statement"])
        exit_status, result = info.get("exit_status"), info.get("submission")
    except Exception as e:
        logger.error(f"Error processing instance {instance_id}: {e}", exc_info=True)
        exit_status, result = type(e).__name__, ""
        extra_info = {"traceback": traceback.format_exc(), "exception_str": str(e)}
    finally:
        if env is not None:
            # Upstream leans on __del__, which leaks sandboxes whenever an exception keeps
            # the agent alive.
            env.cleanup()
        if agent is not None:
            agent.save(
                traj_path,
                {
                    "info": {
                        "exit_status": exit_status,
                        "submission": result,
                        **extra_info,
                    },
                    "instance_id": instance_id,
                },
            )
        update_preds_file(
            raw_dir / "preds.json", instance_id, model.config.model_name, result or ""
        )
        progress_manager.on_instance_end(instance_id, exit_status)


def _generate(
    instances: list[dict], run_input: RunInput, config: SweBenchConfig, raw_dir: Path
) -> None:
    pending = [
        instance
        for instance in instances
        if config.redo_existing
        or not _is_done(
            _traj_path(raw_dir, instance["instance_id"]), config.retry_errored
        )
    ]
    logger.info(f"Running {len(pending)}/{len(instances)} instances...")
    if not pending:
        return

    progress_manager = RunBatchProgressManager(
        len(pending), raw_dir / f"exit_statuses_{time.time()}.yaml"
    )

    def process_futures(futures: dict[concurrent.futures.Future, str]):
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except concurrent.futures.CancelledError:
                pass
            except Exception as e:
                instance_id = futures[future]
                logger.error(
                    f"Error in future for instance {instance_id}: {e}", exc_info=True
                )
                progress_manager.on_uncaught_exception(instance_id, e)

    with Live(progress_manager.render_group, refresh_per_second=4):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=config.workers
        ) as executor:
            futures = {
                executor.submit(
                    _process_instance,
                    instance,
                    run_input,
                    config,
                    raw_dir,
                    progress_manager,
                ): instance["instance_id"]
                for instance in pending
            }
            try:
                process_futures(futures)
            except KeyboardInterrupt:
                logger.info(
                    "Cancelling all pending jobs. Press ^C again to exit immediately."
                )
                for future in futures:
                    if not future.running() and not future.done():
                        future.cancel()
                process_futures(futures)


def _grade(run_input: RunInput, config: SweBenchConfig, run_dir: Path) -> None:
    preds_path = run_dir / "raw" / "preds.json"
    if not preds_path.exists():
        logger.warning("No predictions to grade.")
        return

    predictions = json.loads(preds_path.read_text())
    grading_dir = run_dir / "grading"
    report_path = grading_dir / "report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    ungraded = sorted(set(predictions) - set(report))
    if not ungraded:
        logger.info("All generations are already graded.")
        return

    dataset_path, split = _dataset(run_input, config)
    run_id = f"{run_input.run_name}-{int(time.time())}"
    logger.info(f"Grading {len(ungraded)} generations (run_id={run_id})...")

    # The harness resolves both --report_dir and its logs/ tree relative to the cwd.
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "swebench.harness.run_evaluation",
            "--dataset_name", dataset_path,
            "--split", split,
            "--predictions_path", str(preds_path.resolve()),
            "--run_id", run_id,
            "--max_workers", str(config.grade_workers),
            "--timeout", str(config.grade_timeout),
            "--namespace", config.namespace,
            "--instance_ids", *ungraded,
        ],
        cwd=grading_dir,
        check=False,
    )
    if completed.returncode != 0:
        logger.error(
            f"swebench harness exited with {completed.returncode}; "
            "recording only the instances it did report on."
        )

    for instance_id in ungraded:
        prediction = predictions[instance_id]
        model_name = (prediction.get("model_name_or_path") or "").replace("/", "__")
        instance_report = (
            grading_dir
            / "logs"
            / "run_evaluation"
            / run_id
            / model_name
            / instance_id
            / "report.json"
        )
        if instance_report.exists():
            try:
                report[instance_id] = json.loads(instance_report.read_text())[
                    instance_id
                ]
                continue
            except (json.JSONDecodeError, KeyError, OSError):
                pass
        if completed.returncode == 0:
            # A clean harness run that produced no report means an empty or unusable patch.
            reason = (
                "empty patch"
                if not prediction.get("model_patch")
                else "no report produced"
            )
            report[instance_id] = {"resolved": False, "error": reason}

    report_path.write_text(json.dumps(report, indent=2))


def _text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        )
    return str(content)


def _message_usage(message: dict) -> Usage:
    response = (message.get("extra") or {}).get("response")
    usage = (response or {}).get("usage") if isinstance(response, dict) else None
    usage = usage or {}
    details = usage.get("completion_tokens_details") or {}
    return Usage(
        prompt_tokens=usage.get("prompt_tokens") or 0,
        completion_tokens=usage.get("completion_tokens") or 0,
        reasoning_tokens=details.get("reasoning_tokens") or 0,
    )


def _command_text(actions: list[dict], tool_call_id: str | None, index: int) -> str:
    if tool_call_id:
        for action in actions:
            if action.get("tool_call_id") == tool_call_id:
                return action.get("command", "")
    if index < len(actions):
        return actions[index].get("command", "")
    return ""


def _parse_trajectory(trajectory: dict, resolved: bool | None) -> RunOutput:
    messages = trajectory.get("messages") or []
    turns: list[Turn] = []
    total_usage = Usage()
    total_latency = 0.0
    actions: list[dict] = []
    observation_index = 0

    for message in messages[2:]:
        role = message.get("role")
        if role == "exit":
            break

        extra = message.get("extra") or {}
        latency = extra.get("latency")
        if latency is not None:
            total_latency += latency

        if role == "assistant":
            usage = _message_usage(message)
            total_usage = Usage(
                prompt_tokens=total_usage.prompt_tokens + usage.prompt_tokens,
                completion_tokens=total_usage.completion_tokens
                + usage.completion_tokens,
                reasoning_tokens=total_usage.reasoning_tokens + usage.reasoning_tokens,
            )
            actions = extra.get("actions") or []
            observation_index = 0
            turns.append(
                Message(
                    content=_text(message.get("content")),
                    reasoning=_text(message.get("reasoning_content")),
                    usage=usage,
                    latency=latency,
                    role="assistant",
                )
            )
        elif "raw_output" in extra:
            turns.append(
                Command(
                    command=_command_text(
                        actions, message.get("tool_call_id"), observation_index
                    ),
                    stdout=extra["raw_output"],
                    exit_code=extra.get("returncode"),
                    extra={
                        key: value
                        for key, value in extra.items()
                        if key not in {"raw_output", "returncode", "latency"}
                    },
                    latency=latency,
                )
            )
            observation_index += 1
        else:
            # Format-error or interruption feedback injected by the harness.
            turns.append(
                Message(
                    content=_text(message.get("content")),
                    reasoning="",
                    usage=Usage(),
                    latency=latency,
                    role="user",
                )
            )

    return RunOutput(
        system_prompt=_text(messages[0].get("content")) if messages else "",
        initial_input=_text(messages[1].get("content")) if len(messages) > 1 else "",
        turns=turns,
        success=resolved,
        total_usage=total_usage,
        total_latency=total_latency or None,
    )


def _parse(run_dir: Path) -> None:
    report_path = run_dir / "grading" / "report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    traces = {}
    for traj_path in sorted((run_dir / "raw").glob("*/*.traj.json")):
        try:
            trajectory = json.loads(traj_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Skipping unreadable trajectory {traj_path}: {e}")
            continue
        instance_id = trajectory.get("instance_id") or traj_path.parent.name
        graded = report.get(instance_id)
        traces[instance_id] = _parse_trajectory(
            trajectory, graded.get("resolved") if graded else None
        ).model_dump()

    (run_dir / "traces.json").write_text(json.dumps(traces, indent=2))
    logger.info(f"Parsed {len(traces)} trajectories into {run_dir / 'traces.json'}")


def run(run_input: RunInput, config: SweBenchConfig) -> None:
    """Generate the missing instances of the slice, grade what is ungraded, then parse."""
    if run_input.benchmark not in DATASET_BY_BENCHMARK:
        raise ValueError(f"Unsupported benchmark: {run_input.benchmark}")

    run_dir = RUNS_DIR / run_input.run_name
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "grading").mkdir(exist_ok=True)
    (run_dir / "run_config.json").write_text(
        json.dumps(
            {"run_input": run_input.model_dump(), "config": config.model_dump()},
            indent=2,
        )
    )
    add_file_handler(raw_dir / "minisweagent.log")

    _generate(_load_instances(run_input, config), run_input, config, raw_dir)
    if config.grade:
        _grade(run_input, config, run_dir)
    _parse(run_dir)
    logger.info(f"Results saved to {run_dir}")


def _slice(value: str) -> tuple[int, int] | None:
    if value.lower() in {"", "none", "all"}:
        return None
    start, _, end = value.partition(":")
    return int(start or 0), int(end)


def main() -> None:
    run_default = {
        name: field.default for name, field in RunInput.model_fields.items()
    }
    default = SweBenchConfig()

    parser = argparse.ArgumentParser(
        prog="python -m src.benchmarks.swebench.run_swebench",
        description=run.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add = parser.add_argument

    add("-n", "--run-name", required=True)
    add("-m", "--llm", required=True, help="litellm model name")
    add("--benchmark", default="swebench-verified", choices=list(DATASET_BY_BENCHMARK))
    add("--slice", type=_slice, default=run_default["slice"],
        help="'start:end', or 'none' for all")
    add("--base-image", default=run_default["base_image"],
        help="overrides the per-instance swebench image")
    add("--cpu-count", type=int, default=run_default["cpu_count"])
    add("--memory-mb", type=int, default=run_default["memory_mb"])
    add("--command-timeout", type=int, default=run_default["command_timeout"])
    add("--max-turns", type=int, default=run_default["max_turns"])
    add("--benchmark-timeout", type=int, default=run_default["benchmark_timeout"])

    add("--dataset-path", default=default.dataset_path)
    add("--split", default=default.split)
    add("--filter", dest="filter_spec", default=default.filter_spec)
    add("--shuffle", action="store_true")
    add("-w", "--workers", type=int, default=default.workers)
    add("--api-base", default=default.api_base)
    add("--cost-limit", type=float, default=default.cost_limit)
    add("--cost-tracking", default=default.cost_tracking,
        choices=["default", "ignore_errors"])
    add("--max-consecutive-format-errors", type=int,
        default=default.max_consecutive_format_errors)
    add("--cwd", default=default.cwd)
    add("--sandbox-timeout", type=int, default=default.sandbox_timeout)
    add("--no-grade", dest="grade", action="store_false")
    add("--grade-workers", type=int, default=default.grade_workers)
    add("--grade-timeout", type=int, default=default.grade_timeout)
    add("--namespace", default=default.namespace)
    add("--redo-existing", action="store_true")
    add("--retry-errored", action="store_true")

    args = parser.parse_args()
    run_input = RunInput(
        **{
            key: value
            for key, value in vars(args).items()
            if key in RunInput.model_fields
        }
    )
    config = SweBenchConfig(
        **{
            key: value
            for key, value in vars(args).items()
            if key in SweBenchConfig.model_fields
        }
    )
    run(run_input, config)


if __name__ == "__main__":
    main()
