#!/usr/bin/env python3
import argparse
import colorlog
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

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
You are an AI documentation generator. Your task is to create detailed API documentation in Markdown format based on a given dictionary of filepaths and file contents.

The API consists of multiple endpoints, each defined in different files. For each endpoint, extract its purpose, request method (GET, POST, etc.), URL path, parameters (query, body, headers), expected responses, and any additional details.

Structure the documentation as follows:

    API Overview
    Authentication (if applicable)
    List of Endpoints
        Endpoint Name
        Method: (GET/POST/PUT/DELETE)
        URL: /api/example
        Description: What this endpoint does
        Request Parameters: Query, Path, and Body parameters with types and descriptions
        Response Format: Expected success and error responses with examples
        Headers: Required headers, if any
    Error Codes & Descriptions
    Examples of API Usage

Ensure that the documentation is clear, concise, and follows best practices for API documentation. Use Markdown formatting, including code blocks for examples. Generate tables where necessary for parameters and responses.

Here is the dictionary of file paths and contents:
<FILE CONTENTS>

Generate the Markdown documentation based on this input. You must keep the documentation under 10000 characters.
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


if __name__ == "__main__":
    main()
