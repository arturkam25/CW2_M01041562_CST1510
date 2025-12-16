import streamlit as st
from openai import OpenAI

from app.utils.auth import require_login
from app.utils.navigation import hide_default_streamlit_menu, render_navigation_sidebar
from app.services.chat_history import load_chat_history, save_chat_history

# ===== AUTH =====
user = require_login()

# Hide default Streamlit menu
hide_default_streamlit_menu()

# Render custom sidebar
render_navigation_sidebar()

st.title("🤖 AI Assistant")
st.caption(f"Logged in as: {user['username']}")

# ===== OpenAI client =====
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# ===== Session state (PER USER, SAFE) =====
if (
    "chat_history" not in st.session_state
    or st.session_state.get("chat_user_id") != user["id"]
):
    st.session_state.chat_user_id = user["id"]
    st.session_state.chat_history = load_chat_history(user["id"])


# ===== Display history =====
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===== Input =====
prompt = st.chat_input("Ask me anything...")

if prompt:
    # user message
    st.session_state.chat_history.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for a university coursework project."
                    },
                    *st.session_state.chat_history
                ]
            )

            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state.chat_history.append(
        {"role": "assistant", "content": reply}
    )

    # ===== SAVE HISTORY PER USER =====
    save_chat_history(user["id"], st.session_state.chat_history)
