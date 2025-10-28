import pytest

from app.services import nlp_service


class _FakeSettings:
    openai_api_key = "test-key"
    openai_model = "test-model"


class _MissingKeySettings:
    openai_api_key = None
    openai_model = "test-model"


class _DummyChain:
    def __init__(self, response):
        self.response = response
        self.received = None

    async def ainvoke(self, inputs):
        self.received = inputs
        return self.response


@pytest.mark.asyncio
async def test_generate_summary_raises_for_empty_transcript(monkeypatch) -> None:
    monkeypatch.setattr(nlp_service, "get_settings", lambda: _FakeSettings)

    with pytest.raises(ValueError):
        await nlp_service.generate_summary("   ")


@pytest.mark.asyncio
async def test_generate_summary_returns_normalised_payload(monkeypatch) -> None:
    chain = _DummyChain(
        {
            "summary": "meeting summary",
            "actions": [{"task": "Do thing"}, "ignore"],
            "topics": ["Topic A", 123],
        }
    )

    monkeypatch.setattr(nlp_service, "get_settings", lambda: _FakeSettings)
    monkeypatch.setattr(nlp_service, "_get_chain", lambda api_key, model_name: chain)

    result = await nlp_service.generate_summary(" Valid transcript ")

    assert chain.received == {"transcript": "Valid transcript"}
    assert result["summary"] == "meeting summary"
    assert result["actions"] == [{"task": "Do thing"}]
    assert result["topics"] == ["Topic A"]
    assert result["transcript_length"] == len("Valid transcript")


@pytest.mark.asyncio
async def test_generate_summary_requires_api_key(monkeypatch) -> None:
    monkeypatch.setattr(nlp_service, "get_settings", lambda: _MissingKeySettings)

    with pytest.raises(RuntimeError):
        await nlp_service.generate_summary("Transcript")


@pytest.mark.asyncio
async def test_extract_actions_returns_only_dicts(monkeypatch) -> None:
    async def fake_generate_summary(_: str):
        return {"actions": [{"task": "A"}, "skip"], "summary": "", "topics": []}

    monkeypatch.setattr(nlp_service, "generate_summary", fake_generate_summary)

    result = await nlp_service.extract_actions("something")

    assert result == [{"task": "A"}]
