import requests
import json

BASE_URL = "http://localhost:8001"

def test_register():
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/register", json=data)
    print("Register:", response.status_code, response.text)

def test_login():
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/login", json=data)
    print("Login:", response.status_code, response.text)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_create_task(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test Task",
        "description": "This is a test task"
    }
    response = requests.post(f"{BASE_URL}/tasks", json=data, headers=headers)
    print("Create Task:", response.status_code, response.text)

def test_get_tasks(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks", headers=headers)
    print("Get Tasks:", response.status_code, response.json())

def test_update_task(token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Updated Task",
        "completed": True
    }
    response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=data, headers=headers)
    print("Update Task:", response.status_code, response.json())

def test_delete_task(token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print("Delete Task:", response.status_code, response.json())

if __name__ == "__main__":
    test_register()
    token = test_login()
    if token:
        test_create_task(token)
        test_get_tasks(token)
        # Assuming task id 1 for demo
        test_update_task(token, 1)
        test_delete_task(token, 1)