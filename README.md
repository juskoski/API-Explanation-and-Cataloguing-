# API-Explanation-and-Cataloguing
## Jussi Koskinen - 2303255
This repository contains the assignment for API Explanation and Cataloguing for the course Advanced Software Quality and Security 2024/2025.

## Description
This project utilizes a LLM, OpenAI's o1, to build API documentation from a project's repository.

## Setup
Instructions assume Linux is used.

**Note!** This is developed ad-hoc for completing the assingment and thus only supports `.py` files. LLMs can hallucinate quite a bit, so restricting the filetype only to `.py` helps with correcting hallucinations.

1. Create a new python virtual environment and start it:
```sh
$ python3 -m venv venv
$ source venv/bin/activate
```
2. Install the requirements:
```sh
$ pip3 install -r requirements.txt
```
3. Create a file named `.env` and copy the contents from (.env.example)[.env.example]. Replace the placeholder API key with your OpenAI API key.
4. For this project, Wazuh is used as for testing
```sh
$ cd ..
$ git clone git@github.com:wazuh/wazuh.git
$ cd API-Explanation-and-Cataloguing-
```
4. Run the application:
```sh
$ python3 main.py --project-path ../wazuh
```

# Code style
The code style follows [PEP8](https://peps.python.org/pep-0008/) with the exception that lines can be up to 120 characters long.

Commits shall follow the 50/72 formatting rule.

# Report of AI use
AI was used to help in explaining the assingment requirements and writing the code. AI tools used:
- ChatGPT
- Perplexity
