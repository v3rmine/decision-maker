import requests
import json

# Define the roles and markers
B_FUNC, E_FUNC = "<FUNCTIONS>", "</FUNCTIONS>\n\n"
B_INST, E_INST = "[INST] ", " [/INST]" #Llama style
# B_INST, E_INST = "\n### Instruction:\n", "\n### Response:\n" #DeepSeek Coder Style
# B_INST, E_INST = "Human: ", " Assistant: " #Yi Style

# Define the function metadata
function_metadata = [{
    "function": "go",
    "description": "Move the robot to some coordinates.",
    "arguments": [
        {
            "name": "to",
            "type": "Coordinates",
            "description": "Coordinates of a location"
        }
    ],
}, {
    "function": "get_coordinates",
    "description": "Return the coordinates associated with an waypoint name.",
    "arguments": [
        {
            "name": "waypoint_name",
            "type": "string",
            "description": "Name of a defined waypoint."
        }
    ],
    "return": {
        "type": "Coordinates",
        "description": "Coordinates associated with waypoint_name"
    }
}, {
    "function": "search",
    "description": "Search for an object/element around.",
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

# Define the user prompt
user_prompt = 'Go to the kitchen and bring a banana.'

# Format the function list and prompt
function_list = json.dumps(function_metadata, indent=4)
prompt = f"{B_FUNC}{function_list.strip()}{E_FUNC}{B_INST}{user_prompt.strip()}{E_INST}\n\n"

# Define the API endpoint
url = "http://127.0.0.1:8080/completion"

# Send the POST request to the API server
response = requests.post(url, json={"prompt": prompt})

# Print the response
print(json.dumps(response.json(), indent=4, sort_keys=True))
