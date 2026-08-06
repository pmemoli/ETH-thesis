"""AgentENV-backed environment for mini-swe-agent, reached through its E2B-compatible API.

Mirrors the contract of `minisweagent.environments.docker.DockerEnvironment`.
"""

import hashlib
import logging
import os
import platform
import re
import threading
from typing import Any

from e2b import CommandExitException, Sandbox, Template
from minisweagent.exceptions import Submitted
from minisweagent.utils.serialize import recursive_merge
from pydantic import BaseModel

_TEMPLATE_LOCKS: dict[str, threading.Lock] = {}
_TEMPLATE_LOCKS_GUARD = threading.Lock()


def _template_lock(name: str) -> threading.Lock:
    """One lock per template name, so distinct images still build concurrently."""
    with _TEMPLATE_LOCKS_GUARD:
        return _TEMPLATE_LOCKS.setdefault(name, threading.Lock())


class EnvironmentConfig(BaseModel):
    image: str
    template_name: str = ""

    """Derived from the image when empty."""
    cwd: str = "/"
    env: dict[str, str] = {}
    forward_env: list[str] = []

    """Forwarded from the host if set. `env` takes precedence."""
    timeout: int = 60
    sandbox_timeout: int = 7200

    """Sandbox TTL. The e2b default of 300s is far too short for a full episode."""
    cpu_count: int = 2
    memory_mb: int = 4096


def template_name_from_image(image: str) -> str:
    """Derive a deterministic, alias-safe template name from a docker image name."""
    name = re.sub(r"[^a-z0-9]+", "-", image.rsplit("/", 1)[-1].lower()).strip(
        "-"
    )
    if len(name) > 48:
        name = f"{name[:48].rstrip('-')}-{hashlib.sha1(image.encode()).hexdigest()[:8]}"
    return name


def generate_template(config: EnvironmentConfig) -> str:
    """Build the AgentENV template for the configured image. Returns its name."""
    name = config.template_name or template_name_from_image(config.image)
    with _template_lock(name):
        if not Template.exists(name):
            Template.build(
                Template().from_image(config.image),
                name,
                cpu_count=config.cpu_count,
                memory_mb=config.memory_mb,
            )
    return name


class AgentEnvEnvironment:
    def __init__(
        self,
        *,
        config_class: type = EnvironmentConfig,
        logger: logging.Logger | None = None,
        **kwargs,
    ):
        """See `EnvironmentConfig` for keyword arguments."""
        self.logger = logger or logging.getLogger("minisweagent.environment")
        self.sandbox: Sandbox | None = None
        self.config = config_class(**kwargs)
        template_name = generate_template(self.config)
        self.sandbox = Sandbox.create(
            template_name, timeout=self.config.sandbox_timeout
        )
        self.logger.info(
            f"Started sandbox {self.sandbox.sandbox_id} from template {template_name}"
        )

    def _envs(self) -> dict[str, str]:
        envs = {
            key: value
            for key in self.config.forward_env
            if (value := os.getenv(key)) is not None
        }
        return envs | self.config.env

    def execute(
        self, action: dict, cwd: str = "", *, timeout: int | None = None
    ) -> dict[str, Any]:
        """Execute a command in the sandbox and return the result as a dict."""
        command = action.get("command", "")
        assert self.sandbox is not None, "Sandbox not started"

        try:
            result = self.sandbox.commands.run(
                command,
                envs=self._envs(),
                cwd=cwd or self.config.cwd,
                timeout=timeout or self.config.timeout,
            )
            output = {
                "output": result.stdout + result.stderr,
                "returncode": result.exit_code,
                "exception_info": "",
            }
        except CommandExitException as e:
            # e2b raises on any non-zero exit code, but still carries the real output.
            output = {
                "output": e.stdout + e.stderr,
                "returncode": e.exit_code,
                "exception_info": "",
            }
        except Exception as e:
            output = {
                "output": "",
                "returncode": -1,
                "exception_info": f"An error occurred while executing the command: {e}",
                "extra": {
                    "exception_type": type(e).__name__,
                    "exception": str(e),
                },
            }
        self._check_finished(output)
        return output

    def _check_finished(self, output: dict):
        """Raises Submitted if the output indicates task completion."""
        lines = output.get("output", "").lstrip().splitlines(keepends=True)
        if (
            lines
            and lines[0].strip() == "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"
            and output["returncode"] == 0
        ):
            submission = "".join(lines[1:])
            raise Submitted(
                {
                    "role": "exit",
                    "content": submission,
                    "extra": {
                        "exit_status": "Submitted",
                        "submission": submission,
                    },
                }
            )

    def get_template_vars(self, **kwargs) -> dict[str, Any]:
        return recursive_merge(
            self.config.model_dump(), platform.uname()._asdict(), kwargs
        )

    def serialize(self) -> dict:
        return {
            "info": {
                "config": {
                    "environment": self.config.model_dump(mode="json"),
                    "environment_type": f"{self.__class__.__module__}.{self.__class__.__name__}",
                }
            }
        }

    def cleanup(self):
        """Kill the sandbox."""
        sandbox = getattr(self, "sandbox", None)
        if sandbox is None:
            return
        self.sandbox = None
        sandbox_id = getattr(sandbox, "sandbox_id", "<unknown>")
        try:
            sandbox.kill()
        except Exception as e:
            try:
                self.logger.warning(
                    f"Failed to kill sandbox {sandbox_id}: {e}"
                )
            except Exception:
                pass

    def __del__(self):
        self.cleanup()
