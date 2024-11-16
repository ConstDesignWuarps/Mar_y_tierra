from flask import render_template, Blueprint, request, jsonify
from mar_tierra import db
from mar_tierra.models import Visit
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI and GROQ API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the ChatGroq LLM
from langchain_groq import ChatGroq

llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Flask Blueprint
main = Blueprint("main", __name__)


# Home Route
@main.route("/")
@main.route("/home")
def home():
    ip_address = request.remote_addr
    visit = Visit.query.filter_by(ip_address=ip_address).first()

    if visit:
        visit.visit_count += 1
    else:
        visit = Visit(ip_address=ip_address, visit_count=1, consent_given=False)
        db.session.add(visit)

    db.session.commit()  # Save visit updates
    return render_template("main/home.html", ip_address=ip_address, consent_given=visit.consent_given)


# Chat Route
@main.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint with simplified logic."""
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please provide a message."}), 400

    try:
        # Handle greetings
        greeting_keywords = ["hi", "hello", "hey", "greetings"]
        if any(keyword in user_message.lower() for keyword in greeting_keywords):
            return jsonify({
                               "response": "Hey there! I can help with construction estimates, contacts, or general inquiries. What do you need assistance with?"})

        # Handle specific tasks
        if "estimate" in user_message.lower():
            return jsonify({
                               "response": "I can help you with construction cost estimates. Please refer to https://wuarpsconstructiondesign.com/home#?"})
        if "contact" in user_message.lower():
            return jsonify({
                               "response": "For further assistance, you can reach out to our construction specialists at wuarpsdesigns@gmail.com."})

        # General questions forwarded to LLM
        llm_input = [{"role": "user", "content": user_message}]
        print("LLM Input:", llm_input)  # Debugging log

        # Query the LLM
        response = llm.generate(llm_input)
        print("LLM Response:", response)  # Debugging log

        # Parse the LLM response
        bot_reply = response.generations[0].text.strip()
        return jsonify({"response": bot_reply})

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({
            "response": "Sorry, an error occurred while processing your request.",
            "error": str(e)
        }), 500
