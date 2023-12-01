from os.path import expanduser
import json

from llama_cpp import Llama

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
    "function": "get_location",
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
    ],
    "return": {
        "type": "coordinates",
        "description": "Coordinates associated with the element"
    }
}, {
    "function": "grab",
    "description": "Grab an element at some coordinates with the robot hand",
    "arguments": [
        {
            "name": "where",
            "type": "coordinates",
            "description": "Coordinates of the element to grab."
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
functions = function_list.strip().replace("{", "{{").replace("}", "}}")
types_list = json.dumps(types_metadata, indent=4)
types = types_list.strip().replace("{", "{{").replace("}", "}}")

model_path = expanduser("./llama-2-7b-chat.Q3_K_M.gguf")
llm = Llama(
    model_path=model_path,
    streaming=False,
    temperature=0,
    top_p=1,
    n_ctx=2048,
    verbose=False,
    use_mmap=True,
    use_mlock=True,
)

resp = llm.create_chat_completion(
    messages = [
        {
            "role": "system", 
            "content": f"""
            You are a helful functions chain plannifier, that only communicate in valid JSON files.
            Here are your capabilities:
            {{
                "types": {types},
                "functions": {functions}
            }}
            The expected output from you has to be a valid JSON array with the functions chain:
            [
                {{
                    "function": <function1_name>,
                    "args": [<optional function_parameters>],
                    "store_result": <optional $variable to store result>
                }}, {{
                    "function": <function2_name>,
                    "args": [<optional function_parameters>],
                    "store_result": <optional $variable to store result>
                }}
            ]
            """
        },
        {
            "role": "user",
            "content": """
            { "prompt":"Go to the kitchen and bring a banana" }
            """,
        },
        {
            "role": "assistant",
            "content": """
            [
                {
                    "function": "get_location",
                    "args": [{ "location_name": "kitchen" }],
                    "store_result": "$location"
                }, {
                    "function": "go",
                    "args": [{ "to": "$location" }]
                }, {
                    "function": "search",
                    "args": [{ "element": "banana" }],
                    "store_result": "$banana_location"
                }, {
                    "function": "grab",
                    "args": [{ "where": "$banana_location" }]
                }
            ]
            """
        },
        {
            "role": "user",
            "content": """
            { "prompt": "Grab an apple in the fridge in the kitchen" }
            """
        }
    ]
)

assistant_response = json.loads(json.dumps(resp))['choices'][0]['message']['content']
print(assistant_response)