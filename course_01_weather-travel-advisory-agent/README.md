
# Automated Weather & Travel Advisory Agent

Reference project from **Build Your First AI Agent: Tools, Loops & Self-Correction**.

This agent is built using pure Python and Groq, without agent frameworks such as LangGraph.

## Features

- Retrieves live weather forecasts using Open-Meteo
- Converts currencies using live exchange rates
- Uses Groq for LLM-based tool calling
- Executes tools through a Python agent loop
- Reviews the generated travel advisory using a quality auditor
- Produces a final Markdown travel report

## Requirements

The dependencies are included in the main repository installation.

A Groq API key and an internet connection are required.

Add your API key to the repository's `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

## Run

```bash
python weather_travel_advisory_agent.py
```

## How It Works

The agent starts with a predefined request for a three-day trip to Tokyo with a budget of $500 USD.

1. The LLM decides which tools to call.
2. The weather tool retrieves forecast information.
3. The currency tool converts USD to JPY.
4. The agent generates an initial response.
5. The program pauses for user input.
6. A quality auditor reviews and refines the response.

## Course Reference

This project is revisited in **Why Pure Python Agents Fail in Production** to explore memory limitations, blocking execution, error handling, and workflow complexity.

It provides a comparison point for the LangGraph implementations introduced later in the course.
