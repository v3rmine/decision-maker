from os.path import expanduser
import json

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_experimental.chat_models import Llama2Chat
from langchain.llms import LlamaCpp
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage

B_FUNC, E_FUNC = "<FUNCTIONS>", "</FUNCTIONS>\n\n"
B_TYPES, E_TYPES = "<TYPES>", "</TYPES>\n\n"
B_INST, E_INST = "[INST] ", " [/INST]"
function_metadata = [{
    "function": "go",
    "description": "Move the robot to some coordinates.",
    "arguments": [
        {
            "name": "to",
            "type": "coordinates",
            "description": "Coordinates of a location"
        }
    ],
}, {
    "function": "get_location_coordinates",
    "description": "Return the coordinates associated with an location name.",
    "arguments": [
        {
            "name": "location_name",
            "type": "string",
            "description": "Name of a defined location."
        }
    ],
    "return": {
        "type": "coordinates",
        "description": "Coordinates associated with location_name"
    }
}, {
    "function": "search",
    "description": "Search for an object/element in the robot environment.",
    "arguments": [
        {
            "name": "element",
            "type": "string",
            "description": "Name of the element to search."
        }
    ]
}, {
    "function": "grab",
    "description": "Grab an element with the robot hand",
    "arguments": [
        {
            "name": "element",
            "type": "string",
            "description": "Name of the element to grab."
        }
    ]
}]
types_metadata = [{
    "ident": "string",
    "desc": "sequence of text"
}, {
    "ident": "list",
    "desc": "list of elements",
    "args": [{
        "type": "generic",
        "desc": "element of the list"
    }]
}, {
    "ident": "coordinates",
    "desc": "Specific position coordinates on X and Y axis",
}]

function_list = json.dumps(function_metadata, indent=4)
functions=function_list.strip().replace("{", "{{").replace("}", "}}")
types_list = json.dumps(types_metadata, indent=4)
types=types_list.strip().replace("{", "{{").replace("}", "}}")
template_messages = [
    SystemMessage(content=
    """
    You convert a prompt, a list of TYPES, a list of FUNCTIONS to a list of sequential function calls, one function call per line.
    Example:
    <TYPES>
    [{
        "ident": "string",
        "desc": "sequence of text"
    }, {
        "ident": "list",
        "desc": "list of elements",
        "args": [{
            "type": "generic",
            "desc": "element of the list"
        }]
    }]
    </TYPES>

    <FUNCTIONS>
    [{
        "function": "search",
        "description": "Search for a query online.",
        "arguments": [
            {
                "name": "element",
                "type": "string",
                "description": "Name of the element to search."
            }
        ],
        "returns": {
            "type": "list<string>",
            "description": "List of found content."
        }
    }, {
        "function": "filter",
        "description": "Filter a list to remove the unwanted elements",
        "arguments": [
            {
                "name": "element",
                "type": "list<string>",
                "description": "Name of the element to grab."
            },
            {
                "name": "pattern",
                "type": "string",
                "description": "Pattern to keep in the list"
            }
        ],
        "returns": {
            "type": "list<string>",
            "description": "Filtered list of results"
        }
    }]
    </FUNCTIONS>

    [INST] Search for cats online where orange is in content [/INST]

    [AI]
    result = search("cats")
    filter(result, "orange")
    [/AI]
    """),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template(f"{B_TYPES}{types}{E_TYPES}{B_FUNC}{functions}{E_FUNC}{B_INST}{{text}}{E_INST}\n\n"),
]
prompt_template = ChatPromptTemplate.from_messages(template_messages)
print(prompt_template.to_json())
model_path = expanduser("./llama-2-7b-chat.Q3_K_M.gguf")

llm = LlamaCpp(
    model_path=model_path,
    streaming=False,
    temperature=0.5,
    top_p=1,
    n_ctx=1024,
)
model = Llama2Chat(llm=llm)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
chain = LLMChain(llm=model, prompt=prompt_template, memory=memory)

print(
    chain.run(
        text="Go to the kitchen and bring a banana",
    )
)