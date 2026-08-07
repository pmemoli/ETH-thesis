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

make harbor-install:
	pip install --force 'harbor[e2b]'

# harbor jobs
JOB ?= src/harbor_jobs/env_variability_smoke_test.yaml

harbor-run:
	OPENAI_API_KEY=${SWISSAI_API_KEY} \
	harbor run \
		--config $(JOB) \
		--yes

.PHONY: mut-create mut-resume mut-kill mut-list download-data harbor-install harbor-run

