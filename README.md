# CTF Auto Solver: AI CAPTCHA Bypass

This project demonstrates an automated attack against a CAPTCHA-protected system using a Convolutional Recurrent Neural Network (CRNN) with CTC Loss.

## Project Structure

- `server/`: FastAPI server that serves CAPTHCAs and verifies answers.
- `ai_model/`: PyTorch implementation of the OCR model (CRNN).
- `dataset/`: Training and validation data (generated).
- `solver/`: Exploit script that uses the trained AI to bypass the server.
- `logs/`: Persistent execution logs for training and exploit automation.
- `logbook.md`: Detailed work journal tracking hypotheses, commands, and troubleshooting over 30 hours.



## Getting Started

### 1. Setup Isolated Environment (Recommended)
To satisfy the strict "clean environment" security requirement, the Target Server is containerized via Docker, and the AI Solver runs in a Python Virtual Environment.

#### Start the Server (Docker)
```bash
# Build and run the server using docker-compose
docker-compose up -d --build
```
*The server will be available at http://localhost:8000*

#### Setup Client/Solver Workspace (Virtual Environment)
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate
# Or on Windows: venv\Scripts\activate

# Install dependencies for AI and Exploit
pip install -r server/requirements.txt
pip install torch torchvision opencv-python requests pillow
```

### 2. Generate Dataset
You need to generate images before training.
```bash
# Ensure venv is activated
python server/captcha_gen.py --count 20000
```

### 4. Train the AI
```bash
cd ai_model
python train.py
```

### 5. Run the Exploit
```bash
cd solver
python exploit.py
```

## Challenge Goal
Successfully solve **50 consecutive CAPTCHAs** in under the time limit to retrieve the flag: `FLAG{UET_AI_Bypass_Success}`.
# UET-CN3124-DeepCAPTCHA-Solver
