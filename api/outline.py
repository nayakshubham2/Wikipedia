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
    wikipedia_url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    try:
        response = requests.get(wikipedia_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=404, detail=f"Wikipedia page for '{country}' not found.")

    soup = BeautifulSoup(response.text, "html.parser")

    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    outline = "## Contents\n\n"

    seen_titles = set()

    for tag in headings:
        title = tag.get_text(strip=True)

        # Avoid duplicate page title headers or unwanted Wikipedia boilerplate
        if not title or title in seen_titles or title.lower() in ["references", "external links", "see also", "navigation menu"]:
            continue

        seen_titles.add(title)
        level = int(tag.name[1])
        outline += f"{'#' * level} {title}\n\n"

    return {"markdown": outline.strip()}
# ✅ API endpoint with optional query parameter
@app.get("/", response_class=PlainTextResponse)
async def get_outline(country: str = Query("India", description="Country name to fetch Wikipedia outline for")):
    return generate_outline(country)

