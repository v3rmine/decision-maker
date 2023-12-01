import requests
import json

# Define the function metadata
function_metadata = [{
    "function": "goto_location",
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
    "function": "search_element",
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
    "function": "grab_element",
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

# Define the user prompt
user_prompt = 'Go to the kitchen and bring a banana.'

history = [
    {
        "role": "system", 
        "content": f"""
        You are an helpful AI, that only communicate in valid JSON files.
        Here are your only capabilities:
        {{
            "types": {types}, // The types that you will encounter, throw an error if you miss one
            "functions": {functions} // The functions that you can use, throw an error if you miss one
        }}
        Variables are preceded by '$', you cannot use them if they haven't been initialized. 
        The expected output from you has to be a valid JSON array.
        """
    },
    {
        "role": "user",
        "content": """
        { "prompt":"Go to the kitchen and grab a banana" }
        """,
    },
    {
        "role": "assistant",
        "content": """
        [
            {
                "function": "get_location",
                "args": [{ "location_name": "kitchen" }],
                "store_result": "$kitchen_location"
            }, {
                "function": "goto_location",
                "args": [{ "to": "$kitchen_location" }]
            }, {
                "function": "search_element",
                "args": [{ "element": "banana" }],
                "store_result": "$banana_location"
            }, {
                "function": "grab_element",
                "args": [{ "where": "$banana_location" }]
            }
        ]
        """
    },
    {
        "role": "user",
        "content": """
        { "prompt":"Go to the kitchen and come back" }
        """,
    },
    {
        "role": "assistant",
        "content": """
        [
            {
                "function": "get_location",
                "args": [{ "location_name": "current" }],
                "store_result": "$initial_location"
            }, {
                "function": "get_location",
                "args": [{ "location_name": "kitchen" }],
                "store_result": "$kitchen_location"
            }, {
                "function": "goto_location",
                "args": [{ "to": "$kitchen_location" }]
            }, {
                "function": "goto_location",
                "args": [{ "to": "$initial_location" }]
            }
        ]
        """
    },
    {
        "role": "user",
        "content": """
        { "prompt": "Go to bedroon and grab the dog" }
        """
    }
]

def wizard_message(message):
    if message['role'] == 'system':
        return f"{message['content']}\n"
    elif message['role'] == 'user':
        return f"""
        USER:
        {message['content']}"""
    elif message['role'] == 'assistant':
        return f"""
        ASSISTANT:
        {message['content']}"""
    else:
        return ""
    
def llama_message(message):
    if message['role'] == 'system':
        return f"<<SYS>> {message['content']} <</SYS>"
    elif message['role'] == 'user':
        return f"""
        [INST]
        {message['content']}
        [/INST]"""
    elif message['role'] == 'assistant':
        return f"""
        {message['content']}
        """
    else:
        return ""
    
def alpaca_message(message):
    if message['role'] == 'system':
        return f"{message['content']}'\n\n"
    elif message['role'] == 'user':
        return f"""
        ### Instruction:
        {message['content']}"""
    elif message['role'] == 'assistant':
        return f"""
        ### Response:
        {message['content']}"""
    else:
        return ""

# Format the function list and prompt
function_list = json.dumps(function_metadata, indent=4)
prompt = ''.join(map(alpaca_message, history))

# Define the API endpoint
# url = "http://127.0.0.1:8080/completion"
url = "http://192.168.1.111:8080/completion"
# url = "http://192.168.1.242:8080/completion"

# Send the POST request to the API server
response = requests.post(url, json={"prompt": prompt})

# Print the response
print(response.json()["content"])
