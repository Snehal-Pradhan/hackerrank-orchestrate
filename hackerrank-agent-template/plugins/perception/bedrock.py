from __future__ import annotations

import json
import os
from typing import Any, Dict

from core.contracts import ExecutionContext
from core.plugin import Plugin


class BedrockPerception(Plugin):
    category = "perception"
    name = "perception.bedrock"
    version = "0.1.0"
    abstract = False
    provides = ["perception.lang"]
    requires = []
    config_schema = {"model_id": str, "region": str, "max_tokens": int, "text_fields": "list"}

    def setup(self) -> None:
        try:
            import boto3  # noqa: PLC0415
        except ImportError as exc:
            raise RuntimeError("boto3 not installed; run: pip install 'hackerrank-agent-template[aws]'") from exc
        self._model_id = self.config.get("model_id") or os.environ.get("AWS_BEDROCK_MODEL_ID", "")
        if not self._model_id:
            raise RuntimeError("perception.bedrock requires model_id or AWS_BEDROCK_MODEL_ID")
        region = self.config.get("region") or os.environ.get("AWS_REGION") or "us-east-1"
        self._client = boto3.client("bedrock-runtime", region_name=region)

    def process(self, ctx: ExecutionContext) -> ExecutionContext:
        fields = ctx.normalized.fields or ctx.item.fields
        text_fields = self.config.get("text_fields", [])
        keys = text_fields or list(fields)
        text = " ".join(str(fields[k]) for k in keys if fields.get(k))
        prompt = (
            "Classify the message. Return JSON only: "
            '{"intents": ["..."], "urgency": "low|medium|high", "sentiment": "negative|neutral|positive"}. '
            f"Message: {text}"
        )
        body = self._build_body(prompt)
        response = self._client.invoke_model(modelId=self._model_id, body=json.dumps(body))
        payload = json.loads(response["body"].read())
        content = self._extract_content(payload)
        ctx.perception.provider = "bedrock"
        ctx.perception.raw["model"] = self._model_id
        ctx.perception.structured = content if isinstance(content, dict) else {"text": content}
        return ctx

    def _build_body(self, prompt: str) -> Dict[str, Any]:
        max_tokens = self.config.get("max_tokens", 256)
        if "claude" in self._model_id:
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
        return {"inputText": prompt, "textGenerationConfig": {"maxTokenCount": max_tokens}}

    def _extract_content(self, payload: Dict[str, Any]) -> Any:
        if "content" in payload and isinstance(payload["content"], list):
            return payload["content"][0].get("text", "")
        return payload.get("results", [{}])[0].get("outputText", payload.get("outputText", payload))