from flask import Flask, request, jsonify
import openai
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

# Check if keys are loaded
if not openai.api_key:
    raise Exception("OPENAI_API_KEY not found in environment")
if not mongo_uri:
    raise Exception("MONGODB_URI not found in environment")

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["tasdar"]
logs = db["logs"]

# Root route
@app.route("/")
def index():
    return "TAS.DAR Realiti Aktif", 200

# Ask GPT
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Anda ialah AI sahabat TAS.DAR, bertindak dengan reflektif dan mesra."},
                {"role": "user", "content": user_input}
            ]
        )
        answer = response.choices[0].message["content"]
        logs.insert_one({"message": user_input, "response": answer})
        return jsonify({"reply": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Launch
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
