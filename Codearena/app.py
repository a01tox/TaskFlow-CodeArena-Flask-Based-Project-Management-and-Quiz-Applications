from flask import Flask, jsonify, request, render_template, send_from_directory, redirect
import json
import os

app = Flask(__name__)

CODEARENA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "codearena")

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

# ----------------------------------
# CodeArena
# ----------------------------------
@app.route("/")
def home():
    return redirect("/codearena/app")

@app.route("/codearena")
def codearena_root():
    return redirect("/codearena/app")

@app.route("/codearena/app")
@app.route("/codearena/app/")
def codearena_app():
    return send_from_directory(CODEARENA_DIR, "codearena-app.html")

@app.route("/codearena/auth")
def codearena_auth():
    return send_from_directory(CODEARENA_DIR, "codearena-auth.html")

@app.route("/quiz")
def quiz():
    return redirect("/codearena/app")

# ----------------------------------
# Read Quiz Questions

QUESTIONS_FILE = "questions.json"

def read_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

#----------------------------------
# Get Quiz Questions
# ----------------------------------
@app.route("/questions", methods=["GET"])
def get_questions():
    return jsonify(read_questions())

# ----------------------------------
# Submit Quiz & Calculate Score
# ----------------------------------
@app.route("/submit", methods=["POST"])
def submit_quiz():

    user_answers = request.get_json()

    questions_data = read_questions()
    questions = questions_data["questions"]

    score = 0

    for question in questions:

        qid = str(question["id"])

        if qid in user_answers:

            if user_answers[qid] == question["answer"]:
                score += 1

    return jsonify({
        "score": score,
        "total": len(questions)
    })
    
# ----------------------------------
@app.route("/questions/<difficulty>")
def get_questions_by_difficulty(difficulty):

    data = read_questions()

    filtered = [
        q for q in data["questions"]
        if q["difficulty"] == difficulty
    ]

    return jsonify(filtered) 

# ----------------------------------
@app.route("/api")     
def api_status():   
    return jsonify({
        "message": "CodeArena API Running"
    })  

# ----------------------------------
# User Auth
# ----------------------------------
USERS_FILE = "users.json"

def read_users():
    if not os.path.exists(USERS_FILE):
        return {"users": []}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    username = body.get("username")
    password = body.get("password")

    users_data = read_users()
    for user in users_data.get("users", []):
        if user.get("username") == username and user.get("password") == password:
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

    data = read_users()

    for user in data.get("users", []):
        if user.get("username") == username:
            return jsonify({
                "success": False,
                "error": "User already exists"
            }), 400

    if "users" not in data:
        data["users"] = []

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

# Run Server
# ----------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
