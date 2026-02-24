from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scanner import WebScanner
import os

app = FastAPI(title="Web Security Scanner")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scan")
async def start_scan(url: str = Form(...)):
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    scanner = WebScanner(url)
    results = scanner.run_scan()
    
    if "error" in results:
        return JSONResponse(status_code=400, content=results)
        
    return results

@app.get("/results", response_class=HTMLResponse)
async def results_page(request: Request):
    # This page will be populated via JavaScript from the scan session
    return templates.TemplateResponse("results.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
