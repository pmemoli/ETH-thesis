#!/bin/bash

# installs uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# installs harbor
uv tool install harbor['e2b']

# installs agentenv and starts server
curl -fsSL https://raw.githubusercontent.com/kvcache-ai/AgentENV/main/scripts/install.sh | sudo bash
sudo systemctl start aenv

# installs docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$(id -un)"
sudo systemctl enable --now docker

# creates thesis folders (the rest is synced with mutagen)
mkdir -p $HOME/thesis/data/runs
