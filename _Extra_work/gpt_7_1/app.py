import os
import json
from pathlib import Path
import streamlit as st
from openai import OpenAI
from dotenv import dotenv_values
from cost_tracking import log_daily_cost, get_cost_summary, get_total_cost, reset_costs



model_pricings = {
    "gpt-4o": {
        "input_tokens": 5.00 / 1_000_000,  # per token
        "output_tokens": 15.00 / 1_000_000,  # per token
    },
    "gpt-4o-mini": {
        "input_tokens": 0.150 / 1_000_000,  # per token
        "output_tokens": 0.600 / 1_000_000,  # per token
    }
}
MODEL = "gpt-4o"
USD_TO_PLN = 3.69
PRICING = model_pricings[MODEL]

env = dotenv_values(".env")

openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])

#
# CHATBOT
#
def chatbot_reply(user_prompt, memory):
    # add system message
    messages = [
        {
            "role": "system",
            "content": st.session_state["chatbot_personality"],
        },
    ]
    # add all messages from memory
    for message in memory:
        messages.append({"role": message["role"], "content": message["content"]})

    # add user message
    messages.append({"role": "user", "content": user_prompt})

    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    usage = {}
    if response.usage:
        usage = {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "total_tokens": response.usage.total_tokens,
        }

    return {
        "role": "assistant",
        "content": response.choices[0].message.content,
        "usage": usage,
    }

#
# CONVERSATION HISTORY AND DATABASE
#
DEFAULT_PERSONALITY = """
You are a helper who answers all user questions.
Answer questions in a concise and understandable way.
""".strip()

DB_PATH = Path("db")
DB_CONVERSATIONS_PATH = DB_PATH / "conversations"
# db/
# ├── current.json
# ├── conversations/
# │   ├── 1.json
# │   ├── 2.json
# │   └── ...
def load_conversation_to_state(conversation):
    st.session_state["id"] = conversation["id"]
    st.session_state["name"] = conversation["name"]
    st.session_state["messages"] = conversation["messages"]
    st.session_state["chatbot_personality"] = conversation["chatbot_personality"]



def load_current_conversation():
    if not DB_PATH.exists():
        DB_PATH.mkdir()
        DB_CONVERSATIONS_PATH.mkdir()
        conversation_id = 1
        conversation = {
            "id": conversation_id,
            "name": "Conversation 1",
            "chatbot_personality": DEFAULT_PERSONALITY,
            "messages": [],
        }

        # create a new conversation
        with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w", encoding="utf-8") as f:
            json.dump(conversation, f)

        # which immediately becomes the current one
        with open(DB_PATH / "current.json", "w", encoding="utf-8") as f:
            json.dump({"current_conversation_id": conversation_id}, f)

    else:
        # check which conversation is current
        with open(DB_PATH / "current.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            conversation_id = data["current_conversation_id"]

        conversation_file = DB_CONVERSATIONS_PATH / f"{conversation_id}.json"
        if not conversation_file.exists():
            # If file doesn't exist – create empty conversation
            conversation = {
                "id": conversation_id,
                "name": f"Conversation {conversation_id}",
                "chatbot_personality": DEFAULT_PERSONALITY,
                "messages": [],
            }
            with open(conversation_file, "w", encoding="utf-8") as f:
                json.dump(conversation, f)
        else:
            # Load content only if it's not empty
            with open(conversation_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    # Empty file – overwrite with default structure
                    conversation = {
                        "id": conversation_id,
                        "name": f"Conversation {conversation_id}",
                        "chatbot_personality": DEFAULT_PERSONALITY,
                        "messages": [],
                    }
                    with open(conversation_file, "w", encoding="utf-8") as f_w:
                        json.dump(conversation, f_w)
                else:
                    conversation = json.loads(content)

    load_conversation_to_state(conversation)

















def save_current_conversation_messages():
    conversation_id = st.session_state["id"]
    new_messages = st.session_state["messages"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r", encoding="utf-8") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({
            **conversation,
            "messages": new_messages,
        }))


def save_current_conversation_name():
    conversation_id = st.session_state["id"]
    new_conversation_name = st.session_state["new_conversation_name"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r", encoding="utf-8") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({
            **conversation,
            "name": new_conversation_name,
        }))


def save_current_conversation_personality():
    conversation_id = st.session_state["id"]
    new_chatbot_personality = st.session_state["new_chatbot_personality"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r", encoding="utf-8") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({
            **conversation,
            "chatbot_personality": new_chatbot_personality,
        }))


