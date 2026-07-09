from abc import ABC, abstractmethod
import re


class BaseTool(ABC):
    name: str

    @abstractmethod
    def can_handle(self, prompt: str) -> bool:
        """Cheap keyword/regex check — used by the agent's router."""

    @abstractmethod
    def run(self, prompt: str) -> str:
        """Execute and return a plain-text result. Raise ToolError on bad input."""


class ToolError(Exception):
    pass


class CalculatorTool(BaseTool):
    name = "CalculatorTool"
    _EXPR = re.compile(r"^[\d\.\s\+\-\*\/\(\)]+$")

    def can_handle(self, prompt: str) -> bool:
        return bool(re.search(r"\d+\s*[\+\-\*/]\s*\d+", prompt))

    def run(self, prompt: str) -> str:
        # Drop everything that isn't part of an expression (e.g. "What is " / "?")
        # rather than searching for the first run of whitelisted chars — a plain
        # search would stop at the first stray whitespace between words.
        expr = re.sub(r"[^\d\.\s\+\-\*/\(\)]", "", prompt).strip()
        if not expr or not self._EXPR.match(expr):
            raise ToolError(f"Could not parse a valid arithmetic expression from: {prompt!r}")
        try:
            # Safe: _EXPR whitelists digits/operators/parens only, builtins stripped.
            return str(eval(expr, {"__builtins__": {}}, {}))
        except ZeroDivisionError:
            raise ToolError("Division by zero")
        except (SyntaxError, TypeError):
            raise ToolError(f"Could not evaluate expression: {expr!r}")


class TextProcessorTool(BaseTool):
    name = "TextProcessorTool"

    def can_handle(self, prompt: str) -> bool:
        return any(k in prompt.lower() for k in ["uppercase", "lowercase", "word count"])

    def run(self, prompt: str) -> str:
        lower = prompt.lower()
        text = re.sub(r"(convert|to|uppercase|lowercase|word count|of)", "", lower, flags=re.I).strip(" '\"")
        if "uppercase" in lower:
            return text.upper()
        if "lowercase" in lower:
            return text.lower()
        if "word count" in lower:
            return str(len(text.split()))
        raise ToolError("No recognized text operation in prompt")


class WeatherMockTool(BaseTool):
    name = "WeatherMockTool"
    _MOCK_DATA = {"toronto": "18°C, Cloudy", "vancouver": "15°C, Rainy", "montreal": "20°C, Sunny"}

    def can_handle(self, prompt: str) -> bool:
        return "weather" in prompt.lower()

    def run(self, prompt: str) -> str:
        for city, forecast in self._MOCK_DATA.items():
            if city in prompt.lower():
                return f"{city.title()}: {forecast}"
        return "No mock data for that city (defaulting): 20°C, Clear"
