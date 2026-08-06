include .env
export

# mutagen commands
mut-create:
	mutagen sync create -m one-way-safe --ignore=.venv --ignore=.git --ignore=./data \
		--name=eth-thesis \
		. ${SSH_URL}:/users/pmemoli/thesis/

mut-resume:
	mutagen sync resume eth-thesis

mut-kill:
	mutagen sync terminate eth-thesis

mut-list:
	mutagen sync list

# load data from runs
download-data:
	rsync -avz --ignore-existing ${SSH_URL}:/users/pmemoli/thesis/data/runs/ ./data/runs/

# run swebench on the minisweagent agent (only one available right now)
RUN_NAME ?= default
CONFIG ?= src/config/swebench.yaml
MODEL ?= openai/swiss-ai/Apertus-v1.5-8B-thinking
MAX_TURNS ?= 250
MEMORY_MB ?= 4096
SUBSET ?= verified
SPLIT ?= test
SLICE ?= 0:5
WORKERS ?= 1
GRADE ?= --grade

run-swebench:
	OPENAI_API_KEY=${SWISSAI_API_KEY} uv run python -m src.run \
		-n ${RUN_NAME} -f ${CONFIG} ${GRADE} \
		--set model_name=${MODEL} \
		--set max_turns=${MAX_TURNS} \
		--set env_config.memory_mb=${MEMORY_MB} \
		--set options.subset=${SUBSET} \
		--set options.split=${SPLIT} \
		--set options.slice_spec=${SLICE} \
		--set options.workers=${WORKERS}

.PHONY: mut-create mut-resume mut-kill mut-list download-data run-swebench

