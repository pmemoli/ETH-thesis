#!/bin/bash

# installs uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# installs agentenv and starts server
curl -fsSL https://raw.githubusercontent.com/kvcache-ai/AgentENV/main/scripts/install.sh | sudo bash
sudo systemctl start aenv

# creates thesis folders (the rest is synced with mutagen)
mkdir $HOME/thesis
mkdir $HOME/thesis/data/runs
