# WebPageAI

WebPageAI is a FastAPI-based application that crawls websites and allows users to ask questions based on the crawled content. It uses OpenAI's GPT model to generate answers from the gathered data. The app provides endpoints for retrieving source information and querying the site data via a RESTful API.

## Required

* Dockerfile
* Python3.12 (For Tests)

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

## How to run tests

```bash
python -m unittest discover tests/
```

## TODO for production ready

* Cache the crawler results so it is not needed to do every time (Ex: Redis)
  * Seperate worker to populate the redis
* Tests
  * Matrix unit tests
  * E2E
  * Code Quality/Style
* E2E tests
* Better filtering of unwanted text when asking questions:
  * Remove duplicate text
    * Cosine similarity
  * Remove unrelated links when making requests
    * Give OpenAI the question to ask what links to remove by giving in the link text and length of its content
* Crawl more than one website
* /ask is requested in JSON format instead of plain text
* Implement CI/CD pipeline

## Building a CI/CD pipeline

### Version control

Having 3 type of branches: master, dev and dev-{taskID}.

Master branch would be Production enviournment branch. When changes are merged to this branch, a deployment process starts for Production. Master branch should not do tests for Deployment not be halted in case of a disaster

Dev branch would be Stage enviournment branch. When changes are merged to this branch, a deployment process starts for Stage. This would be used for pull requests to merge to Master. Dev branch will do tests and fail Deployment in case any tests fail.

Dev-{taskID} would be Development branch. Would be used for pull requests to merge code changes to Dev. Dev branch will do tests and the results are show in GitHub Pull Requests.

### Continuous Integration (CI)

Using GitHub Actions could set up to build the Docker image and run the following tests:

* Code Quality/Style checks
  * Pylint
  * Flake8
* Tests using pytest
* E2E tests using Selenium

The result of this build alongside the tests results must be shown in GitHub Pull Requests

### Continuous Deployment (CD)

Application would be automatically deployed to Azure using Azure DevOps or GitHub Actions

1. Create Github Actions Workflow file following the CI steps above
2. Set up GitHub Secrets for connecting with Azure including the Azure COntainer Registry

### Azure cloud

1. Tag Docker image
2. Push Docker image to registry
3. Create Azure App Service for Containers
4. Configure App Service to Use Docker Image
5. Test if it works