def create_new_conversation():
    # find ID for our next conversation
    conversation_ids = []
    for p in DB_CONVERSATIONS_PATH.glob("*.json"):
        conversation_ids.append(int(p.stem))

    # conversation_ids contains all conversation IDs
    # next conversation will have ID 1 greater than the largest ID in the list
    conversation_id = max(conversation_ids) + 1
    personality = DEFAULT_PERSONALITY
    if "chatbot_personality" in st.session_state and st.session_state["chatbot_personality"]:
        personality = st.session_state["chatbot_personality"]

    conversation = {
        "id": conversation_id,
        "name": f"Conversation {conversation_id}",
        "chatbot_personality": personality,
        "messages": [],
    }

    # create a new conversation
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(conversation))

    # which immediately becomes the current one
    with open(DB_PATH / "current.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "current_conversation_id": conversation_id,
        }))

    load_conversation_to_state(conversation)
    st.rerun()


def switch_conversation(conversation_id):
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r", encoding="utf-8") as f:
        conversation = json.loads(f.read())

    with open(DB_PATH / "current.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "current_conversation_id": conversation_id,
        }))

    load_conversation_to_state(conversation)
    st.rerun()


def list_conversations():
    conversations = []
    for p in DB_CONVERSATIONS_PATH.glob("*.json"):
        with open(p, "r", encoding="utf-8") as f:
            conversation = json.loads(f.read())
            conversations.append({
                "id": conversation["id"],
                "name": conversation["name"],
            })

    return conversations


#
# MAIN PROGRAM
#
load_current_conversation()

st.title(":classical_building: OurGPT")

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("What would you like to ask?")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = chatbot_reply(prompt, memory=st.session_state["messages"][-20:])
        st.markdown(response["content"])

    st.session_state["messages"].append({"role": "assistant", "content": response["content"], "usage": response["usage"]})
    log_daily_cost(
        response["usage"]["prompt_tokens"] * PRICING["input_tokens"]
        + response["usage"]["completion_tokens"] * PRICING["output_tokens"]
    )
    save_current_conversation_messages()

with st.sidebar:
    # 1. Model at the top
    st.write("### Current model", MODEL)

    
    # 2. Costs (USD / PLN)
    total_cost = 0
    for message in st.session_state.get("messages") or []:
        if "usage" in message:
            total_cost += message["usage"]["prompt_tokens"] * PRICING["input_tokens"]
            total_cost += message["usage"]["completion_tokens"] * PRICING["output_tokens"]

    c0, c1 = st.columns(2)
    with c0:
        st.metric("Conversation cost (USD)", f"${total_cost:.4f}")

    with c1:
        st.metric("Conversation cost (PLN)", f"{total_cost * USD_TO_PLN:.4f}")

        # Total cost from the beginning
    total_all_time = get_total_cost()
    st.markdown(f"**Total conversation cost:**\n\n`${total_all_time:.4f}` USD / `{total_all_time * USD_TO_PLN:.2f}` PLN")
 
        
    
    # Expandable cost history for 60 days
    with st.expander("Show cost history (Max 60 days)"):
        cost_history = get_cost_summary(days=60)
        if not cost_history:
            st.write("No data.")
        else:
            for date_str, cost_usd in cost_history.items():
                st.write(f"{date_str}: ${cost_usd:.4f} / {cost_usd * USD_TO_PLN:.2f} PLN")



    # 3. Conversation settings
    # st.subheader("Current conversation")
    st.session_state["name"] = st.text_input(
        "Conversation name (Press Enter to apply)",
        value=st.session_state["name"],
        key="new_conversation_name",
        on_change=save_current_conversation_name,
    )
    st.session_state["chatbot_personality"] = st.text_area(
        "Chatbot personality (Press Ctrl+Enter to apply)",
        max_chars=1000,
        height=200,
        value=st.session_state["chatbot_personality"],
        key="new_chatbot_personality",
        on_change=save_current_conversation_personality,
    )

    st.subheader("Conversations")
    if st.button("New conversation"):
        create_new_conversation()

    # show only top 5 conversations
    # conversations = list_conversations()
    # sorted_conversations = sorted(conversations, key=lambda x: x["id"], reverse=True)
    # for conversation in sorted_conversations[:5]:
    #    c0, c1 = st.columns([10, 3])
    #    with c0:
    #       st.write(conversation["name"])
    #    with c1:
    #        if st.button("load", key=conversation["id"], disabled=conversation["id"] == st.session_state["id"]):
    #            switch_conversation(conversation["id"])
   
    # show all conversations in expandable section
    conversations = list_conversations()
    sorted_conversations = sorted(conversations, key=lambda x: x["id"], reverse=True)

    with st.expander("Conversation list"):
        for conversation in sorted_conversations:
            c0, c1 = st.columns([10, 3])
            with c0:
                st.write(conversation["name"])
            with c1:
                if st.button("load", key=conversation["id"], disabled=conversation["id"] == st.session_state["id"]):
                    switch_conversation(conversation["id"])



    st.divider()  # optional separator line

    if st.button("Reset history"):
        reset_costs()
        st.session_state["messages"] = []
        save_current_conversation_messages()
        st.rerun()
