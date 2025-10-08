
import json
import os

USER_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    
    if os.path.getsize(USER_FILE) == 0:
        return {}
        
    with open(USER_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def signup(username, password, role):
    users = load_users()
    if username in users:
        return False, "Username already exists!"
    
    users[username] = {"password": password, "role": role} 
    save_users(users)
    return True, "Account created successfully!"

def login(username, password):
    users = load_users()
    if username not in users:
        return False, "User not found!"
    if users[username]["password"] != password:
        return False, "Incorrect password!"
    return True, users[username]["role"]