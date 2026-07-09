"""Unit tests for the API endpoints in the agent_api module."""
import pytest
from rest_framework.test import APIClient
from agent_api.agent import AgentController


@pytest.fixture
def client():
    """Fixture to provide an APIClient instance for testing."""
    return APIClient()


def test_create_task_returns_201_with_steps(db, client):
    """Test that creating a task via the API returns a 201 status and includes execution steps."""
    response = client.post("/api/tasks/", {"prompt": "What is 15 + 27?"}, format="json")
    assert response.status_code == 201
    data = response.json()
    assert data["result"] == "42"
    assert len(data["steps"]) == 4
    assert data["steps"][0]["tool_name"] is None


def test_create_task_multi_step(db, client):
    """Test that creating a multi-step task via the API returns a 201 status and includes execution steps."""
    response = client.post(
        "/api/tasks/", {"prompt": "What is 2 + 2 and weather in Toronto"}, format="json"
    )
    assert response.status_code == 201
    data = response.json()
    assert data["result"] == "4 | Toronto: 18°C, Cloudy"
    assert len(data["steps"]) == 6


def test_create_task_empty_prompt_returns_400(db, client):
    """Test that creating a task with an empty prompt returns a 400 status."""
    response = client.post("/api/tasks/", {"prompt": ""}, format="json")
    assert response.status_code == 400
    assert response.json() == {"error": "prompt is required"}


def test_create_task_missing_prompt_returns_400(db, client):
    """Test that creating a task without a prompt returns a 400 status."""
    response = client.post("/api/tasks/", {}, format="json")
    assert response.status_code == 400
    assert response.json() == {"error": "prompt is required"}


def test_list_tasks_omits_steps_most_recent_first(db, client):
    """
    Test that listing tasks via the API omits steps 
    and returns tasks in most recent first order.
    """
    AgentController().run("What is 1 + 1?")
    AgentController().run("weather in Toronto")

    response = client.get("/api/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert "steps" not in data[0]
    assert data[0]["prompt"] == "weather in Toronto"
    assert data[1]["prompt"] == "What is 1 + 1?"


def test_retrieve_task_includes_steps(db, client):
    """Test that retrieving a specific task via the API includes execution steps."""
    task = AgentController().run("What is 1 + 1?")

    response = client.get(f"/api/tasks/{task.id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert "steps" in data
    assert len(data["steps"]) == 4


def test_retrieve_missing_task_returns_404(db, client):
    """Test that retrieving a non-existent task returns a 404 status."""
    response = client.get("/api/tasks/999999/")
    assert response.status_code == 404
    assert response.json() == {"error": "not found"}
