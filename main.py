import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from src.crawler.crawler import crawl_site
from src.openapi.openai import OpenAI

load_dotenv()

WEBSITE = os.getenv("BASE_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):
	print(f"Crawling site '{WEBSITE}'")
	app.state.site_data = await crawl_site(WEBSITE)
	app.state.openai = OpenAI({WEBSITE: get_site_data()})
	yield

app = FastAPI(lifespan=lifespan)

@app.get("/source_info")
async def get_source():
	return get_site_data()

@app.post("/ask")
async def ask_question(request: Request):
	question = (await request.body()).decode('utf-8')
	if len(question) > 500:
		raise HTTPException(status_code=400, detail="Question exceeds maximum length of 500 characters")

	response = get_openai().ask(WEBSITE, question) 
	return {
		"response": {
			"user_question": question,
			"answer": response.answer,
			"usage": {
				"input_tokens": response.input_tokens,
				"output_tokens": response.output_tokens
			},
			"sources": response.sources
		}
	}

@app.get("/openapi.json")
def get_openapi_endpoint():
	return JSONResponse(content=get_openapi(
		title="WepPage AI API",
		version="1.0.0",
		routes=app.routes,
	))


def get_site_data() -> dict[str, str]:
	return app.state.site_data

def get_openai() -> OpenAI:
	return app.state.openai