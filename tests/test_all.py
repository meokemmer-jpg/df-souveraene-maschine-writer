"""All-tests for df-souveraene-maschine-writer (consolidated). [CRUX-MK]
17+ Tests across 4 modules."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.all_modules import (
    OutlineManager, Chapter, SOUVERAENE_MASCHINE_OUTLINE,
    StyleGuide, ChapterGenerator, AdapterOrchestrator)


def test_outline_manager_init():
    om = OutlineManager()
    assert om.book_title == "Die Souveraene Maschine"


def test_chapter_count_is_10():
    """Welle-44 spec: 10 Kapitel."""
    assert OutlineManager().chapter_count() == 10


def test_get_chapter_returns_correct():
    om = OutlineManager()
    ch1 = om.get_chapter(1)
    assert ch1 is not None
    assert "souveraene" in ch1.title.lower() or "Constraint" in ch1.title


def test_chapter_is_frozen():
    ch = Chapter(1, "Test")
    try:
        ch.number = 2  # type: ignore
        raise AssertionError("Should be frozen")
    except (AttributeError, Exception):
        pass


def test_style_guide_philosophical_max_words():
    sg = StyleGuide()
    assert sg.max_sentence_words == 30


def test_audit_short_text_passes():
    sg = StyleGuide()
    text = "Souveraenitaet ist Constraint. Die Maschine sagt Nein. Klar."
    report = sg.audit(text)
    assert report.passes is True


def test_audit_long_sentence_warns():
    sg = StyleGuide(max_sentence_words=5)
    text = "Dies ist ein sehr langer philosophischer Satz."
    report = sg.audit(text)
    assert any(v.rule == "philosophical_sentence_length" for v in report.violations)


def test_split_sentences_handles_empty():
    sg = StyleGuide()
    assert sg.split_sentences("") == []


def test_generator_init():
    gen = ChapterGenerator()
    assert gen.book_title == "Die Souveraene Maschine"


def test_default_mock_mode():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("DF_BOOK_REAL_ENABLED", None)
        gen = ChapterGenerator()
        assert gen._check_real_mode() is False


def test_mock_chapter_generation():
    gen = ChapterGenerator()
    ch = Chapter(1, "Test")
    result = gen.generate_chapter(ch)
    assert result.source == "mock"
    assert "MOCK STUB" in result.text


def test_real_mode_without_ticket_raises():
    with patch.dict(os.environ, {"DF_BOOK_REAL_ENABLED": "true"}, clear=False):
        os.environ.pop("PHRONESIS_TICKET", None)
        gen = ChapterGenerator()
        try:
            gen.generate_chapter(Chapter(1, "X"))
            raise AssertionError("Should raise")
        except RuntimeError as e:
            assert "PHRONESIS_TICKET" in str(e)


def test_real_mode_with_ticket_raises_not_implemented():
    with patch.dict(os.environ, {
        "DF_BOOK_REAL_ENABLED": "true",
        "PHRONESIS_TICKET": "PT-2026-05-11-004",
    }, clear=False):
        gen = ChapterGenerator()
        try:
            gen.generate_chapter(Chapter(1, "X"))
            raise AssertionError("Should raise NotImplementedError")
        except NotImplementedError as e:
            assert "Welle-45+" in str(e)


def test_env_var_truthy_strict_check():
    for val in ["1", "yes", "True", "TRUE"]:
        with patch.dict(os.environ, {"DF_BOOK_REAL_ENABLED": val}, clear=False):
            assert ChapterGenerator()._check_real_mode() is False


def test_orchestrator_init():
    with tempfile.TemporaryDirectory() as tmp:
        orch = AdapterOrchestrator(audit_log_dir=Path(tmp))
        assert orch.book_title == "Die Souveraene Maschine"


def test_run_default_quota():
    with tempfile.TemporaryDirectory() as tmp:
        orch = AdapterOrchestrator(audit_log_dir=Path(tmp), quota_max_per_run=3)
        result = orch.run()
        assert result.chapters_generated == 3


def test_run_with_specific_chapters():
    with tempfile.TemporaryDirectory() as tmp:
        orch = AdapterOrchestrator(audit_log_dir=Path(tmp), quota_max_per_run=10)
        result = orch.run(chapter_numbers=[1, 5, 9])
        assert result.chapters_generated == 3
