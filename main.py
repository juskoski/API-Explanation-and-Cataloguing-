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

Return the API directory path(s) along with a short reasoning for your choice.
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
    response = generate_response(prompt, 1000)
    logging.info(f"LLM response to identified API files: {response}")


if __name__ == "__main__":
    main()
