import logging
from typing import Any

import streamlit as st
from haystack.dataclasses import ChatMessage

from app.domain.chat.agent import ask

logging.basicConfig(
    format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


st.title("SQL Chatbot")


def main():
    st.chat_message("assistant").write("Ask a question about your database:")

    # Text input for the user's question
    user_question = st.chat_input("Your question")

    if user_question and user_question.strip():
        with st.spinner("Thinking..."):
            try:
                response = ask(user_question)
                logger.info(f"Response: {response}")
                # Safely extract the answer from the response dictionary
                message: Any = response.get("last_message")
                if (
                    message
                    and hasattr(message, "text")
                    and isinstance(message, ChatMessage)
                ):
                    answer = message.text
                else:
                    answer = "Sorry, I couldn't understand the response."
                st.chat_message("user").write(user_question)
                st.chat_message("assistant").write(answer)
            except Exception as e:
                st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
