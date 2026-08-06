from typing import Any, Literal

from pydantic import BaseModel

# Run input
Benchmark = Literal["swebench-verified"]


class RunInput(BaseModel):
    benchmark: Benchmark
    llm: str
    run_name: str

    # env resources & limits
    base_image: str = ""
    cpu_count: int = 1
    memory_mb: int = 2048
    command_timeout: int = 100  # In seconds

    # benchmark limits
    max_turns: int = 300
    benchmark_timeout: int = 3600  # In seconds

    # benchmark config
    slice: tuple[int, int] | None = [0, 1]


# Run output
class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0


class Message(BaseModel):
    content: str
    reasoning: str
    usage: Usage
    latency: float | None = None
    role: Literal["assistant", "user"] = "assistant"


class Command(BaseModel):
    command: str
    stdout: str
    exit_code: int | None = None
    extra: dict[str, Any] = {}
    latency: float | None = None


Turn = Message | Command


class RunOutput(BaseModel):
    system_prompt: str
    initial_input: str

    turns: list[Turn] = []

    success: bool | None = None
    total_usage: Usage = Usage()
    total_latency: float | None = None
