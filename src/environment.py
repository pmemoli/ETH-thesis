import platform
from typing import Any

from minisweagent.utils.serialize import recursive_merge
from pydantic import BaseModel
from e2b import Sandbox, Template


class EnvironmentConfig(BaseModel):
    """Base configuration for the environment."""

    env_name: str = "default_env"
    image: str = "ubuntu:24.04"
    cpu_count: int = 1
    memory_mb: int = 512
    timeout: int = 60
    envs: dict = {}
    cwd: str = ""


def generate_template(config: EnvironmentConfig) -> str:
    """Generate a template based on the provided configuration. Returns the e2b template name."""

    if Template.exists(config.env_name):
        return config.env_name

    template = Template().from_image(config.image)
    Template.build(
        template,
        config.env_name,
        cpu_count=config.cpu_count,
        memory_mb=config.memory_mb,
    )

    return config.env_name


def create_sandbox(config: EnvironmentConfig) -> Sandbox:
    """Create a sandbox environment based on the provided configuration."""

    template_name = generate_template(config)
    sandbox = Sandbox.create(template_name)

    return sandbox


class MiniSWEAgentEnv:
    """Subclasses the Environment class to provide a specific environment for MiniSWEAgent."""

    def __init__(self, config: EnvironmentConfig):
        self.config = config
        self.sandbox = create_sandbox(config)

    def execute(
        self, action: dict, cwd: str = "", timeout: int = None
    ) -> dict:
        """Execute a command in the sandbox environment."""
        command = action.get("command", "")
        if not command:
            raise ValueError("No command provided in action.")

        try:
            result = self.sandbox.commands.run(
                command,
                cwd=cwd or self.config.cwd,
                timeout=timeout or self.config.timeout,
            )
            output = {
                "output": result.stdout,
                "returncode": result.exit_code,
                "exception_info": "",
                "extra": "Run successfully",
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

        return output

    def get_template_vars(self, **kwargs) -> dict[str, Any]:
        return recursive_merge(
            self.config.model_dump(),
            platform.uname()._asdict(),
            self.config.envs,
            kwargs,
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
