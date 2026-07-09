from agent_api.agent import AgentController


def test_single_tool_trace_has_expected_steps(db):
    task = AgentController().run("Convert 'hi' to uppercase")
    descriptions = [s.description for s in task.steps.all()]
    assert descriptions[0].startswith("Received input")
    assert "TextProcessorTool" in descriptions[1]
    assert task.result == "HI"


def test_multi_step_chains_two_tools(db):
    task = AgentController().run("What is 2 + 2 and weather in Toronto")
    tool_names = [s.tool_name for s in task.steps.all() if s.tool_name]
    assert "CalculatorTool" in tool_names and "WeatherMockTool" in tool_names
    assert task.result == "4 | Toronto: 18°C, Cloudy"


def test_unmatched_prompt_logs_no_matching_tool(db):
    task = AgentController().run("tell me a joke")
    descriptions = [s.description for s in task.steps.all()]
    assert any("No matching tool" in d for d in descriptions)
