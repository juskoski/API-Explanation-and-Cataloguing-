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

    logging.info(f"Path: {args.project_path}")


if __name__ == "__main__":
    main()
