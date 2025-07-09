import os
from typing import Any, Dict

from haystack.components.agents import Agent
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.tools import ComponentTool
from haystack_integrations.components.generators.google_genai import (
    GoogleGenAIChatGenerator,
)

from app.adapter.agents.sql_query import SQLQuery
from app.domain.chat.prompt import prompt_template

# Initialize the LLM
# Make sure the GOOGLE_API_KEY environment variable is set.
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError(
        "Please set the GOOGLE_API_KEY environment variable in your .env file."
    )
llm = GoogleGenAIChatGenerator(model="gemini-2.5-flash")

# Create the SQLQuery component and wrap it in a tool for the agent
sql_query_tool = ComponentTool(
    component=SQLQuery(),
    name="sql_query",
    description="Runs a SQL query against the database and returns the result as a string.",
)

# Create the agent
sql_agent = Agent(
    chat_generator=llm,
    system_prompt=prompt_template,
    tools=[sql_query_tool],
    streaming_callback=print_streaming_chunk,
    exit_conditions=["text"],
)


def ask(question: str) -> Dict[str, Any]:
    """
    Asks a question to the SQL agent.

    Args:
        question: The question to ask in natural language.

    Returns:
        The agent's response as a string.
    """
    return sql_agent.run(messages=[ChatMessage.from_user(question)])
