GOOGLE_REGION=asia-northeast1
DOCKER_BASE_URL=${GOOGLE_REGION}-docker.pkg.dev
DOCKER_URL=${DOCKER_BASE_URL}/${GOOGLE_CLOUD_PROJECT}/line-sakamomo-family-api/edinet_job
JOB_NAME=sakamomo-family-job
DURATION_DAYS=10
CPU=4
MEMORY=8
MAX_RETRY_COUNT=0
TASK_TIMEOUT=3600
DELETE_FLAG=1
JOB_SCHEDULE="0 12 * * *"
JOB_HEADERS="DURATION_DAYS=${DURATION_DAYS},DELETE_FLAG=${DELETE_FLAG}"

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
		--max-retries ${MAX_RETRY_COUNT} \
		--task-timeout ${TASK_TIMEOUT} \
		--set-env-vars EDINET_API_KEY=${EDINET_API_KEY} \
		--set-env-vars TABLE_ID=${TABLE_ID}

run_job:
	gcloud run jobs execute ${JOB_NAME} --wait \
		--region ${GOOGLE_REGION} \
		--update-env-vars DURATION_DAYS=${DURATION_DAYS} \
		--update-env-vars DELETE_FLAG=${DELETE_FLAG}

delete_job:
	gcloud run jobs delete ${JOB_NAME} \
		--region ${GOOGLE_REGION}

register_job_scheduler:
	gcloud scheduler jobs create http ${JOB_NAME} \
		--location ${GOOGLE_REGION} \
		--schedule=${JOB_SCHEDULE} \
		--uri="https://${GOOGLE_REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${GOOGLE_CLOUD_PROJECT}/jobs/${JOB_NAME}:run" \
		--http-method POST \
		--time-zone=Asia/Tokyo \
		--headers=${JOB_HEADERS} \
		--oauth-service-account-email=${JOB_SERVICE_ACCOUNT}

delete_job_scheduler:
	gcloud scheduler jobs delete ${JOB_NAME} --location=${GOOGLE_REGION}
