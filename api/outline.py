from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS for all origins and GET requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/outline", response_class=PlainTextResponse)
async def get_outline(country: str = Query(..., description="Country name to fetch Wikipedia outline for")):
    wikipedia_url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    try:
        response = requests.get(wikipedia_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=404, detail=f"Wikipedia page for '{country}' not found.")

    soup = BeautifulSoup(response.text, "html.parser")

    # Get all headings in order
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    markdown = ["## Contents\n"]
    for tag in headings:
        text = tag.get_text().strip()
        if text.lower() in ["jump to navigation", "jump to search"]:
            continue
        level = int(tag.name[1])
        markdown.append(f"{'#' * level} {text}")

    return "\n\n".join(markdown)
