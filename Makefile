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

run:


.PHONY: mut-create mut-resume mut-kill mut-list run
