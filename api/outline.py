from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS (Allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/", response_class=PlainTextResponse)
def get_outline(country: str = Query(..., min_length=1)):
    # Format Wikipedia URL
    base_url = "https://en.wikipedia.org/wiki/"
    url = base_url + country.replace(" ", "_")

    # Fetch page
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Wikipedia page not found")

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract all headings h1-h6
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

    markdown = ["## Contents\n"]
    for tag in headings:
        level = int(tag.name[1])
        text = tag.get_text().strip()
        if text.lower() in ["jump to navigation", "jump to search"]:
            continue
        markdown.append(f"{'#' * level} {text}")

    return "\n\n".join(markdown)
