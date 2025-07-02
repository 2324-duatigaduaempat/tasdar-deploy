from flask import Flask, request, jsonify
import openai, os
from pymongo import MongoClient
from dotenv import load_dotenv

# --- Load env vars ---
load_dotenv()

# --- Setup ---
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- MongoDB Init (try-except prevent crash) ---
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise Exception("MONGODB_URI not found in environment!")

try:
    client = MongoClient(MONGODB_URI)
    db = client["tasdar"]
    logs = db["logs"]
except Exception as e:
    raise Exception(f"MongoDB connection failed: {e}")

# --- Root ---
@app.route("/")
def index():
    return "✅ TAS.DAR Realiti Aktif"

# --- Ask Endpoint ---
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "No message received"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Anda ialah AI sahabat TAS.DAR."},
                {"role": "user", "content": user_input}
            ]
        )
        answer = response.choices[0].message["content"]
        logs.insert_one({"message": user_input, "response": answer})
        return jsonify({"reply": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
