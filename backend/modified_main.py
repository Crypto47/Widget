from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from pymongo import MongoClient
from config import OpenaiApi, MongoDBConnection
import requests
import os
from fastapi.middleware.cors import CORSMiddleware

openai_client = OpenAI(api_key=OpenaiApi)



app = FastAPI()

class Message(BaseModel):
    content: str
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define Zapier webhook URLs
zapier_hooks = {
    "slack": "https://hooks.zapier.com/hooks/catch/your-slack-webhook-url/",
    "meeting": "Your Meeting has been Booked",
    "email": "https://hooks.zapier.com/hooks/catch/your-email-webhook-url/",
    "fetch": "https://hooks.zapier.com/hooks/catch/your-fetch-webhook-url/"
}

# Initialize the conversation history as a dictionary
history = {"user": [], "assistant": []}

# Checker function that uses OpenAI to detect intent and validate requirements
def checker(history):
    # Combine the entire conversation history into a single string
    full_conversation = "\n".join([f"{role}: {msg}" for role in history for msg in history[role]])

    # Use OpenAI to detect the intent and check if all requirements are satisfied
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """
                You are an assistant that checks the conversation history to identify intents and whether all required information is present for each intent. The possible intents are:
                - **Meeting**: Requires platform, time and date, email of recipient, and title of meeting.
                - **Slack**: Requires the name of the user you want to send a message to.
                - **Gmail**: Requires title, subject, and recipient email.
                - **Fetch**: Intent is `fetch`, no additional requirements.
                Identify the intent of the variable `history` that stores the whole conversation. If and only if the requirements are fulfilled and the intent is detected, then return the intent. Otherwise, return 'incomplete'.
            """},
            {"role": "user", "content": f"Here is the conversation: {full_conversation}."}
        ]
    )

    # Extract the intent from the response
    intent = response.choices[0].message.content.strip().lower()

    # Debug: Print the response
    print("Checker response:", response)

    # Check if the intent is valid and complete
    return intent if intent in zapier_hooks else "incomplete"


def trigger_zapier_webhook(intent, full_conversation, history):
    if intent in zapier_hooks:
        webhook_url = zapier_hooks[intent]
        payload = {
            "conversation": full_conversation,
            "full_convo": history
        }
        # Insert the history into MongoDB
        #collection.insert_one({"history": history})
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to trigger Zapier webhook for {intent}. Status code: {response.status_code}")
        return f"Triggered {intent} action via Zapier."
    else:
        return "No valid intent detected."

@app.post("/chat")
async def chat(message: Message):
    try:
        # Define the assistant's instructions
        assistant_instructions = (
            "You are a helpful assistant. Your role is to assist the user in whatever tasks they require, "
            "offering a seamless experience.\n\n"
            "1. **Scheduling a Meeting**: When the user requests to schedule a meeting, ask for the platform "
            "(e.g., Google Meet, Zoom), the date, the subject of the meeting, the time (using the user's time zone), and the email addresses of the recipients.\n\n"
            "2. **Sending a Message on Slack**: When the user wants to send a message via Slack, ask who they want to "
            "send it to and what the message should say.\n\n"
            "3. **Fetching Data**: When the user needs to fetch data, ask for the file name and type (e.g., .docx, .xlsx, .pdf).\n\n"
            "4. **Drafting an Email**: When the user wants to draft an email, ask for the topic and the recipient."
        )

        # Append the instructions as the assistant's first message
        history["assistant"].append(assistant_instructions)

        # Append the new message to the conversation history
        history["user"].append(message.content)

        # Call the checker function to determine the intent and if requirements are met
        intent = checker(history)

        if intent != "incomplete":
            # Trigger the Zapier webhook if the intent and requirements are satisfied
            response_text = trigger_zapier_webhook(intent, message.content, history)
        else:
            # Default behavior: Use OpenAI for general conversation or to gather more information
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": assistant_instructions},
                    {"role": "user", "content": message.content}
                ]
            )
            # Append the bot's response to the conversation history
            bot_response = response.choices[0].message.content.strip().lower()
            history["assistant"].append(bot_response)
            response_text = bot_response

        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
