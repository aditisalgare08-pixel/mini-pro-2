# Smile Detection Mini Project

This is an easy VS Code project using Python, HTML, CSS and JavaScript.

## Features

- Webcam access from browser
- Face detection using OpenCV
- Smile detection using OpenCV Haar Cascade
- Live rectangle overlay
- Confidence percentage
- Single main code file: `app.py`

## Required Packages

The packages are listed in `requirements.txt`:

```txt
flask
opencv-python
numpy
```

## How to Run in VS Code

### Step 1: Extract ZIP
Extract the ZIP file and open the folder in VS Code.

### Step 2: Open VS Code Terminal
Use:

```powershell
Terminal > New Terminal
```

### Step 3: Create Virtual Environment

```powershell
python -m venv venv
```

### Step 4: Activate Virtual Environment

```powershell
.\venv\Scripts\activate
```

### Step 5: Install Packages

```powershell
pip install -r requirements.txt
```

### Step 6: Run Project

```powershell
python app.py
```

### Step 7: Open Browser

Open:

```text
http://127.0.0.1:5000
```

Click **Start Camera**, allow camera permission, and smile.

## Common Error Fix

If `python` does not work, try:

```powershell
py -m venv venv
.\venv\Scripts\activate
py -m pip install -r requirements.txt
py app.py
```

If camera does not open, allow camera permission in browser settings.
