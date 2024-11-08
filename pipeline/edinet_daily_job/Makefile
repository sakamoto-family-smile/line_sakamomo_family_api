GOOGLE_CLOUD_PROJECT=youyaku-ai
GOOGLE_REGION=asia-northeast1
DOCKER_BASE_URL=${GOOGLE_REGION}-docker.pkg.dev
DOCKER_URL=${DOCKER_BASE_URL}/${GOOGLE_CLOUD_PROJECT}/line-sakamomo-family-api/edinet_job
JOB_NAME=sakamomo-family-job
DURATION_DAYS=365
CPU=2
MEMORY=4

include .env

setup:
	gcloud auth configure-docker ${DOCKER_BASE_URL}

build:
	docker build -t ${DOCKER_URL}:latest .

push_image:
	docker push ${DOCKER_URL}:latest

deploy_job:
	gcloud run jobs create ${JOB_NAME} \
		--image ${DOCKER_URL} \
		--region ${GOOGLE_REGION} \
		--cpu ${CPU} \
		--memory ${MEMORY}G \
		--set-env-vars EDINET_API_KEY=${EDINET_API_KEY} \
		--set-env-vars TABLE_ID=${TABLE_ID}

run_job:
	gcloud run jobs execute ${JOB_NAME} --wait \
		--region ${GOOGLE_REGION} \
		--update-env-vars DURATION_DAYS=${DURATION_DAYS}

delete_job:
	gcloud run jobs delete ${JOB_NAME} \
		--region ${GOOGLE_REGION}
