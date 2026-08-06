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

# run swebench (needs uv tool install --force 'harbor[e2b]')
DATASET ?= swebench-verified@1.0
AGENT ?= terminus-2
MODEL ?= swiss-ai/Apertus-v1.5-70B
API_BASE ?= https://api.swissai.svc.cscs.ch/v1
N_TASKS ?= 1
N_CONCURRENT ?= 1
N_ATTEMPTS ?= 1
RUN_NAME ?= $(shell date +%Y%m%d-%H%M%S)

run-swebench:
	OPENAI_API_KEY=${SWISSAI_API_KEY} \
	harbor run \
		--dataset $(DATASET) \
		--agent $(AGENT) \
		--model openai/$(MODEL) \
		--ak api_base=$(API_BASE) \
		--env e2b \
		--n-tasks $(N_TASKS) \
		--n-concurrent $(N_CONCURRENT) \
		--n-attempts $(N_ATTEMPTS) \
		--jobs-dir data/runs \
		--job-name $(RUN_NAME) \
		--yes

.PHONY: mut-create mut-resume mut-kill mut-list download-data harbor-install run-swebench

