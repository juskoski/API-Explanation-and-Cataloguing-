#!/usr/bin/env python3
import argparse
import colorlog
import logging
import os
from flask import Flask, send_file
from flask_swagger_ui import get_swaggerui_blueprint
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Endpoints for the API catalogue
SWAGGER_URL = "/swagger"
SWAGGER_FILE_FILEPATH = "api_documentation_swagger.yaml"
API_URL = f"/static/{SWAGGER_FILE_FILEPATH}"

# Endpoint configuration
swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Load the OpenAI API key and initialize the client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME: str = "gpt-4o-mini"

# Prompts
PROMPT_IDENTIFY_API = """
You are an expert in analyzing software project structures. Given a list of file paths, identify which directory (or directories) is most likely the API directory. API directories often contain files related to request handling, such as routes/, controllers/, api/, or endpoints/. Consider naming conventions and directory structures used in common web frameworks (Node.js, Django, Flask, etc.).

Here is the list of file paths:

<PATHS>

Only return the file paths with the APIs, each path on their own line, like so:
    path 1
    path 2
    path n

Do not add any other explanation or other response text. Only include the .py python files. Ignore all __init__.py files and other not-source-code related files.
"""

PROMPT_GENERATE_DOCUMENTATION = """
You are an AI-powered documentation generator. Your task is to generate a Swagger (OpenAPI 3.0.0) YAML specification based on a given dictionary of file paths and their contents.
Requirements:

    - Extract API details from the given file contents, including:
        - Endpoint Purpose: A brief description of what the endpoint does.
        - Request Method: (e.g., GET, POST, PUT, DELETE).
        - URL Path: The endpoint’s path.
        - Parameters: Identify query parameters, request body, headers, and path variables.
        - Responses: Define expected response codes (200, 400, 500, etc.) and their descriptions.
        - Request/Response Examples: If available, include JSON examples for clarity.
    - Ensure the documentation follows Swagger best practices and is structured properly.
    - Keep the YAML output under 10,000 characters.

Instructions:

    - Parse the given dictionary, where:
        - Keys represent file paths.
        - Values contain the code and comments that define API endpoints.
    - Extract relevant API details and organize them in Swagger-compliant YAML format.
    - Do not include any text that is not part of the YAML documentation.
    - Ensure proper indentation and formatting to maintain readability.

Do not include any backticks or other markdown formatting, the user is expecting the entire file to be in valid yaml syntax.

Here are the file contents:
<FILE CONTENTS>
"""

PROMPT_GENERATE_NEW_ENDPOINT = """
You are an AI assistant specializing in generating API endpoints for web applications. Given a project structure and a description of the desired functionality, your task is to generate a new API endpoint.

### Requirements:
- The generated code must follow best practices for API development.
- Include proper request validation.
- Implement appropriate HTTP methods (GET, POST, PUT, DELETE) based on the functionality.
- Include clear comments explaining each part of the code.
- If authentication or authorization is required, incorporate it accordingly.
- Ensure error handling for invalid requests and unexpected failures.
- Return responses in JSON format, following RESTful API principles.

### Instructions:
- Analyze the provided project structure to determine where the new endpoint should be placed.
- Use the given functionality description to generate the correct API logic.
- Ensure that the endpoint follows the conventions of the detected framework.
- Only return the generated Python code, without additional explanation.

**Inputs:**
- Project structure: <PATHS>
- Functionality description: <DESCRIPTION>
- Project file contents: <FILE CONTENTS>
"""

# Logging configuration
log_formatter = colorlog.ColoredFormatter(
    '%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


def generate_response(prompt: str, max_len: int) -> str:
    """
    Generates a response based on the prompt using OpenAI's ChatGPT API.

    Args:
        prompt (str): The prompt to generate a response for.
        max_len (int): The maximum length for a response (max tokens).

    Returns:
        str: The model's generated response.
    """
    logger.info(f"Generating response for prompt: {prompt}")

    try:
        # Make API call to OpenAI's ChatGPT API
        response = client.chat.completions.create(model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_len)

        # Extract and return the generated text from the response
        response_text = response.choices[0].message.content
        return response_text
    except Exception as e:
        logger.error(f"Error occurred while generating response: {e}")
        raise


def get_filepaths_from_path(project_path: str) -> list:
    """
    Fetches all filepaths from the provided project path, if it exists.

    Args:
        project_path (str): The path to the project's root directory.

    Returns:
        List of filepaths.
    """
    try:
        logging.info(f"Fetching filepaths from {project_path}")
        paths = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                paths.append(os.path.join(root, file))  # Full path of each file
        logging.info(f"Successfully found filepaths")
        return paths
    except FileNotFoundError:
        logging.error(f"Path {project_path} does not exist on the system.")
        raise


def initialize_argparse() -> argparse.ArgumentParser:
    """
    Initializes and returns the argument parser for the CLI tool.

    Returns:
        argparse.ArgumentParser: The initialized and configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Returs the Risk Analysis remedation suggestion for the chosen scenarios."
    )

    parser.add_argument(
        "--project-path",
        type=str,
        required=True,
        help="Path to the local project."
    )

    return parser


def main() -> None:
    """
    Main function of the application for the assignment SS-B.

    Returns:
        None
    """
    parser = initialize_argparse()
    args = parser.parse_args()

    # Get the files from the provided path
    filepaths = get_filepaths_from_path(args.project_path)

    # Ask AI to identify the directories with API endpoints
    prompt = PROMPT_IDENTIFY_API.replace("<PATHS>", str(filepaths))
    identified_api_endpoints = generate_response(prompt, 1000).split("\n")

    # Fetch file contents using the LLM provided filepaths
    file_contents = {}
    for filepath in identified_api_endpoints:
        try:
            # Only consider .py files
            if filepath.endswith(".py"):
                f = open(filepath, "r")
                file_contents[filepath] = f.read()
            else:
                logging.error(f"Attempted to parse a non-python file: {filepath}")
        except FileNotFoundError:
            # AI hallucinated and failed to identify some filepath
            logging.error(f"Filepath {filepath} does not exist!")
            continue
        except Exception as e:
            logging.error(f"Exception occurred while reading {filepath}: {e}")
            continue

    # Take only the first n files as analyzing all of them at once overwhelms the API
    prompt = PROMPT_GENERATE_DOCUMENTATION.replace("<FILE CONTENTS>", str(file_contents))
    generated_api_documentation = generate_response(prompt, 10000)
    logging.info(generated_api_documentation)

    # Save the response as a file
    filename = "api_documentation_swagger.yaml"
    with open(filename, "w") as file:
        file.write(generated_api_documentation)

    logging.info("Navigate to http://localhost:5000 for the API catalogue.")

    # Generate new endpoint based on user's request
    new_endpoint_description = "I want to create a new endpoint which deletes user agents from all devices"
    prompt = PROMPT_GENERATE_NEW_ENDPOINT.replace("<PATHS>", str(filepaths))

    # Only consider half of the file contents, otherwise the OpenAPI token limit may be reached
    file_contents_str = str(file_contents)
    mid_index = len(file_contents_str) // 2
    file_contents_first_half = file_contents_str[:mid_index]

    prompt = prompt.replace("<FILE CONTENTS>", str(file_contents_first_half))
    prompt = prompt.replace("<DESCRIPTION>", new_endpoint_description)
    new_api_endpoint_code = generate_response(prompt, 10000)
    logging.info(f"Code for new endpoint: {new_api_endpoint_code}")


@app.route(API_URL)
def swagger_yaml():
    return send_file(SWAGGER_FILE_FILEPATH, mimetype="text/yaml")


if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=5000, debug=True)
