#!/usr/bin/env bash
# Build + push image to ECR, register task, run one Fargate task, wait, pull output.
set -euo pipefail

ACCOUNT_ID="${AWS_ACCOUNT_ID:?set AWS_ACCOUNT_ID}"
REGION="${AWS_REGION:-us-east-1}"
ECR_REPO="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/hackerrank-agent"
TAG="${TAG:-latest}"
CLUSTER="${CLUSTER:-hackerrank-agent}"
CONTAINER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${CONTAINER_DIR}/../.." && pwd)"

BUCKET="${S3_BUCKET:?set S3_BUCKET (bucket already holding recipe+input)}"
RECIPE_KEY="${RECIPE_KEY:-recipes/text-classification-bedrock.yaml}"
INPUT_KEY="${INPUT_KEY:-input/sample_tickets.csv}"
OUT_KEY="${OUT_KEY:-output/decisions_$(date +%s).csv}"
TRACE_KEY="${TRACE_KEY:-output/trace_$(date +%s).jsonl}"
MODEL_ID="${BEDROCK_MODEL_ID:-anthropic.claude-3-haiku-20240307-v1:0}"

echo ">>> building image"
docker build -t "hackerrank-agent:${TAG}" -f "${CONTAINER_DIR}/Dockerfile" "${ROOT}"

echo ">>> ECR login + push"
aws ecr get-login-password --region "${REGION}" \
  | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com" >/dev/null
docker tag "hackerrank-agent:${TAG}" "${ECR_REPO}:${TAG}"
docker push "${ECR_REPO}:${TAG}"

echo ">>> rendering task definition"
sed -e "s|ACCOUNT_ID|${ACCOUNT_ID}|g" \
    -e "s|REGION|${REGION}|g" \
    -e "s|s3://YOUR_BUCKET/recipes/text-classification-bedrock.yaml|s3://${BUCKET}/${RECIPE_KEY}|g" \
    -e "s|s3://YOUR_BUCKET/input/sample_tickets.csv|s3://${BUCKET}/${INPUT_KEY}|g" \
    -e "s|s3://YOUR_BUCKET/output/decisions_.csv|s3://${BUCKET}/${OUT_KEY}|g" \
    -e "s|s3://YOUR_BUCKET/trace/trace.jsonl|s3://${BUCKET}/${TRACE_KEY}|g" \
    "${CONTAINER_DIR}/task-definition.json" > "${CONTAINER_DIR}/task-rendered.json"

echo ">>> registering task definition"
TASK_ARN="$(
  aws ecs register-task-definition --region "${REGION}" \
    --cli-input-json "file://${CONTAINER_DIR}/task-rendered.json" \
    --query "taskDefinition.taskDefinitionArn" --output text
)"
echo ">>> task def: ${TASK_ARN}"

echo ">>> cluster on-demand"
aws ecs create-cluster --cluster-name "${CLUSTER}" --region "${REGION}" >/dev/null 2>&1 || true

echo ">>> running Fargate task"
RUN_ID="$(
  aws ecs run-task --region "${REGION}" --cluster "${CLUSTER}" --task-definition "${TASK_ARN}" \
    --launch-type FARGATE \
    --network-configuration '{"awsvpcConfiguration":{"subnets":["SUBNET_ID"],"assignPublicIp":"ENABLED"}}' \
    --query "tasks[0].taskArn" --output text
)"
echo ">>> task: ${RUN_ID}"

echo ">>> polling task status"
while :; do
  STATUS="$(aws ecs describe-tasks --region "${REGION}" --cluster "${CLUSTER}" --tasks "${RUN_ID}" --query 'tasks[0].lastStatus' --output text)"
  echo "    status=${STATUS}"
  case "${STATUS}" in
    STOPPED|STOPPING) break ;;
    RUNNING) ;;
    *) sleep 10 ;;
  esac
done

EXIT_CODE="$(aws ecs describe-tasks --region "${REGION}" --cluster "${CLUSTER}" --tasks "${RUN_ID}" --query 'tasks[0].containers[0].exitCode' --output text)"
echo ">>> exit code: ${EXIT_CODE}"
if [ "${EXIT_CODE}" != "0" ]; then
  echo ">>> task failed; streaming logs (CloudWatch group /ecs/hackerrank-agent)"
  aws logs tail /ecs/hackerrank-agent --since 5m --region "${REGION}" || true
  exit 1
fi

echo ">>> fetching output + trace"
aws s3 cp "s3://${BUCKET}/${OUT_KEY}" ./"$(basename "${OUT_KEY}")" --region "${REGION}"
aws s3 cp "s3://${BUCKET}/${TRACE_KEY}" ./"$(basename "${TRACE_KEY}")" --region "${REGION}"
echo ">>> done. outputs: $(basename "${OUT_KEY}"), $(basename "${TRACE_KEY}")"
