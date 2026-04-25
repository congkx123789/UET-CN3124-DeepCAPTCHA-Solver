import uuid
import base64
import io
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
try:
    from .captcha_gen import CaptchaGenerator
except (ImportError, ValueError):
    from captcha_gen import CaptchaGenerator

app = FastAPI(title="CTF CAPTCHA Server")
gen = CaptchaGenerator()

# In-memory store for sessions (session_id -> captcha_text)
sessions: Dict[str, str] = {}
# Track consecutive correct answers
user_progress: Dict[str, int] = {}

class VerifyRequest(BaseModel):
    session_id: str
    answer: str

@app.get("/challenge")
async def get_challenge():
    session_id = str(uuid.uuid4())
    img, text = gen.generate()
    
    # Save to buffer
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
        throw_error(404, "Invalid or expired session.")
        
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
            # Generate a new one for the same session to continue the streak
            # Wait, typically in CTFs you get a NEW session ID or keep the same one but refresh the challenge.
            # Let's keep the same session ID for the streak.
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
        user_progress[req.session_id] = 0 # Reset streak on failure
        return {
            "status": "failed",
            "message": "Incorrect answer. Streak reset.",
            "progress": "0/50"
        }

def throw_error(code: int, detail: str):
    raise HTTPException(status_code=code, detail=detail)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
