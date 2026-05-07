"""
Pytest tests for the Mergington High School API.

Tests use the Arrange-Act-Assert pattern and cover the backend endpoints for
activities, signup, duplicate signup handling, unknown activities, unregister,
and unregister error behavior.
"""

import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity data before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities_returns_success(self, client):
        # Arrange
        expected_activity_name = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert expected_activity_name in response_data
        assert response_data[expected_activity_name]["description"] == "Learn strategies and compete in chess tournaments"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_returns_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        url = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(url, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_participant_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        url = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(url, params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_for_unknown_activity_returns_404(self, client):
        # Arrange
        activity_name = "Non-existent Club"
        email = "newstudent@mergington.edu"
        url = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.post(url, params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_existing_participant_returns_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        url = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.delete(url, params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]

    def test_unregister_non_signed_up_participant_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"
        url = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.delete(url, params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"

    def test_unregister_from_unknown_activity_returns_404(self, client):
        # Arrange
        activity_name = "Non-existent Club"
        email = "michael@mergington.edu"
        url = f"/activities/{quote(activity_name)}/signup"

        # Act
        response = client.delete(url, params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
