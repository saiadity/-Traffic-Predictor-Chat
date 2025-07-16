from flask import Blueprint, request, jsonify
from flask_cors import CORS
from app.traffic_logic import handle_user_query

api = Blueprint("api", __name__)
CORS(api)  # ✅ Allow CORS for frontend access

@api.route("/predict", methods=["POST"])
def predict_traffic():
    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    user_question = data["question"]

    try:
        response = handle_user_query(user_question)
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
