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

        # " then " splits the prompt into sequential stages, where each
        # stage's result is piped into the next stage's input. " and "
        # (within a stage) stays parallel/independent, as before.
        stages = [s.strip() for s in prompt.split(" then ") if s.strip()]
        previous_result: str | None = None
        stage_outputs = []
        chain_broken = False

        for stage in stages:
            if chain_broken:
                log(f'Skipped "{stage}" — previous step failed')
                continue

            if previous_result is not None:
                log(f'Piping result "{previous_result}" into next step')
                stage = f"{previous_result} {stage}"

            sub_prompts = [p.strip() for p in stage.split(" and ") if p.strip()]
            outputs = []
            stage_failed = False
            for sub in sub_prompts:
                tool = self._select_tool(sub)
                if tool is None:
                    log(f'No matching tool for: "{sub}"')
                    outputs.append(f"(Unavailable tool: {sub})")
                    stage_failed = True
                    continue
                log(f"Selected tool: {tool.name}", tool_name=tool.name)
                try:
                    result = tool.run(sub)
                    log(f"Tool result: {result}", tool_name=tool.name)
                    outputs.append(result)
                except ToolError as e:
                    log(f"Tool error: {e}", tool_name=tool.name)
                    outputs.append(f"(error: {e})")
                    stage_failed = True

            stage_result = " | ".join(outputs)
            stage_outputs.append(stage_result)
            previous_result = stage_result
            chain_broken = stage_failed

        final_result = stage_outputs[-1] if stage_outputs else ""
        log("Returning result to user")

        task.result = final_result
        task.save(update_fields=["result"])
        return task
