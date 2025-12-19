# ==============================================================================
# AI ASSISTANT – AUTHENTICATED CHAT INTERFACE
# ==============================================================================

# This Streamlit page provides an authenticated AI chat assistant
# integrated with the OpenAI API.

# Scope of responsibility:
# - provide a conversational AI interface for logged-in users
# - persist chat history per user
# - restore conversation context between sessions
# - limit context size for performance and cost control

# Access control:
# - page is accessible only to authenticated users
# - each user sees only their own chat history

# Architectural role:
# - UI interaction layer
# - consumer of the OpenAI API
# - integrates with internal chat history persistence service

# Design considerations:
# - per-user session isolation
# - controlled message window (MAX_MESSAGES)
# - no sensitive system data exposed to the model
# - assistant behaviour constrained to coursework support
# - supports both text and image inputs for enhanced analysis

import streamlit as st
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image

# ==============================================================================
# DEPENDENCIES AND ACCESS CONTROL
# ==============================================================================

# Import authentication guard.
from app.utils.auth import require_login

# Import navigation utilities.
from app.utils.navigation import hide_default_streamlit_menu, render_navigation_sidebar

# Import chat history persistence layer.
from app.services.chat_history import (
    load_chat_history,
    save_chat_history,
    clear_chat_history
)

# ==============================================================================
# CONFIGURATION CONSTANTS
# ==============================================================================

# Maximum number of messages kept in memory and sent to the model.
# This limits:
# - token usage
# - latency
# - API cost
MAX_MESSAGES = 20

# OpenAI model configuration for vision support.
# Using gpt-4o for multimodal capabilities (text and images).
MODEL_NAME = "gpt-4o"

# ==============================================================================
# AUTHENTICATION AND NAVIGATION SETUP
# ==============================================================================

# Enforce authentication before any session logic.
user = require_login()
# Hide default Streamlit navigation to maintain a controlled UI.
hide_default_streamlit_menu()
# Render application-specific sidebar navigation.
render_navigation_sidebar()

# ==============================================================================
# SESSION STATE INITIALISATION (PER USER)
# ==============================================================================

# Chat history is stored per user.
# If the session is new or the logged-in user has changed,
# load chat history from persistent storage.
if (
    "chat_history" not in st.session_state
    or st.session_state.get("chat_user_id") != user["id"]
):
    st.session_state.chat_user_id = user["id"]
    st.session_state.chat_history = load_chat_history(user["id"])

# ==============================================================================
# PAGE HEADER
# ==============================================================================

st.title("🤖 AI Assistant")
st.caption(f"Logged in as: {user['username']}")

# ==============================================================================
# OPENAI CLIENT INITIALISATION
# ==============================================================================

# Create OpenAI client using API key stored securely in Streamlit secrets.
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# ==============================================================================
# IMAGE PROCESSING UTILITIES
# ==============================================================================

# This section provides helper functions for handling image inputs
# and converting them to formats compatible with the OpenAI API.

def encode_image_to_base64(image_file) -> str:
    # Converts an uploaded image file to base64-encoded string.
    #
    # Parameters:
    # - image_file: Streamlit UploadedFile object containing image data
    #
    # Returns:
    # - base64-encoded string with data URI prefix for OpenAI API
    image_bytes = image_file.read()
    base64_string = base64.b64encode(image_bytes).decode("utf-8")
    
    # Determine MIME type from file extension
    mime_type = "image/jpeg"
    if image_file.type:
        mime_type = image_file.type
    elif image_file.name:
        ext = image_file.name.lower().split(".")[-1]
        mime_map = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp"
        }
        mime_type = mime_map.get(ext, "image/jpeg")
    
    return f"data:{mime_type};base64,{base64_string}"

def prepare_message_content(text: str = None, images: list = None) -> list:
    # Prepares message content in OpenAI API format.
    #
    # The OpenAI API expects messages with images to have content as a list
    # of content blocks, where each block is either text or an image.
    #
    # Parameters:
    # - text: optional text content for the message
    # - images: optional list of base64-encoded image strings
    #
    # Returns:
    # - list of content blocks compatible with OpenAI API format
    content_blocks = []
    
    if text:
        content_blocks.append({
            "type": "text",
            "text": text
        })
    
    if images:
        for image_data in images:
            content_blocks.append({
                "type": "image_url",
                "image_url": {
                    "url": image_data
                }
            })
    
    # If no content provided, return empty text block
    if not content_blocks:
        content_blocks.append({
            "type": "text",
            "text": ""
        })
    
    return content_blocks

