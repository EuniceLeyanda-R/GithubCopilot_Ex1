"""
Test suite for FastAPI Mergington High School Activities API.

Tests cover all endpoints with both happy path and edge case scenarios.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 3
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_response_structure(self, client, reset_activities):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_contains_participants(self, client, reset_activities):
        """Test that activities include their current participants."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity."""
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 3
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup fails when activity doesn't exist."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity."""
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Try to signup again with the same email
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response2.status_code == 400
        result = response2.json()
        assert "already signed up" in result["detail"].lower()
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities."""
        email = "versatile@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity."""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "michael@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant from the activity."""
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister fails when activity doesn't exist."""
        response = client.delete(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregister fails when student is not registered for the activity."""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "not registered" in result["detail"].lower()
    
    def test_unregister_can_signup_again(self, client, reset_activities):
        """Test that after unregistering, a student can sign up again."""
        email = "flexible@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Unregister
        response1 = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify signed up
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
