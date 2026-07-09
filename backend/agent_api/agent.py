from .tools import BaseTool, CalculatorTool, TextProcessorTool, WeatherMockTool, ToolError
from .models import Task, ExecutionStep


class AgentController:
    def __init__(self):
        self.tools: list[BaseTool] = [CalculatorTool(), TextProcessorTool(), WeatherMockTool()]

    def _select_tool(self, sub_prompt: str) -> BaseTool | None:
        return next((t for t in self.tools if t.can_handle(sub_prompt)), None)

    def run(self, prompt: str) -> Task:
        task = Task.objects.create(prompt=prompt)
        step_num = 1

        def log(description, tool_name=None):
            nonlocal step_num
            ExecutionStep.objects.create(
                task=task, step_number=step_num, description=description, tool_name=tool_name
            )
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
