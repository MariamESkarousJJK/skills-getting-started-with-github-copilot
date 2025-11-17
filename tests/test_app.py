import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

def test_signup_and_unregister():
    # Use a unique email for testing
    test_email = "pytestuser@mergington.edu"
    activity = "Chess Club"

    # Ensure not already signed up
    client.delete(f"/activities/{activity}/unregister", params={"email": test_email})

    # Sign up
    response = client.post(f"/activities/{activity}/signup", params={"email": test_email})
    assert response.status_code == 200
    assert f"Signed up {test_email}" in response.json()["message"]

    # Check participant is present
    activities = client.get("/activities").json()
    assert test_email in activities[activity]["participants"]

    # Unregister
    response = client.delete(f"/activities/{activity}/unregister", params={"email": test_email})
    assert response.status_code == 200
    assert f"Unregistered {test_email}" in response.json()["message"]

    # Check participant is removed
    activities = client.get("/activities").json()
    assert test_email not in activities[activity]["participants"]

def test_signup_duplicate():
    activity = "Programming Class"
    email = "emma@mergington.edu"  # Already present
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_full():
    # Fill up an activity artificially
    activity = "Gym Class"
    max_participants = 2
    activities[activity]["max_participants"] = max_participants
    activities[activity]["participants"] = [f"a{i}@mergington.edu" for i in range(max_participants)]
    response = client.post(f"/activities/{activity}/signup", params={"email": "new@mergington.edu"})
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]