# ==============================================================================
# RENDER EXISTING CHAT HISTORY
# ==============================================================================

# Replay previous messages so the conversation
# feels continuous to the user.
# Supports both legacy text-only format and new multimodal format.
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        # Handle legacy format (simple string content)
        if isinstance(msg.get("content"), str):
            st.markdown(msg["content"])
        # Handle new multimodal format (list of content blocks)
        elif isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if block.get("type") == "text":
                    if block.get("text"):
                        st.markdown(block["text"])
                elif block.get("type") == "image_url":
                    # Extract base64 data from data URI
                    image_url = block.get("image_url", {}).get("url", "")
                    if image_url.startswith("data:image"):
                        # Decode and display image
                        try:
                            header, encoded = image_url.split(",", 1)
                            image_data = base64.b64decode(encoded)
                            image = Image.open(BytesIO(image_data))
                            st.image(image, use_container_width=True)
                        except Exception:
                            st.error("Failed to display image from history")
        else:
            # Fallback for unexpected formats
            st.markdown(str(msg.get("content", "")))

# ==============================================================================
# USER INPUT HANDLING
# ==============================================================================

# Image uploader for multimodal input support.
# Allows users to upload images alongside or instead of text prompts.
uploaded_images = st.file_uploader(
    "Upload images (optional)",
    type=["png", "jpg", "jpeg", "gif", "webp"],
    accept_multiple_files=True,
    help="You can upload images to analyze charts, diagrams, or data visualizations."
)

# Chat input field for user prompts.
prompt = st.chat_input("Ask me anything...")

# Process user input when either text or images are provided.
if prompt or (uploaded_images and len(uploaded_images) > 0):
    # Prepare image data if images were uploaded.
    image_data_list = []
    if uploaded_images:
        for img_file in uploaded_images:
            try:
                encoded_image = encode_image_to_base64(img_file)
                image_data_list.append(encoded_image)
            except Exception as e:
                st.error(f"Failed to process image {img_file.name}: {str(e)}")
                continue
    
    # Prepare message content in OpenAI API format.
    # Include text only if provided, images only if uploaded.
    user_text = prompt.strip() if prompt and prompt.strip() else None
    message_content = prepare_message_content(
        text=user_text,
        images=image_data_list if image_data_list else None
    )
    
    # Create user message for API (using OpenAI format).
    user_message_for_api = {
        "role": "user",
        "content": message_content
    }
    
    # Store in history (using OpenAI format for consistency).
    st.session_state.chat_history.append(user_message_for_api)
    
    # Display user message immediately with images if present.
    with st.chat_message("user"):
        if user_text:
            st.markdown(user_text)
        if image_data_list:
            for img_data in image_data_list:
                try:
                    # Extract and display image
                    header, encoded = img_data.split(",", 1)
                    image_bytes = base64.b64decode(encoded)
                    image = Image.open(BytesIO(image_bytes))
                    st.image(image, use_container_width=True)
                except Exception:
                    st.error("Failed to display uploaded image")
    
    # Generate assistant response using multimodal model.
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare messages for API, converting legacy format if needed.
            api_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for a university "
                        "coursework project. You can analyze images, charts, "
                        "diagrams, and data visualizations to help students "
                        "understand their project data and results."
                    )
                }
            ]
            
            # Convert chat history to API format, handling both legacy and new formats.
            for msg in st.session_state.chat_history[-MAX_MESSAGES:]:
                if isinstance(msg.get("content"), str):
                    # Legacy format: convert to new format
                    api_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                else:
                    # New format: use as-is
                    api_messages.append(msg)
            
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=api_messages
                )
                
                reply = response.choices[0].message.content
                st.markdown(reply)
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                st.error(error_msg)
                reply = error_msg
    
    # Append assistant response to session history.
    # Assistant responses are always text-only in current implementation.
    st.session_state.chat_history.append(
        {"role": "assistant", "content": reply}
    )
    
    # Enforce maximum message limit to control context size.
    if len(st.session_state.chat_history) > MAX_MESSAGES:
        st.session_state.chat_history = (
            st.session_state.chat_history[-MAX_MESSAGES:]
        )
    
    # Persist updated chat history to disk.
    save_chat_history(
        user["id"],
        st.session_state.chat_history
    )
