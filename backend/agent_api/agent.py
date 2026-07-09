"""Agent Controller module for managing task execution based on user prompts."""
from agent_api.tools import (
    BaseTool,
    CalculatorTool,
    CityTimeTool,
    DaysSinceTool,
    TextProcessorTool,
    WeatherMockTool,
    ToolError,
)
from agent_api.models import Task, ExecutionStep


class AgentController:
    """
    The AgentController class manages the execution of tasks based on user prompts.
    It selects appropriate tools to handle sub-prompts, logs execution steps, 
    and returns the final result.
    """

    def __init__(self):
        # Ordered: first can_handle match wins. DaysSinceTool must precede
        # CalculatorTool — a bare date like 2024-01-15 parses as arithmetic
        # (2024 - 01 - 15), so the calculator would steal date prompts.
        self.tools: list[BaseTool] = [
            DaysSinceTool(),
            CalculatorTool(),
            TextProcessorTool(),
            WeatherMockTool(),
            CityTimeTool(),
        ]

    def _select_tool(self, sub_prompt: str) -> BaseTool | None:
        """
        Selects the appropriate tool for a given sub-prompt.

        Args:
            sub_prompt (str): The sub-prompt to be processed.

        Returns:
            BaseTool | None: The selected tool if found, otherwise None.
        """
        return next((t for t in self.tools if t.can_handle(sub_prompt)), None)

    def run(self, prompt: str) -> Task:
        """
        Executes the given prompt by splitting it into sub-prompts, selecting appropriate tools,
        logging execution steps, and returning the final result.

        Args:
            prompt (str): The user input prompt to be processed.

        Returns:
            Task: The Task object containing the final result and execution steps.
        """
        task = Task(prompt=prompt)
        task.save()
        step_num = 1

        def log(description, tool_name=None):
            """
            Logs the execution step with the given description and tool name.
            Args:
                description (str): Description of the execution step.
                tool_name (str, optional): Name of the tool used in this step. Defaults to None.
            """
            nonlocal step_num
            step = ExecutionStep(
                task=task,
                step_number=step_num,
                description=description,
                tool_name=tool_name,
            )
            step.save()
            step_num += 1

        log(f'Received input "{prompt}"')

        sub_prompts = [p.strip() for p in prompt.split(" and ") if p.strip()]
        outputs = []
        for sub in sub_prompts:
            tool = self._select_tool(sub)
            if tool is None:
                log(f'No matching tool for: "{sub}"')
                outputs.append(f"(unhandled: {sub})")
                continue
            log(f"Selected tool: {tool.name}", tool_name=tool.name)
            try:
                result = tool.run(sub)
                log(f"Tool result: {result}", tool_name=tool.name)
                outputs.append(result)
            except ToolError as e:
                log(f"Tool error: {e}", tool_name=tool.name)
                outputs.append(f"(error: {e})")

        final_result = " | ".join(outputs)
        log("Returning result to user")

        task.result = final_result
        task.save(update_fields=["result"])
        return task
