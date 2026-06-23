from flask import Flask, jsonify, request, render_template, send_from_directory, redirect
import json
import os

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

TASKS_FILE = "task.json"

# ----------------------------------
# Read JSON Data
# ----------------------------------
def read_data():
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ----------------------------------
# Write JSON Data
# ----------------------------------
def write_data(data):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ----------------------------------
# Home Page
# ----------------------------------

@app.route("/")
def home():
    return render_template("login.html")

# ----------------------------------
# Dashboard
# ----------------------------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/members")
def members():
    return render_template("dashboard.html")
    



# ----------------------------------
# Get All Tasks
# ----------------------------------
@app.route("/task", methods=["GET"])
def get_tasks():
    data = read_data()
    return jsonify(data)

# ----------------------------------
# Add Task
# ----------------------------------
@app.route("/task", methods=["POST"])
def add_task():
    data = read_data()
    body = request.get_json()

    if not body.get("title"):
        return jsonify({
            "error": "Title required"
        }), 400

    new_id = max(
        [task["id"] for task in data["task"]],
        default=0
    ) + 1

    new_task = {
        "id": new_id,
        "title": body["title"],
        "desc": body.get("desc", ""),
        "status": body.get("status", "À faire"),
        "assigned_to": body.get("assigned_to", ""),
        "tag": body.get("tag", "Development"),
        "urgent": body.get("urgent", False),
        "live": body.get("live", False),
        "info": body.get("info", ""),
        "infoIcon": body.get("infoIcon", ""),
    }

    data["task"].append(new_task)

    write_data(data)

    return jsonify(new_task), 201
  
# ----------------------------------
# Update Task
# ----------------------------------
@app.route("/task/<int:task_id>", methods=["PUT"])
def update_task(task_id):

    data = read_data()
    body = request.get_json()

    allowed_status = [
        "À faire",
        "En cours",
        "Terminé"
    ]

    for task in data["task"]:

        if task["id"] == task_id:

            if "title" in body:
                task["title"] = body["title"]

            if "assigned_to" in body:
                task["assigned_to"] = body["assigned_to"]

            if "desc" in body:
                task["desc"] = body["desc"]

            if "tag" in body:
                task["tag"] = body["tag"]

            if "urgent" in body:
                task["urgent"] = body["urgent"]

            if "live" in body:
                task["live"] = body["live"]

            if "info" in body:
                task["info"] = body["info"]

            if "infoIcon" in body:
                task["infoIcon"] = body["infoIcon"]

            if "status" in body:

                if body["status"] not in allowed_status:
                    return jsonify({
                        "error": "Invalid status"
                    }), 400

                task["status"] = body["status"]

            write_data(data)

            return jsonify(task)

    return jsonify({
        "error": "Task not found"
    }), 404

# ----------------------------------
# Delete Task
# ----------------------------------
@app.route("/task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    data = read_data()

    original_length = len(data["task"])

    data["task"] = [
        task for task in data["task"]
        if task["id"] != task_id
    ]

    if len(data["task"]) == original_length:
        return jsonify({
            "error": "Task not found"
        }), 404

    write_data(data)

    return jsonify({
        "message": "Task deleted successfully"
    }) 


# ----------------------------------
USERS_FILE = "users.json"

def read_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ----------------------------------

# ----------------------------------
@app.route("/login", methods=["POST"])
def login():

    body = request.get_json()

    username = body.get("username")
    password = body.get("password")

    users = read_users()["users"]

    for user in users:
        if (
            user["username"] == username and
            user["password"] == password
        ):
            return jsonify({
                "success": True,
                "message": "Login successful"
            })

    return jsonify({
        "success": False,
        "message": "Invalid username or password"
    }), 401

@app.route("/register", methods=["POST"])
def register():
    body = request.get_json()
    username = body.get("username")
    password = body.get("password")

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for user in data["users"]:
        if user["username"] == username:
            return jsonify({
                "success": False,
                "error": "User already exists"
            }), 400

    data["users"].append({
        "username": username,
        "password": password
    })

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return jsonify({
        "success": True,
        "message": "Registered successfully"
    }), 201

#
@app.route("/forgot-password-page")
def forgot_password_page():
    return render_template("forgot_password.html")

    
#foregt password
@app.route("/forgot-password", methods=["POST"])
def forgot_password():

    body = request.get_json()

    username = body.get("username")
    new_password = body.get("new_password")

    with open("users.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for user in data["users"]:

        if user["username"] == username:

            user["password"] = new_password

            with open("users.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            return jsonify({
                "message": "Password updated successfully"
            })

    return jsonify({
        "error": "User not found"
    }), 404

# ----------------------------------
@app.route("/api")     
def api_status():   
    return jsonify({
        "message": "TaskFlow API Running"
    })  
# ----------------------------------

#----------------------------------
@app.route("/mytasks")
def mytasks():
    return render_template("dashboard.html")
# ----------------------------------



# stats--  ------------------------------
@app.route("/stats")
def stats():

    data = read_data()

    total = len(data["task"])

    completed = len([
        t for t in data["task"]
        if t["status"] == "Terminé"
    ])

    progress = len([
        t for t in data["task"]
        if t["status"] == "En cours"
    ])

    return jsonify({
        "total": total,
        "completed": completed,
        "progress": progress
    })

#--------------------------------
# Get Members
@app.route("/members-data") # renamed to avoid conflict with /members which is a template route (though /members was overridden earlier in the file to render dashboard.html). Wait, the original code had both.
def get_members_data():
    with open("users.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    return jsonify(data)
#serch members
@app.route("/search")
def search_task():

    title = request.args.get("title", "")

    data = read_data()

    result = [
        task for task in data["task"]
        if title.lower() in task["title"].lower()
    ]

    return jsonify(result) 


# Run Server
# ----------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
