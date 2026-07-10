"""Tests for the agent API tools."""
from datetime import date
import re

import pytest

from agent_api.tools import (
    CalculatorTool,
    CityTimeTool,
    DaysSinceTool,
    TextProcessorTool,
    WeatherMockTool,
    ToolError,
)


def test_calculator_basic():
    """Test basic arithmetic operations."""
    assert CalculatorTool().run("What is 15 + 27?") == "42"


def test_calculator_bad_input_raises():
    """Test that bad input raises a ToolError."""
    with pytest.raises(ToolError):
        CalculatorTool().run("what is the meaning of life")


def test_calculator_division_by_zero_raises():
    """Test that division by zero raises a ToolError."""
    with pytest.raises(ToolError):
        CalculatorTool().run("What is 5 / 0?")


def test_calculator_parentheses_expression():
    """Test arithmetic expressions with parentheses."""
    assert CalculatorTool().run("What is (2 + 3) * 4?") == "20"


def test_calculator_malformed_expression_raises():
    """Test that malformed expressions raise a ToolError."""
    with pytest.raises(ToolError):
        CalculatorTool().run("What is 2 + ?")


def test_text_processor_uppercase():
    """Test converting text to uppercase."""
    assert TextProcessorTool().run("convert 'hello world' to uppercase") == "HELLO WORLD"


def test_text_processor_lowercase():
    """Test converting text to lowercase."""
    assert TextProcessorTool().run("convert 'HELLO' to lowercase") == "hello"


def test_text_processor_word_count():
    """Test counting words in text."""
    assert TextProcessorTool().run("word count of 'one two three'") == "3"


def test_text_processor_reverse():
    """Test reversing text."""
    assert TextProcessorTool().run("reverse 'hello world'") == "dlrow olleh"


def test_weather_known_city():
    """Test fetching weather for a known city."""
    assert "Toronto" in WeatherMockTool().run("weather in Toronto")


def test_weather_unknown_city_defaults():
    """Test fetching weather for an unknown city defaults correctly."""
    assert "No mock data" in WeatherMockTool().run("weather in Atlantis")


def test_days_since_iso_date():
    """Test counting days since an ISO-format date."""
    expected = (date.today() - date(2024, 1, 15)).days
    assert DaysSinceTool().run("days since 2024-01-15") == f"{expected} days since 2024-01-15"


def test_days_until_future_date_with_written_month():
    """Test that a future date in 'Month D, YYYY' format is phrased as days until."""
    assert DaysSinceTool().run("how many days until December 25, 2099?").endswith(
        "days until 2099-12-25"
    )


def test_days_since_no_parseable_date_raises():
    """Test that a prompt without a recognizable date raises a ToolError."""
    with pytest.raises(ToolError):
        DaysSinceTool().run("days since forever")


def test_city_time_known_city_format():
    """Test that a known city returns a City: HH:MM (zone) shaped reply."""
    result = CityTimeTool().run("what time is it in Tokyo?")
    assert re.fullmatch(r"Tokyo: \d{2}:\d{2} \(.+\)", result)


def test_city_time_unknown_city_defaults_to_utc():
    """Test that an unknown city falls back to UTC."""
    assert "defaulting to UTC" in CityTimeTool().run("time in Atlantis")
