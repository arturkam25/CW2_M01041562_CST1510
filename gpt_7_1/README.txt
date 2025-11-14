Project Description

The gpt_7_1 project is a Streamlit-based application that provides an interactive chatbot powered by the OpenAI API.
Its purpose is to simulate conversational interactions, maintain conversation history, and track token usage and daily costs associated with API calls.

The application is designed for learning purposes and operates only with the sample logic included in this project.

Main Features

Chatbot interface built with Streamlit

Persistent conversation history stored in JSON files

Ability to create, switch, rename and personalise conversations

Tracking of:

prompt tokens

completion tokens

total cost in USD and PLN

daily usage summary

Sidebar view with:

current model

cost breakdown

conversation settings

list of all conversations

Requirements

To run this application, you need:

Python 3.10 or higher

An OpenAI API key

Required dependencies:

streamlit
openai
python-dotenv


Install them with:
pip install streamlit openai python-dotenv

Important Note
The .env file should contain your OpenAI API key:
OPENAI_API_KEY=your_key_here
This file must NOT be included in the repository.

How to Run the Application
Place your API key inside the .env file
Open a terminal in the project folder (where app.py is located)

Start the application:
streamlit run app.py
The interface will open in your browser at:
http://localhost:8501
