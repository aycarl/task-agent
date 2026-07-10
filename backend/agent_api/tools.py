"""Tools module for the agent API."""

import ast
from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
import re
from zoneinfo import ZoneInfo


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

    # Instruction/filler words stripped out when extracting the operand text.
    # \b-bounded so a word is only removed as a whole word — without this,
    # a bare "to" would also delete itself out of content like "Tokyo".
    _STRIP_RE = re.compile(
        r"\b("
        r"convert|transform|set|make|turn|change|please|into|to|of|"
        r"upper case|uppercase|lower case|lowercase|word count|reverse"
        r")\b",
        re.I,
    )

    def can_handle(self, prompt: str) -> bool:
        lower = prompt.lower()
        return any(
            k in lower
            for k in [
                "uppercase",
                "upper case",
                "lowercase",
                "lower case",
                "word count",
                "reverse",
            ]
        )

    def run(self, prompt: str) -> str:
        lower = prompt.lower()
        text = self._STRIP_RE.sub("", lower).strip(" '\"")
        if "uppercase" in lower or "upper case" in lower:
            return text.upper()
        if "lowercase" in lower or "lower case" in lower:
            return text.lower()
        if "word count" in lower:
            return str(len(text.split()))
        if "reverse" in lower:
            return text[::-1]
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


class DaysSinceTool(BaseTool):
    """Tool for counting the days since (or until) a calendar date."""

    name = "DaysSinceTool"
    # Each pattern pairs a regex that finds the date substring with the
    # strptime formats to try on it (commas stripped first).
    _DATE_PATTERNS = [
        (re.compile(r"\d{4}-\d{2}-\d{2}"), ["%Y-%m-%d"]),
        (re.compile(r"[A-Za-z]+ \d{1,2},? \d{4}"), ["%B %d %Y", "%b %d %Y"]),
    ]

    def _extract_date(self, prompt: str) -> date | None:
        """Return the first parseable date found in prompt, or None."""
        for pattern, formats in self._DATE_PATTERNS:
            match = pattern.search(prompt)
            if not match:
                continue
            text = match.group().replace(",", "")
            for fmt in formats:
                try:
                    return datetime.strptime(text, fmt).date()
                except ValueError:
                    continue
        return None

    def can_handle(self, prompt: str) -> bool:
        return "days since" in prompt.lower() or "days until" in prompt.lower()

    def run(self, prompt: str) -> str:
        parsed = self._extract_date(prompt)
        if parsed is None:
            raise ToolError(f"Could not parse a date from: {prompt!r}")
        delta = (date.today() - parsed).days
        if "days until" in prompt.lower():
            delta = -delta
        return str(delta)


class CityTimeTool(BaseTool):
    """Tool for reporting the current time in a city."""

    name = "CityTimeTool"
    _CITY_ZONES = {
        "toronto": "America/Toronto",
        "vancouver": "America/Vancouver",
        "montreal": "America/Toronto",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
    }

    def can_handle(self, prompt: str) -> bool:
        return "time in" in prompt.lower() or "current time" in prompt.lower()

    def run(self, prompt: str) -> str:
        lower = prompt.lower()
        for city, zone in self._CITY_ZONES.items():
            if city in lower:
                now = datetime.now(ZoneInfo(zone))
                return f"{city.title()}: {now.strftime('%H:%M')} ({now.strftime('%Z')})"
        now = datetime.now(timezone.utc)
        return f"No timezone data for that city (defaulting to UTC): {now.strftime('%H:%M')}"
