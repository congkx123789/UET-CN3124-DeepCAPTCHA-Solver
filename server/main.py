import uuid
import base64
import io
import os
import sys
import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict
import string

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from .captcha_gen import CaptchaGenerator
except (ImportError, ValueError):
    from captcha_gen import CaptchaGenerator

from ai_model.model import CRNN
from solver.utils import preprocess_image, decode_prediction

app = FastAPI(title="CTF CAPTCHA Server & Demo")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

gen = CaptchaGenerator()

# AI Model Initialization
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CHARACTERS = string.ascii_uppercase + string.digits
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../ai_model/weights/best_model.pth")
model = None

# def load_model():
#     global model
#     model = CRNN(num_chars=len(CHARACTERS) + 1).to(DEVICE)
#     if os.path.exists(MODEL_PATH):
#         model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
#         model.eval()
#         print(f"[*] AI Model loaded successfully from {MODEL_PATH}")
#     else:
#         print(f"[!] Warning: Model weights not found at {MODEL_PATH}. AI will predict randomly.")
#
# load_model()

# In-memory store for sessions
sessions: Dict[str, str] = {}
user_progress: Dict[str, int] = {}

class VerifyRequest(BaseModel):
    session_id: str
    answer: str

class PredictRequest(BaseModel):
    image: str

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/challenge")
async def get_challenge():
    session_id = str(uuid.uuid4())
    img, text = gen.generate()
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    sessions[session_id] = text
    if session_id not in user_progress:
        user_progress[session_id] = 0
        
    return {
        "session_id": session_id,
        "image": img_str,
        "requirement": "Solve 50 consecutive CAPTCHAs to get the flag."
    }

@app.post("/verify")
async def verify_captcha(req: VerifyRequest):
    expected = sessions.get(req.session_id)
    if not expected:
        raise HTTPException(status_code=404, detail="Invalid or expired session.")
        
    if req.answer.upper() == expected.upper():
        user_progress[req.session_id] += 1
        count = user_progress[req.session_id]
        
        if count >= 50:
            return {
                "status": "success",
                "message": f"Verified {count}/50",
                "flag": "FLAG{UET_AI_Bypass_Success}"
            }
        else:
            img, next_text = gen.generate()
            sessions[req.session_id] = next_text
            
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "status": "correct",
                "progress": f"{count}/50",
                "next_image": img_str
            }
    else:
        user_progress[req.session_id] = 0
        return {
            "status": "failed",
            "message": "Incorrect answer. Streak reset.",
            "progress": "0/50"
        }

@app.post("/ai_predict")
async def ai_predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    try:
        tensor_img = preprocess_image(req.image).to(DEVICE)
        with torch.no_grad():
            outputs = model(tensor_img)
            prediction = decode_prediction(outputs)
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
