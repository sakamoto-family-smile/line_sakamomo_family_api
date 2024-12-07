include .env
setup:
	pip install pysen
	pip install black==21.10b0 flake8==4.0.1 isort==5.10.1 mypy==0.910
	pip uninstall click -y
	pip install click==8.0.4
	pip install types-requests

export_infra:
	config-connector bulk-export \
		--project ${GOOGLE_CLOUD_PROJECT} \
		--output output/ \
		--on-error continue \
		-v
