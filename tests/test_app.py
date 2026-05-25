"""
Tests for the Mergington High School API (backend)

All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice basketball skills and compete in inter-school games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Train for soccer matches and learn team strategies",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["maria@mergington.edu", "liam@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore painting, drawing, and mixed media art projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
    },
    "Drama Club": {
        "description": "Practice acting, stagecraft, and perform school productions",
        "schedule": "Thursdays, 3:30 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Science Club": {
        "description": "Explore experiments, science fairs, and research projects",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["olivia@mergington.edu", "ethan@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["daniel@mergington.edu", "zoe@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities before each test to avoid cross-test interference."""
    # Arrange: ensure activities start from a known state
    activities.clear()
    activities.update({k: v.copy() if isinstance(v, dict) else v for k, v in INITIAL_ACTIVITIES.items()})
    yield
    # No-op after test; fixture ensures fresh state on next test


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


def test_get_activities(client):
    """GET /activities returns all activities with expected fields."""
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_participant(client):
    """POST signup should add a new participant (AAA pattern)."""
    # Arrange
    activity = "Chess Club"
    email = "test_new_aaa@mergington.edu"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in resp.json()["message"]
    # Verify side-effect
    activities_resp = client.get("/activities").json()
    assert email in activities_resp[activity]["participants"]


def test_duplicate_signup_returns_400(client):
    """Attempting to sign up an existing participant returns 400."""
    # Arrange
    activity = "Chess Club"
    existing = "michael@mergington.edu"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": existing})

    # Assert
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"]


def test_remove_participant(client):
    """DELETE should remove a participant from an activity."""
    # Arrange
    activity = "Programming Class"
    temp = "temp_remover@mergington.edu"
    signup = client.post(f"/activities/{activity}/signup", params={"email": temp})
    assert signup.status_code == 200

    # Act
    resp = client.delete(f"/activities/{activity}/signup", params={"email": temp})

    # Assert
    assert resp.status_code == 200
    data = client.get("/activities").json()
    assert temp not in data[activity]["participants"]


def test_signup_invalid_activity_returns_404(client):
    """Signing up for a non-existent activity returns 404."""
    # Arrange
    activity = "No Such Activity"
    email = "noone@mergington.edu"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"
