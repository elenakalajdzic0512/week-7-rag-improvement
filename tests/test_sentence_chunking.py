import pytest

from src import config
from src.chunking import build_chunks, split_text, split_text_by_sentences
from src.corpus import Document


def test_greedy_packing_includes_separator_in_limit() -> None:
    assert split_text_by_sentences("One. Two? End!", 9) == ["One. Two?", "End!"]
    assert split_text_by_sentences("One. Two? End!", 8) == ["One.", "Two?", "End!"]


def test_oversized_sentence_stays_whole_and_separate() -> None:
    assert split_text_by_sentences("Hi. This sentence is too long! Bye.", 8) == [
        "Hi.", "This sentence is too long!", "Bye."
    ]


@pytest.mark.parametrize("text", ["", " \t\n "])
def test_empty_text(text: str) -> None:
    assert split_text_by_sentences(text) == []


@pytest.mark.parametrize("chunk_size", [0, -1])
@pytest.mark.parametrize("text", ["", "A sentence."])
def test_nonpositive_limit(text: str, chunk_size: int) -> None:
    with pytest.raises(ValueError, match="chunk_size must be > 0"):
        split_text_by_sentences(text, chunk_size)


def test_normalization_and_content_preservation() -> None:
    text = "  First\tpart.\nSecond?   Third!\r\nTrailing text  "
    chunks = split_text_by_sentences(text, 19)
    assert chunks == ["First part. Second?", "Third!", "Trailing text"]
    assert " ".join(chunks) == " ".join(text.split())


def test_only_whitespace_after_sentence_punctuation_is_a_boundary() -> None:
    assert split_text_by_sentences("A.B?C!D. Tail", 3) == ["A.B?C!D.", "Tail"]
    assert split_text_by_sentences("No final punctuation", 3) == ["No final punctuation"]


def test_sentence_dispatch_ignores_overlap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "CHUNK_STRATEGY", "sentences")
    monkeypatch.setattr(config, "CHUNK_SIZE", 9)
    monkeypatch.setattr(config, "CHUNK_OVERLAP", 999)
    assert split_text("One. Two? End!") == ["One. Two?", "End!"]


def test_build_chunks_preserves_order_ids_and_all_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "CHUNK_STRATEGY", "sentences")
    monkeypatch.setattr(config, "CHUNK_SIZE", 5)
    documents = [
        Document("a", "First", "Section", "2026", "current", "One. Two?"),
        Document("b", "Second", "Section", "2024", "superseded", "End!"),
    ]
    chunks = build_chunks(documents)
    assert [chunk.chunk_id for chunk in chunks] == ["a-chunk-0", "a-chunk-1", "b-chunk-0"]
    assert [chunk.text for chunk in chunks] == ["One.", "Two?", "End!"]
    for chunk, doc in zip(chunks, [documents[0], documents[0], documents[1]]):
        assert (chunk.doc_id, chunk.title, chunk.version, chunk.status) == (
            doc.doc_id, doc.title, doc.version, doc.status
        )
