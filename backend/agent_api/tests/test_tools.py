import pytest

from agent_api.tools import CalculatorTool, TextProcessorTool, WeatherMockTool, ToolError


def test_calculator_basic():
    assert CalculatorTool().run("What is 15 + 27?") == "42"


def test_calculator_bad_input_raises():
    with pytest.raises(ToolError):
        CalculatorTool().run("what is the meaning of life")


def test_calculator_division_by_zero_raises():
    with pytest.raises(ToolError):
        CalculatorTool().run("What is 5 / 0?")


def test_text_processor_uppercase():
    assert TextProcessorTool().run("convert 'hello world' to uppercase") == "HELLO WORLD"


def test_text_processor_lowercase():
    assert TextProcessorTool().run("convert 'HELLO' to lowercase") == "hello"


def test_text_processor_word_count():
    assert TextProcessorTool().run("word count of 'one two three'") == "3"


def test_weather_known_city():
    assert "Toronto" in WeatherMockTool().run("weather in Toronto")


def test_weather_unknown_city_defaults():
    assert "No mock data" in WeatherMockTool().run("weather in Atlantis")
