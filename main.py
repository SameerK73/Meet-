from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import Utils

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class TranscriptInput(BaseModel):
    transcript: str
    createEvent: bool

class TranscriptOutput(BaseModel):
    action_items: str
    summary: str
    event_details: dict

@app.post("/process_transcript", response_model=TranscriptOutput)
async def process_transcript(data: TranscriptInput):
    actionItems = Utils.getactionItems(data.transcript)
    summary = Utils.getMeetingSummary(data.transcript)
    eventDetails = Utils.getEventDetails(data.transcript)
    if(data.createEvent):
        Utils.createEvent(eventDetails)
    return {
        "action_items": actionItems,
        "summary": summary,
        "event_details": eventDetails
    }

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request}) 