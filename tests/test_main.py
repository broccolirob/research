import os
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

# Create minimal stub modules required by ``main`` to avoid heavy dependencies.
stubs = {}

class DummyPipe:
    def __or__(self, other):
        return DummyPipe()

    def __ror__(self, other):
        return DummyPipe()

prompts = ModuleType("prompts")

class ChatPromptTemplate:
    @classmethod
    def from_messages(cls, messages):
        return DummyPipe()


class MessagesPlaceholder:
    def __init__(self, *args, **kwargs):
        pass


prompts.ChatPromptTemplate = ChatPromptTemplate
prompts.MessagesPlaceholder = MessagesPlaceholder
stubs["langchain_core.prompts"] = prompts

fc = ModuleType("function_calling")

def convert_to_openai_function(t):
    return t


fc.convert_to_openai_function = convert_to_openai_function
stubs["langchain_core.utils.function_calling"] = fc

tools = ModuleType("tools")

def tool(func):
    return func


tools.tool = tool
stubs["langchain_core.tools"] = tools

openai_mod = ModuleType("langchain_openai")

class DummyChatOpenAI:
    def __init__(self, *args, **kwargs):
        pass

    def bind(self, *args, **kwargs):
        return DummyPipe()


openai_mod.ChatOpenAI = DummyChatOpenAI
stubs["langchain_openai"] = openai_mod

agents_pkg = ModuleType("langchain.agents")

class AgentExecutor:
    def __init__(self, agent=None, tools=None, verbose=None):
        pass


agents_pkg.AgentExecutor = AgentExecutor
stubs["langchain.agents"] = agents_pkg

fs_pkg = ModuleType("fs")

def format_to_openai_function_messages(x):
    return []


fs_pkg.format_to_openai_function_messages = format_to_openai_function_messages
stubs["langchain.agents.format_scratchpad.openai_functions"] = fs_pkg

op_pkg = ModuleType("op")

class OpenAIFunctionsAgentOutputParser:
    def __or__(self, other):
        return DummyPipe()

    def __ror__(self, other):
        return DummyPipe()


op_pkg.OpenAIFunctionsAgentOutputParser = OpenAIFunctionsAgentOutputParser
stubs["langchain.agents.output_parsers.openai_functions"] = op_pkg

sys.modules.update(stubs)

import main


def test_get_word_length():
    assert main.get_word_length("hello") == 5


def test_create_agent_executor_requires_key():
    with patch.dict(os.environ, {}, clear=True):
        try:
            main.create_agent_executor()
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError not raised when key missing")


def test_create_agent_executor_success():
    dummy_executor = object()

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True), \
         patch.object(main, "ChatOpenAI", DummyChatOpenAI), \
         patch.object(main, "AgentExecutor", MagicMock(return_value=dummy_executor)) as mock_exec:
        result = main.create_agent_executor()
        assert result is dummy_executor
        mock_exec.assert_called()
