# WebPageAI

## Packages

* fastapi - Web framework
* uvicorn - Running the web application
* beautifulsoup4 - HTML parsing
* openai - Interacting with OpenAI's models
* httpx - Making async http requests

## How to start server

1. Set up enviournment variables

    1.1 Create .env file from default

    ```bash
    cp .env-default > .env 
    ```

    1.2 Assign .env file variables

2. Run Docker

    ```bash
    docker-compose up --build
    ```

## How to make requests

### /source_info

```bash
curl -X GET http://0.0.0.0:8000/source_info
```

### /ask

```bash
curl -X POST http://0.0.0.0:8000/ask -H "Content-Type: text/plain" -d "What is this website for?"
```

### /openapi.json

```bash
curl -X GET http://0.0.0.0:8000/openapi.json
```

## TODO for production ready

* Cache the crawler results so it is not needed to do every time (Ex: Redis)
  * Seperate worker to populate the redis
* E2E tests
* Better filtering of unwanted text when asking questions:
  * Remove duplicate text
    * Cosine similarity
  * Remove unrelated links when making requests
    * Give OpenAI the question to ask what links to remove by giving in the link text and length of its content
* Handle more than one website
* /ask is requested in JSON format instead of plain text
* UnitTests
* Code Cleanup