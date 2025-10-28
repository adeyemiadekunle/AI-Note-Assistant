from __future__ import annotations

import logging
from threading import Lock
from typing import Any, Dict, List, Tuple

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)

_PARSER = JsonOutputParser()
_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an assistant that summarises meetings into concise notes. "
            "Follow the provided format instructions and ensure JSON output.",
        ),
        ("human", "Transcript:\n{transcript}\n\n{format_instructions}"),
    ]
).partial(format_instructions=_PARSER.get_format_instructions())

_chain_cache: Dict[Tuple[str, str], Runnable[Any, Dict[str, Any]]] = {}
_chain_lock = Lock()


def _get_chain(api_key: str, model_name: str) -> Runnable[Any, Dict[str, Any]]:
    key = (api_key, model_name)
    with _chain_lock:
        if key not in _chain_cache:
            llm = ChatOpenAI(model=model_name, temperature=0.2, api_key=api_key)
            _chain_cache[key] = _PROMPT | llm | _PARSER
    return _chain_cache[key]


def _normalise_summary_payload(data: Dict[str, Any], transcript: str) -> Dict[str, Any]:
    summary = data.get("summary") or ""
    actions = data.get("actions") or []
    topics = data.get("topics") or []

    if not isinstance(actions, list):
        actions = []
    if not isinstance(topics, list):
        topics = []

    filtered_actions = [action for action in actions if isinstance(action, dict)]
    filtered_topics = [topic for topic in topics if isinstance(topic, str)]

    return {
        "summary": summary,
        "actions": filtered_actions,
        "topics": filtered_topics,
        "transcript_length": len(transcript),
    }


async def generate_summary(transcript: str) -> Dict[str, Any]:
    cleaned_transcript = transcript.strip()
    if not cleaned_transcript:
        raise ValueError("Transcript is empty.")

    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API key is not configured.")

    chain = _get_chain(settings.openai_api_key, settings.openai_model)

    try:
        raw_response = await chain.ainvoke({"transcript": cleaned_transcript})
    except OutputParserException as exc:
        logger.error("Failed to parse LangChain output: %s", exc)
        raise RuntimeError("Failed to parse OpenAI response.") from exc
    except Exception as exc:  # pragma: no cover - unexpected LangChain/OpenAI issues
        logger.error("LangChain agent error: %s", exc)
        raise RuntimeError("OpenAI summarisation error.") from exc

    return _normalise_summary_payload(raw_response or {}, cleaned_transcript)


async def extract_actions(transcript: str) -> List[Dict[str, Any]]:
    summary = await generate_summary(transcript)
    actions = summary.get("actions", [])
    if isinstance(actions, list):
        return [action for action in actions if isinstance(action, dict)]
    return []
