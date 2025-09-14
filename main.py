from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Optional

app = FastAPI(
    title="MCP Web Fetcher",
    description="A lightning-fast web content fetcher created in the Monster Castle Laboratory ⚡",
    version="1.0.0"
)

class FetchRequest(BaseModel):
    url: HttpUrl
    summary: Optional[bool] = False

class FetchResponse(BaseModel):
    url: str
    title: Optional[str]
    content: str
    length: int

@app.post("/fetch", response_model=FetchResponse)
async def fetch_url(request: FetchRequest):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(str(request.url)) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Failed to fetch URL")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title = soup.title.string if soup.title else None
                
                # Get main content
                content = ""
                if request.summary:
                    # Get main text content, avoiding scripts and styles
                    for text in soup.stripped_strings:
                        content += f"{text} "
                    content = content[:500] + "..." if len(content) > 500 else content
                else:
                    content = html
                
                return FetchResponse(
                    url=str(request.url),
                    title=title,
                    content=content,
                    length=len(content)
                )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {
        "message": "MCP Web Fetcher is alive! ⚡",
        "usage": "POST to /fetch with {url: string, summary?: boolean}"
    }