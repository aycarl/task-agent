# pylint: disable=no-member,unused-argument
"""Unit tests for the AgentController class in the agent_api module."""

from agent_api.agent import AgentController


def test_single_tool_trace_has_expected_steps(db):
    """Test that a single tool execution produces the expected steps in the task trace."""
    task = AgentController().run("Convert 'hi' to uppercase")
    descriptions = [s.description for s in task.steps.all()]
    assert descriptions[0].startswith("Received input")
    assert "TextProcessorTool" in descriptions[1]
    assert task.result == "HI"


def test_multi_step_chains_two_tools(db):
    """Test that a multi-step prompt involving two tools produces the expected steps and result."""
    task = AgentController().run("What is 2 + 2 and weather in Toronto")
    tool_names = [s.tool_name for s in task.steps.all() if s.tool_name]
    assert "CalculatorTool" in tool_names and "WeatherMockTool" in tool_names
    assert task.result == "4 | Toronto: 18°C, Cloudy"


def test_unmatched_prompt_logs_no_matching_tool(db):
    """Test that an unmatched prompt logs a step indicating no matching tool was found."""
    task = AgentController().run("tell me a joke")
    descriptions = [s.description for s in task.steps.all()]
    assert any("No matching tool" in d for d in descriptions)


def test_date_prompt_routes_to_days_since_not_calculator(db):
    """Test tool ordering: a bare date parses as arithmetic (2024 - 01 - 15 = 2008),
    so DaysSinceTool must win the route ahead of CalculatorTool."""
    task = AgentController().run("days since 2024-01-15")
    tool_names = {s.tool_name for s in task.steps.all() if s.tool_name}
    assert tool_names == {"DaysSinceTool"}


def test_multi_step_chains_three_tools(db):
    """Test that a three-part prompt routes each part to its own tool in one trace."""
    task = AgentController().run("days since 2025-01-01 and time in Tokyo and what is 15 * 4")
    tool_names = [s.tool_name for s in task.steps.all() if s.tool_name]
    assert "DaysSinceTool" in tool_names
    assert "CityTimeTool" in tool_names
    assert "CalculatorTool" in tool_names
