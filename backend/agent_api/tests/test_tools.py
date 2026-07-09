"""Tests for the agent API tools."""
import pytest

from agent_api.tools import CalculatorTool, TextProcessorTool, WeatherMockTool, ToolError


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


def test_weather_known_city():
    """Test fetching weather for a known city."""
    assert "Toronto" in WeatherMockTool().run("weather in Toronto")


def test_weather_unknown_city_defaults():
    """Test fetching weather for an unknown city defaults correctly."""
    assert "No mock data" in WeatherMockTool().run("weather in Atlantis")
