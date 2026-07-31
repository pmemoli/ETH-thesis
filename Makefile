include .env
export

mut-create:
	mutagen sync create -m two-way-safe --ignore=.venv --ignore=.git \
		--name=eth-${USER} \
		. ${USER}@sgs-gpu05.ethz.ch:/pub/scratch/${USER}

mut-resume:
	mutagen sync resume eth-${USER}

mut-kill:
	mutagen sync terminate eth-${USER}

mut-list:
	mutagen sync list

ssh:
	ssh ${USER}@${DOMAIN_NAME}

run:


.PHONY: mut-sync
