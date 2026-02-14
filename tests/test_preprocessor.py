"""Tests for script text preprocessing."""

from sba.parsing.preprocessor import preprocess_script_text


def test_removes_page_numbers():
    text = "some text\n\n  42  \n\nmore text"
    result = preprocess_script_text(text)
    assert "42" not in result
    assert "some text" in result
    assert "more text" in result


def test_removes_continued_markers():
    text = "JOHN\nHello there.\n(CONTINUED)\n\nCONTINUED:\nJOHN (CONT'D)\nMore dialogue."
    result = preprocess_script_text(text)
    assert "(CONTINUED)" not in result
    assert "CONTINUED:" not in result
    assert "JOHN" in result
    assert "JOHN (CONT'D)" in result  # Character CONT'D preserved


def test_collapses_blank_lines():
    text = "line 1\n\n\n\n\nline 2"
    result = preprocess_script_text(text)
    assert "\n\n\n" not in result
    assert "line 1" in result
    assert "line 2" in result


def test_normalizes_line_endings():
    text = "line 1\r\nline 2\rline 3\nline 4"
    result = preprocess_script_text(text)
    assert "\r" not in result
    assert result.count("\n") >= 3
