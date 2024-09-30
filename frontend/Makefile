GOOGLE_CLOUD_PROJECT=youyaku-ai
GOOGLE_REGION=asia-northeast1
DOCKER_BASE_URL=${GOOGLE_REGION}-docker.pkg.dev
DOCKER_URL=${DOCKER_BASE_URL}/${GOOGLE_CLOUD_PROJECT}/line-sakamomo-family-api/front
SERVICE_NAME=sakamomo-family-web-app
WEB_PORT=8501


setup:
	gcloud auth configure-docker ${DOCKER_BASE_URL}

build:
	docker build -t ${DOCKER_URL}:latest .

push_image:
	docker push ${DOCKER_URL}:latest

local_run:
	streamlit run app/main.py

deploy_run:
	gcloud run deploy ${SERVICE_NAME} \
		--region ${GOOGLE_REGION} \
		--image ${DOCKER_URL} \
		--port ${WEB_PORT} \
		--allow-unauthenticated

all_process:
	make build
	make push_image
	make deploy_run

delete_run:
	gcloud run services delete ${SERVICE_NAME} --region ${GOOGLE_REGION}

lint:
	pysen run lint

format:
	pysen run format
