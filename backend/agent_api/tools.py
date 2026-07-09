"""Tools module for the agent API."""

import ast
from abc import ABC, abstractmethod
import re


class BaseTool(ABC):
    """Abstract base class for tools used by the agent API."""

    name: str

    @abstractmethod
    def can_handle(self, prompt: str) -> bool:
        """Cheap keyword/regex check — used by the agent's router."""

    @abstractmethod
    def run(self, prompt: str) -> str:
        """Execute and return a plain-text result. Raise ToolError on bad input."""


class ToolError(Exception):
    """Custom exception for tool errors."""


class CalculatorTool(BaseTool):
    """Tool for evaluating simple arithmetic expressions."""

    name = "CalculatorTool"
    _EXPR = re.compile(r"^[\d\.\s\+\-\*\/\(\)]+$")

    def _extract_expression(self, prompt: str) -> str | None:
        """Return a strict arithmetic expression extracted from prompt, or None."""
        candidate = re.sub(r"[^\d\.\s\+\-\*/\(\)]", "", prompt).strip()
        if not candidate:
            return None
        if not self._EXPR.fullmatch(candidate):
            return None
        if not re.search(r"\d", candidate) or not re.search(r"[\+\-\*/]", candidate):
            return None
        return candidate

    def _eval_node(self, node: ast.AST) -> float:
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError()
                return left / right
            raise ValueError("unsupported operator")

        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise ValueError("unsupported unary operator")

        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)

        raise ValueError("unsupported expression")

    def _evaluate_expression(self, expr: str) -> str:
        parsed = ast.parse(expr, mode="eval")
        result = self._eval_node(parsed.body)
        if result.is_integer():
            return str(int(result))
        return str(result)

    def can_handle(self, prompt: str) -> bool:
        return self._extract_expression(prompt) is not None

    def run(self, prompt: str) -> str:
        expr = self._extract_expression(prompt)
        if expr is None:
            raise ToolError(
                f"Could not parse a valid arithmetic expression from: {prompt!r}"
            )
        try:
            return self._evaluate_expression(expr)
        except ZeroDivisionError as exc:
            raise ToolError("Division by zero") from exc
        except (SyntaxError, TypeError, ValueError) as exc:
            raise ToolError(f"Could not evaluate expression: {expr!r}") from exc


class TextProcessorTool(BaseTool):
    """Tool for processing text, including case conversion and word counting."""

    name = "TextProcessorTool"

    def can_handle(self, prompt: str) -> bool:
        return any(
            k in prompt.lower() for k in ["uppercase", "lowercase", "word count"]
        )

    def run(self, prompt: str) -> str:
        lower = prompt.lower()
        text = re.sub(
            r"(convert|to|uppercase|lowercase|word count|of)", "", lower, flags=re.I
        ).strip(" '\"")
        if "uppercase" in lower:
            return text.upper()
        if "lowercase" in lower:
            return text.lower()
        if "word count" in lower:
            return str(len(text.split()))
        raise ToolError("No recognized text operation in prompt")


class WeatherMockTool(BaseTool):
    """Mock tool for fetching weather information."""

    name = "WeatherMockTool"
    _MOCK_DATA = {
        "toronto": "18°C, Cloudy",
        "vancouver": "15°C, Rainy",
        "montreal": "20°C, Sunny",
    }

    def can_handle(self, prompt: str) -> bool:
        return "weather" in prompt.lower()

    def run(self, prompt: str) -> str:
        for city, forecast in self._MOCK_DATA.items():
            if city in prompt.lower():
                return f"{city.title()}: {forecast}"
        return "No mock data for that city (defaulting): 20°C, Clear"
