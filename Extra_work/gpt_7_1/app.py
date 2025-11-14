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
    # dodaj system message
    messages = [
        {
            "role": "system",
            "content": st.session_state["chatbot_personality"],
        },
    ]
    # dodaj wszystkie wiadomości z pamięci
    for message in memory:
        messages.append({"role": message["role"], "content": message["content"]})

    # dodaj wiadomość użytkownika
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
Jesteś pomocnikiem, który odpowiada na wszystkie pytania użytkownika.
Odpowiadaj na pytania w sposób zwięzły i zrozumiały.
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
            "name": "Konwersacja 1",
            "chatbot_personality": DEFAULT_PERSONALITY,
            "messages": [],
        }

        # tworzymy nową konwersację
        with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w", encoding="utf-8") as f:
            json.dump(conversation, f)

        # która od razu staje się aktualną
        with open(DB_PATH / "current.json", "w", encoding="utf-8") as f:
            json.dump({"current_conversation_id": conversation_id}, f)

    else:
        # sprawdzamy, która konwersacja jest aktualna
        with open(DB_PATH / "current.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            conversation_id = data["current_conversation_id"]

        conversation_file = DB_CONVERSATIONS_PATH / f"{conversation_id}.json"
        if not conversation_file.exists():
            # Jeśli plik nie istnieje – utwórz pustą konwersację
            conversation = {
                "id": conversation_id,
                "name": f"Konwersacja {conversation_id}",
                "chatbot_personality": DEFAULT_PERSONALITY,
                "messages": [],
            }
            with open(conversation_file, "w", encoding="utf-8") as f:
                json.dump(conversation, f)
        else:
            # Wczytaj zawartość tylko jeśli nie jest pusta
            with open(conversation_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    # Plik pusty – nadpisz domyślną strukturą
                    conversation = {
                        "id": conversation_id,
                        "name": f"Konwersacja {conversation_id}",
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

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps({
            **conversation,
            "messages": new_messages,
        }))


def save_current_conversation_name():
    conversation_id = st.session_state["id"]
    new_conversation_name = st.session_state["new_conversation_name"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps({
            **conversation,
            "name": new_conversation_name,
        }))


def save_current_conversation_personality():
    conversation_id = st.session_state["id"]
    new_chatbot_personality = st.session_state["new_chatbot_personality"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps({
            **conversation,
            "chatbot_personality": new_chatbot_personality,
        }))


def create_new_conversation():
    # poszukajmy ID dla naszej kolejnej konwersacji
    conversation_ids = []
    for p in DB_CONVERSATIONS_PATH.glob("*.json"):
        conversation_ids.append(int(p.stem))

    # conversation_ids zawiera wszystkie ID konwersacji
    # następna konwersacja będzie miała ID o 1 większe niż największe ID z listy
    conversation_id = max(conversation_ids) + 1
    personality = DEFAULT_PERSONALITY
    if "chatbot_personality" in st.session_state and st.session_state["chatbot_personality"]:
        personality = st.session_state["chatbot_personality"]

    conversation = {
        "id": conversation_id,
        "name": f"Konwersacja {conversation_id}",
        "chatbot_personality": personality,
        "messages": [],
    }

    # tworzymy nową konwersację
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps(conversation))

    # która od razu staje się aktualną
    with open(DB_PATH / "current.json", "w") as f:
        f.write(json.dumps({
            "current_conversation_id": conversation_id,
        }))

    load_conversation_to_state(conversation)
    st.rerun()


def switch_conversation(conversation_id):
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_PATH / "current.json", "w") as f:
        f.write(json.dumps({
            "current_conversation_id": conversation_id,
        }))

    load_conversation_to_state(conversation)
    st.rerun()


def list_conversations():
    conversations = []
    for p in DB_CONVERSATIONS_PATH.glob("*.json"):
        with open(p, "r") as f:
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

st.title(":classical_building: NaszGPT")

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("O co chcesz spytać?")
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
    # 1. Model na górze
    st.write("### Aktualny model", MODEL)

    
    # 2. Koszty (USD / PLN)
    total_cost = 0
    for message in st.session_state.get("messages") or []:
        if "usage" in message:
            total_cost += message["usage"]["prompt_tokens"] * PRICING["input_tokens"]
            total_cost += message["usage"]["completion_tokens"] * PRICING["output_tokens"]

    c0, c1 = st.columns(2)
    with c0:
        st.metric("Koszt rozmowy (USD)", f"${total_cost:.4f}")

    with c1:
        st.metric("Koszt rozmowy (PLN)", f"{total_cost * USD_TO_PLN:.4f}")

        # Całkowity koszt od początku
    total_all_time = get_total_cost()
    st.markdown(f"**Całkowity koszt rozmów:**\n\n`${total_all_time:.4f}` USD / `{total_all_time * USD_TO_PLN:.2f}` PLN")
 
         
    
    # Rozwijana historia kosztów z 60 dni
    with st.expander("Pokaż historię kosztów (Max 60 dni)"):
        cost_history = get_cost_summary(days=60)
        if not cost_history:
            st.write("Brak danych.")
        else:
            for date_str, cost_usd in cost_history.items():
                st.write(f"{date_str}: ${cost_usd:.4f} / {cost_usd * USD_TO_PLN:.2f} PLN")



    # 3. Ustawienia konwersacji
    # st.subheader("Aktualna konwersacja")
    st.session_state["name"] = st.text_input(
        "Nazwa konwersacji (Press Enter to apply)",
        value=st.session_state["name"],
        key="new_conversation_name",
        on_change=save_current_conversation_name,
    )
    st.session_state["chatbot_personality"] = st.text_area(
        "Osobowość chatbota (Press Ctrl+Enter to apply)",
        max_chars=1000,
        height=200,
        value=st.session_state["chatbot_personality"],
        key="new_chatbot_personality",
        on_change=save_current_conversation_personality,
    )

    st.subheader("Konwersacje")
    if st.button("Nowa konwersacja"):
        create_new_conversation()

    # pokazujemy tylko top 5 konwersacji
    # conversations = list_conversations()
    # sorted_conversations = sorted(conversations, key=lambda x: x["id"], reverse=True)
    # for conversation in sorted_conversations[:5]:
    #    c0, c1 = st.columns([10, 3])
    #    with c0:
    #       st.write(conversation["name"])
    #    with c1:
    #        if st.button("załaduj", key=conversation["id"], disabled=conversation["id"] == st.session_state["id"]):
    #            switch_conversation(conversation["id"])
   
    # pokaż wszystkie konwersacje w rozwijanej sekcji
    conversations = list_conversations()
    sorted_conversations = sorted(conversations, key=lambda x: x["id"], reverse=True)

    with st.expander("Lista konwersacji"):
        for conversation in sorted_conversations:
            c0, c1 = st.columns([10, 3])
            with c0:
                st.write(conversation["name"])
            with c1:
                if st.button("załaduj", key=conversation["id"], disabled=conversation["id"] == st.session_state["id"]):
                    switch_conversation(conversation["id"])



    st.divider()  # opcjonalna linia oddzielająca

    if st.button("Resetuj historię"):
        reset_costs()
        st.session_state["messages"] = []
        save_current_conversation_messages()
        st.rerun()
