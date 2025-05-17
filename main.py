"""Command line entry point for the project."""

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_functions import (
    format_to_openai_function_messages,
)
from langchain.agents.output_parsers.openai_functions import OpenAIFunctionsAgentOutputParser
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

# Define a custom tool
@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

def create_agent_executor():
    """Creates and returns a LangChain agent executor."""

    # Ensure API key is available
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")

    # Define the tools the agent can use
    tools = [get_word_length]
    
    # Convert tools to OpenAI function format
    llm_with_tools = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125").bind(
        functions=[convert_to_openai_function(t) for t in tools]
    )

    # Define the prompt template
    # Based on: https://python.langchain.com/docs/modules/agents/how_to/custom_agent_with_tool_retrieval
    # And: https://python.langchain.com/docs/modules/agents/how_to/function_calling
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # Create the agent runnable
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x.get("chat_history", []), # Handle optional chat_history
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

def main() -> None:
    """Run the application."""
    try:
        agent_executor = create_agent_executor()

        print("Agent created. You can now interact with it.")
        print("Type 'exit' to quit.")

        chat_history = []

        while True:
            user_input = input("Human: ")
            if user_input.lower() == "exit":
                break

            response = agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            
            print(f"Agent: {response['output']}")
            
            # Update chat history
            # Note: The format of chat_history might need adjustment based on how you want to store it
            # and how the specific agent/LLM expects it.
            # For OpenAI Functions agent, it typically expects a list of BaseMessage objects.
            # This is a simplified history update.
            chat_history.append(("human", user_input))
            chat_history.append(("ai", response["output"]))
            # Trim history to keep it manageable, e.g., last 10 messages
            if len(chat_history) > 10:
                chat_history = chat_history[-10:]


    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
