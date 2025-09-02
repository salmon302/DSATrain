from src.services.providers.base import AIContext
from src.services.providers.openai_real import OpenAIRealProvider
from src.services.providers.anthropic_real import AnthropicRealProvider
from src.services.providers.openrouter_real import OpenRouterRealProvider


def test_openai_real_contract_shapes(monkeypatch):
    # Ensure no API key required for placeholder behavior by setting dummy keys
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    ctx = AIContext(enable_ai=False, provider="openai-real", model=None)
    prov = OpenAIRealProvider()

    hint = prov.generate_hint(problem=type("P", (), {"id": "p1"})(), query="q", ctx=ctx)
    assert hint["provider"] == "openai-real"
    assert "hints" in hint and isinstance(hint["hints"], list)

    review = prov.review_code("code", rubric=None, ctx=ctx)
    assert review["provider"] == "openai-real"
    assert "suggestions" in review

    prompts = prov.elaborate_prompts(problem=type("P", (), {"id": "p1"})(), ctx=ctx)
    assert prompts["provider"] == "openai-real"
    assert "why_questions" in prompts


def test_anthropic_real_contract_shapes(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    ctx = AIContext(enable_ai=False, provider="anthropic-real", model=None)
    prov = AnthropicRealProvider()

    hint = prov.generate_hint(problem=type("P", (), {"id": "p1"})(), query=None, ctx=ctx)
    assert hint["provider"] == "anthropic-real"

    review = prov.review_code("code", rubric=None, ctx=ctx)
    assert review["provider"] == "anthropic-real"

    prompts = prov.elaborate_prompts(problem=type("P", (), {"id": "p1"})(), ctx=ctx)
    assert prompts["provider"] == "anthropic-real"


def test_openrouter_real_contract_shapes(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy")
    ctx = AIContext(enable_ai=False, provider="openrouter-real", model=None)
    prov = OpenRouterRealProvider()

    hint = prov.generate_hint(problem=type("P", (), {"id": "p1"})(), query=None, ctx=ctx)
    assert hint["provider"] == "openrouter-real"

    review = prov.review_code("code", rubric=None, ctx=ctx)
    assert review["provider"] == "openrouter-real"

    prompts = prov.elaborate_prompts(problem=type("P", (), {"id": "p1"})(), ctx=ctx)
    assert prompts["provider"] == "openrouter-real"
