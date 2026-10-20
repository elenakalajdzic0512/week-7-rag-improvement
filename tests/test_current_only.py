from src import config
from src.chunking import Chunk
from src.rag import REFUSAL_MESSAGE, build_grounded_answer
from src.retrieval import lexical_score, retrieve_top_k, searchable_chunks


def make_chunk(chunk_id: str, status: str, text: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id=chunk_id,
        title="Policy",
        version="2026",
        status=status,
        text=text,
    )


def test_disabled_filter_preserves_all_candidates_and_order(monkeypatch) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", False)
    chunks = [
        make_chunk("old", "superseded", "remote days"),
        make_chunk("other", "draft", "remote days"),
        make_chunk("new", "current", "remote days"),
    ]

    assert searchable_chunks(chunks) is chunks
    assert [chunk.chunk_id for chunk in searchable_chunks(chunks)] == ["old", "other", "new"]


def test_enabled_filter_keeps_only_exact_current_status(monkeypatch) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    chunks = [
        make_chunk("a", "current", "remote days"),
        make_chunk("b", "superseded", "remote days"),
        make_chunk("c", "draft", "remote days"),
        make_chunk("d", "Current", "remote days"),
        make_chunk("e", "current", "office days"),
    ]

    selected = searchable_chunks(chunks)
    assert [chunk.chunk_id for chunk in selected] == ["a", "e"]
    assert selected[0] is chunks[0]
    assert selected[1] is chunks[4]


def test_empty_input_returns_empty_with_filter_on_or_off(monkeypatch) -> None:
    for enabled in (False, True):
        monkeypatch.setattr(config, "CURRENT_ONLY", enabled)
        assert searchable_chunks([]) == []
        assert retrieve_top_k("remote", [], k=2) == []


def test_only_superseded_sources_lead_to_existing_refusal(monkeypatch) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    chunks = [make_chunk("old", "superseded", "remote days per week")]

    assert retrieve_top_k("remote days", chunks) == []
    answer = build_grounded_answer("remote days", chunks)
    assert answer.refused is True
    assert answer.answer == REFUSAL_MESSAGE
    assert answer.citations == []
    assert answer.retrieved == []


def test_filter_precedes_scoring_and_top_k(monkeypatch) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    old = make_chunk("old", "superseded", "remote remote remote")
    current = make_chunk("new", "current", "remote office calendar")
    assert lexical_score("remote", old.text) > lexical_score("remote", current.text)

    results = retrieve_top_k("remote", [old, current], k=1)
    assert [result.chunk.chunk_id for result in results] == ["new"]


def test_filter_does_not_mutate_input_or_chunks(monkeypatch) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    chunks = [
        make_chunk("old", "superseded", "remote days"),
        make_chunk("new", "current", "remote days"),
    ]
    original = list(chunks)
    original_fields = [(chunk.chunk_id, chunk.status, chunk.text) for chunk in chunks]

    selected = searchable_chunks(chunks)
    assert selected is not chunks
    assert [chunk is original[i] for i, chunk in enumerate(chunks)] == [True, True]
    assert chunks == original
    assert [(chunk.chunk_id, chunk.status, chunk.text) for chunk in chunks] == original_fields
    assert selected[0] is chunks[1]
