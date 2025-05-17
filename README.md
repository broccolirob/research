# Research Project

This project demonstrates a minimal Python package with a focus on test-driven development.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project with test dependencies:

```bash
pip install -e '.[test]'
```

## Configuration

The application expects an OpenAI API key to interact with LangChain and the
OpenAI service. Copy the provided `.env.example` file to `.env` and replace the
placeholder with your actual key:

```bash
cp .env.example .env
echo "OPENAI_API_KEY=your-real-key" >> .env
```

The `python-dotenv` package automatically loads variables from the `.env` file
when running `main.py`.

## Running the tests

Use `pytest` to run the test suite:

```bash
pytest
```
