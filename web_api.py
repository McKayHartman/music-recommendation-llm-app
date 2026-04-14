import os
from typing import Any

import env
from flask import Flask, jsonify, request
from flask_cors import CORS
from langchain.messages import HumanMessage, SystemMessage
from langchain_litellm import ChatLiteLLM

from rag import format_recommendations_for_prompt
from system_prompt import SYSTEM_PROMPT_TEMPLATE


def resolve_model_name() -> str:
    model_name = os.environ.get("MODEL_NAME", "litellm_proxy/js2/gpt-oss-120b").strip()
    if model_name.startswith("litellm_proxy/"):
        return model_name
    return f"litellm_proxy/{model_name}"


MODEL_NAME = resolve_model_name()
API_BASE = "https://llm-api.cyverse.ai"
RAG_RESULTS = 5
DATASET_LENGTH = None


def normalize_response_text(content: Any) -> str:
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "thinking":
                    continue
                parts.append(item.get("text") or item.get("content") or "")
            else:
                item_type = getattr(item, "type", None)
                if item_type == "thinking":
                    continue
                text_value = getattr(item, "text", None) or getattr(item, "content", None)
                parts.append(text_value if text_value is not None else str(item))
        content = "\n".join(parts)
    elif content is None:
        content = ""
    else:
        content = str(content)

    cleaned = content.replace("\\n", "\n").replace("\r\n", "\n").strip()
    lines = [line.strip() for line in cleaned.split("\n")]
    return "\n".join(line for line in lines if line)


def build_messages(
    user_query: str,
    use_rag: bool = True,
    use_system_prompt: bool = True,
):
    messages = []

    if use_system_prompt:
        rag_context = ""
        if use_rag:
            rag_context = format_recommendations_for_prompt(
                query=user_query,
                n_results=RAG_RESULTS,
                dataset_length=DATASET_LENGTH,
            )
        messages.append(
            SystemMessage(content=SYSTEM_PROMPT_TEMPLATE.format(rag_context=rag_context))
        )
    elif use_rag:
        rag_context = format_recommendations_for_prompt(
            query=user_query,
            n_results=RAG_RESULTS,
            dataset_length=DATASET_LENGTH,
        )
        user_query = f"Retrieved context:\n{rag_context}\n\nUser request:\n{user_query}"

    messages.append(HumanMessage(content=user_query))
    return messages


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    api_key = os.environ.get("AIVERDE_API_KEY")
    if not api_key:
        raise RuntimeError("AIVERDE_API_KEY is not set.")

    llm = ChatLiteLLM(
        model=MODEL_NAME,
        api_key=api_key,
        api_base=API_BASE,
    )

    @app.errorhandler(Exception)
    def handle_exception(exc):
        app.logger.exception("Unhandled server error: %s", exc)
        return jsonify({"error": str(exc)}), 500

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/api/chat")
    def chat():
        payload = request.get_json(silent=True) or {}
        user_query = str(payload.get("message", "")).strip()
        use_rag = bool(payload.get("useRag", True))
        use_system_prompt = bool(payload.get("useSystemPrompt", True))
        if not user_query:
            return jsonify({"error": "Message is required."}), 400

        try:
            response = llm.invoke(
                build_messages(
                    user_query,
                    use_rag=use_rag,
                    use_system_prompt=use_system_prompt,
                )
            )
            return jsonify({"reply": normalize_response_text(response.content)})
        except Exception as exc:
            app.logger.exception("Chat request failed: %s", exc)
            return jsonify({"error": f"Backend request failed: {exc}"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
