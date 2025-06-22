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

def generate_outline(country: str) -> str:
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        raise HTTPException(status_code=404, detail="Wikipedia page not found.")

    soup = BeautifulSoup(response.text, "html.parser")
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    markdown = []
    for tag in headings:
        text = tag.get_text().strip()
        if text.lower() in ["jump to navigation", "jump to search"]:
            continue
        level = int(tag.name[1])
        markdown.append(f"{'#' * level} {text}")
    return "\n\n".join(markdown)


# ✅ API endpoint with optional query parameter
@app.get("/", response_class=PlainTextResponse)
async def get_outline(country: str = Query("India", description="Country name to fetch Wikipedia outline for")):
    return generate_outline(country)

