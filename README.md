# CTF Auto Solver: AI CAPTCHA Bypass

This project demonstrates an automated attack against a CAPTCHA-protected system using a Convolutional Recurrent Neural Network (CRNN) with CTC Loss.

## Project Structure

- `server/`: FastAPI server that serves CAPTHCAs and verifies answers.
- `ai_model/`: PyTorch implementation of the OCR model (CRNN).
- `dataset/`: Training and validation data (generated).
- `solver/`: Exploit script that uses the trained AI to bypass the server.

## Hardware Optimization

The training script is optimized for:
- **GPU**: NVIDIA RTX 5060 Ti (16GB VRAM)
- **RAM**: 64GB
- **OS**: Ubuntu / Linux

## Getting Started

### 1. Install Dependencies
```bash
cd server
pip install -r requirements.txt
pip install torch torchvision opencv-python
```

### 2. Generate Dataset
You need to generate images before training.
```bash
# Example command (create a script or run the generator in a loop)
python server/captcha_gen.py --count 20000
```

### 3. Start the Server
```bash
cd server
uvicorn main:app --reload --port 8000
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
