from sqlalchemy import inspect

from app.adapter.database.connection import engine

def get_database_schema() -> str:
    """
    Connects to the database and extracts schema information.

    Returns:
        A string containing the schema of the database.
    """
    inspector = inspect(engine)
    schema_info = []
    for table_name in inspector.get_table_names():
        schema_info.append(f"Table: {table_name}")
        columns = inspector.get_columns(table_name)
        for column in columns:
            schema_info.append(f"  - {column['name']}: {column['type']}")
    return "\n".join(schema_info)


# Get the database schema
db_schema = get_database_schema()

# Define the prompt template for the agent
# This prompt guides the LLM to generate SQL queries from natural language
# or to explain why a question cannot be answered.
prompt_template = f"""
You are a helpful agent that can answer questions by querying a PostgreSQL database.

Given the chat history and the user's question, you must decide whether to use a tool or not.

Use the tools that you're provided with to get information. Don't use your own knowledge.

The database has the following schema:
{db_schema}

If the user's question can be answered by querying the database, you must use the `sql_query` tool.
The `sql_query` tool takes a single argument: a valid PostgreSQL query.

If the question cannot be answered using the database, you must reply that you cannot answer the question and explain why, based on the available schema.
"""
