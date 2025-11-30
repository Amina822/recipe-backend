from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # allow frontend access

DATA_FILE = "recipes.json"
USERS_FILE = "users.json"

# ------------- Helper functions -----------------

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ------------- Recipes API -----------------------

@app.route("/recipes", methods=["GET"])
def get_recipes():
    return jsonify(load_json(DATA_FILE))

@app.route("/recipes", methods=["POST"])
def add_recipe():
    recipes = load_json(DATA_FILE)
    new_recipe = request.json
    recipes.insert(0, new_recipe)
    save_json(DATA_FILE, recipes)
    return jsonify({"status": "ok"}), 201

@app.route("/recipes/<int:rid>", methods=["PUT"])
def edit_recipe(rid):
    recipes = load_json(DATA_FILE)
    for r in recipes:
        if r["id"] == rid:
            r.update(request.json)
            break
    save_json(DATA_FILE, recipes)
    return jsonify({"status": "updated"})

@app.route("/recipes/<int:rid>", methods=["DELETE"])
def delete_recipe(rid):
    recipes = load_json(DATA_FILE)
    recipes = [r for r in recipes if r["id"] != rid]
    save_json(DATA_FILE, recipes)
    return jsonify({"status": "deleted"})

@app.route("/recipes/<int:rid>/like", methods=["POST"])
def toggle_like(rid):
    recipes = load_json(DATA_FILE)
    for r in recipes:
        if r["id"] == rid:
            r["likes"] = request.json.get("likes", r["likes"])
            break
    save_json(DATA_FILE, recipes)
    return jsonify({"status": "like-updated"})

# ------------- User Login/Register ---------------

@app.route("/register", methods=["POST"])
def register():
    users = load_json(USERS_FILE)
    new_user = request.json

    if any(u["username"] == new_user["username"] for u in users):
        return jsonify({"error": "User exists"}), 400

    users.append(new_user)
    save_json(USERS_FILE, users)
    return jsonify({"status": "registered"})

@app.route("/login", methods=["POST"])
def login():
    users = load_json(USERS_FILE)
    data = request.json
    for u in users:
        if u["username"] == data["username"] and u["password"] == data["password"]:
            return jsonify({"status": "ok", "user": u})
    return jsonify({"error": "Invalid credentials"}), 401

# ------------- Run Server ------------------------

if __name__ == "__main__":
    app.run(debug=True)
