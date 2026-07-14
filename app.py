from flask import Flask, request, jsonify, render_template_string
import cv2
import numpy as np
import base64
import time
import os

app = Flask(__name__)

HOST = "127.0.0.1"
PORT = 5000

face_xml = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
smile_xml = os.path.join(cv2.data.haarcascades, "haarcascade_smile.xml")

face_cascade = cv2.CascadeClassifier(face_xml)
smile_cascade = cv2.CascadeClassifier(smile_xml)

if face_cascade.empty() or smile_cascade.empty():
    raise RuntimeError("OpenCV cascade files not found. Run: pip install opencv-python")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Smile Detection</title>
<style>
*{
    box-sizing:border-box;
}
body{
    margin:0;
    min-height:100vh;
    font-family:Arial,Helvetica,sans-serif;
    background:linear-gradient(135deg,#07111f,#13294b,#0f5132);
    color:white;
}
.main{
    width:min(1100px,94%);
    margin:auto;
    padding:30px 0;
}
.top{
    display:grid;
    grid-template-columns:1.2fr .8fr;
    gap:20px;
    margin-bottom:20px;
}
.card{
    background:rgba(255,255,255,.12);
    border:1px solid rgba(255,255,255,.18);
    border-radius:22px;
    padding:24px;
    box-shadow:0 18px 55px rgba(0,0,0,.25);
}
h1{
    font-size:clamp(34px,6vw,60px);
    margin:0;
}
p{
    color:#dbe4ff;
    line-height:1.6;
    font-size:18px;
}
.tags{
    display:flex;
    flex-wrap:wrap;
    gap:10px;
    margin-top:18px;
}
.tag{
    padding:8px 12px;
    border-radius:30px;
    background:rgba(255,255,255,.16);
}
ul{
    line-height:1.9;
    color:#e7f5ff;
}
.camera{
    position:relative;
    aspect-ratio:16/9;
    overflow:hidden;
    border-radius:18px;
    background:#050814;
}
video,canvas{
    position:absolute;
    inset:0;
    width:100%;
    height:100%;
    object-fit:cover;
}
video{
    transform:scaleX(-1);
}
canvas{
    pointer-events:none;
}
.stats{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:12px;
    margin-top:16px;
}
.stat{
    background:rgba(255,255,255,.13);
    border-radius:16px;
    padding:15px;
}
.stat span{
    color:#cdd6f4;
    font-size:13px;
}
.stat strong{
    display:block;
    font-size:25px;
    margin-top:5px;
}
.buttons{
    display:flex;
    flex-wrap:wrap;
    gap:12px;
    margin-top:16px;
}
button{
    border:0;
    border-radius:12px;
    padding:13px 18px;
    font-size:15px;
    font-weight:bold;
    color:white;
    cursor:pointer;
    background:linear-gradient(135deg,#4263eb,#12b886);
}
button.secondary{
    background:rgba(255,255,255,.18);
}
button:disabled{
    opacity:.55;
    cursor:not-allowed;
}
.message{
    margin-top:16px;
    padding:14px 16px;
    border-radius:14px;
    background:rgba(0,0,0,.24);
    color:#e7f5ff;
}
.green{
    color:#8ce99a;
}
.yellow{
    color:#ffd43b;
}
.red{
    color:#ffa8a8;
}
.footer{
    text-align:center;
    color:#cdd6f4;
    margin-top:18px;
}
@media(max-width:850px){
    .top{grid-template-columns:1fr}
    .stats{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:520px){
    .stats{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="main">
    <div class="top">
        <div class="card">
            <h1>😊 Smile Detection</h1>
            <p>
                Live webcam smile detection mini project using
                Python, Flask, OpenCV, HTML, CSS and JavaScript.
            </p>
            <div class="tags">
                <div class="tag">Python</div>
                <div class="tag">OpenCV</div>
                <div class="tag">Flask</div>
                <div class="tag">JavaScript</div>
                <div class="tag">HTML/CSS</div>
            </div>
        </div>
        <div class="card">
            <h2>Features</h2>
            <ul>
                <li>Webcam camera access</li>
                <li>Face detection</li>
                <li>Smile detection</li>
                <li>Live rectangle overlay</li>
                <li>Confidence percentage</li>
                <li>Easy VS Code run</li>
            </ul>
        </div>
    </div>

    <div class="card">
        <div class="camera">
            <video id="video" autoplay playsinline muted></video>
            <canvas id="canvas"></canvas>
        </div>

        <div class="stats">
            <div class="stat">
                <span>Status</span>
                <strong id="status">Ready</strong>
            </div>
            <div class="stat">
                <span>Faces</span>
                <strong id="faces">0</strong>
            </div>
            <div class="stat">
                <span>Smiles</span>
                <strong id="smiles">0</strong>
            </div>
            <div class="stat">
                <span>Speed</span>
                <strong id="speed">0 ms</strong>
            </div>
        </div>

        <div class="buttons">
            <button id="start">Start Camera</button>
            <button id="stop" class="secondary" disabled>Stop Camera</button>
        </div>

        <div class="message" id="msg">
            Click <b>Start Camera</b>, allow camera permission and smile.
        </div>
    </div>

    <div class="footer">Smile Detection Project | Single app.py file</div>
</div>

<script>
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const startBtn = document.getElementById("start");
const stopBtn = document.getElementById("stop");
const statusBox = document.getElementById("status");
const facesBox = document.getElementById("faces");
const smilesBox = document.getElementById("smiles");
const speedBox = document.getElementById("speed");
const msgBox = document.getElementById("msg");

let stream = null;
let timer = null;
let busy = false;

function setMsg(text, css=""){
    msgBox.className = "message " + css;
    msgBox.innerHTML = text;
}

function setButtons(running){
    startBtn.disabled = running;
    stopBtn.disabled = !running;
}

function fitCanvas(){
    canvas.width = video.videoWidth || canvas.clientWidth;
    canvas.height = video.videoHeight || canvas.clientHeight;
}

async function startCamera(){
    try{
        stream = await navigator.mediaDevices.getUserMedia({
            video:{width:{ideal:1280},height:{ideal:720}},
            audio:false
        });
        video.srcObject = stream;
        video.onloadedmetadata = function(){
            fitCanvas();
            startLoop();
        };
        setButtons(true);
        statusBox.textContent = "Running";
        statusBox.className = "green";
        setMsg("Camera started. Now smile in front of camera.","green");
    }catch(error){
        console.log(error);
        setMsg("Camera not started. Please allow camera permission.","red");
    }
}

function stopCamera(){
    if(timer){
        clearInterval(timer);
        timer = null;
    }
    if(stream){
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    video.srcObject = null;
    ctx.clearRect(0,0,canvas.width,canvas.height);
    setButtons(false);
    statusBox.textContent = "Stopped";
    statusBox.className = "";
    facesBox.textContent = "0";
    smilesBox.textContent = "0";
    speedBox.textContent = "0 ms";
    setMsg("Camera stopped.");
}

function captureFrame(){
    fitCanvas();
    const temp = document.createElement("canvas");
    temp.width = video.videoWidth;
    temp.height = video.videoHeight;

    const tctx = temp.getContext("2d");
    tctx.translate(temp.width,0);
    tctx.scale(-1,1);
    tctx.drawImage(video,0,0,temp.width,temp.height);

    return temp.toDataURL("image/jpeg",0.75);
}

async function detect(){
    if(busy || !stream || video.readyState < 2){
        return;
    }
    busy = true;

    try{
        const image = captureFrame();
        const response = await fetch("/detect",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({image:image})
        });

        const data = await response.json();
        updateStats(data);
        drawBoxes(data);

    }catch(error){
        console.log(error);
        setMsg("Detection error. Check VS Code terminal.","red");
    }

    busy = false;
}

function startLoop(){
    if(timer){
        clearInterval(timer);
    }
    timer = setInterval(detect,450);
}

function updateStats(data){
    if(!data.ok){
        statusBox.textContent = "Error";
        statusBox.className = "red";
        setMsg(data.message,"red");
        return;
    }

    facesBox.textContent = data.total_faces;
    smilesBox.textContent = data.smiling_faces;
    speedBox.textContent = data.processing_ms + " ms";

    if(data.smiling_faces > 0){
        statusBox.textContent = "Smiling";
        statusBox.className = "green";
        setMsg("😊 Smile detected! Confidence: " + bestConfidence(data) + "%","green");
    }else if(data.total_faces > 0){
        statusBox.textContent = "Face";
        statusBox.className = "yellow";
        setMsg("Face detected, but smile not detected.","yellow");
    }else{
        statusBox.textContent = "No Face";
        statusBox.className = "";
        setMsg("No face detected. Sit properly in front of camera.");
    }
}

function bestConfidence(data){
    if(!data.faces || data.faces.length === 0){
        return 0;
    }
    return Math.max(...data.faces.map(face => face.confidence || 0));
}

function drawBoxes(data){
    ctx.clearRect(0,0,canvas.width,canvas.height);

    if(!data.ok || !data.faces){
        return;
    }

    const sx = canvas.width / video.videoWidth;
    const sy = canvas.height / video.videoHeight;

    data.faces.forEach(item => {
        const f = item.face;
        const x = f.x * sx;
        const y = f.y * sy;
        const w = f.w * sx;
        const h = f.h * sy;

        ctx.lineWidth = 4;
        ctx.strokeStyle = item.smiling ? "#51cf66" : "#ffd43b";
        ctx.strokeRect(x,y,w,h);

        ctx.fillStyle = item.smiling ? "#51cf66" : "#ffd43b";
        ctx.font = "bold 22px Arial";
        ctx.fillText(item.smiling ? "Smile " + item.confidence + "%" : "Face", x+8, Math.max(28,y-10));

        item.smiles.forEach(s => {
            ctx.lineWidth = 3;
            ctx.strokeStyle = "#74c0fc";
            ctx.strokeRect(s.x*sx,s.y*sy,s.w*sx,s.h*sy);
        });
    });
}

startBtn.addEventListener("click",startCamera);
stopBtn.addEventListener("click",stopCamera);

window.addEventListener("resize",function(){
    if(stream){
        fitCanvas();
    }
});
</script>
</body>
</html>
"""


def clean_base64(data_url):
    if "," in data_url:
        return data_url.split(",", 1)[1]
    return data_url


def decode_frame(data_url):
    image_data = base64.b64decode(clean_base64(data_url))
    image_np = np.frombuffer(image_data, dtype=np.uint8)
    frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    if frame is None:
        raise ValueError("Invalid image received")

    return frame


def resize_for_speed(frame, max_width=720):
    height, width = frame.shape[:2]

    if width <= max_width:
        return frame, 1.0

    scale = max_width / width
    new_height = int(height * scale)
    small = cv2.resize(frame, (max_width, new_height))
    return small, scale


def make_box(x, y, w, h, scale):
    return {
        "x": int(x / scale),
        "y": int(y / scale),
        "w": int(w / scale),
        "h": int(h / scale),
    }


def get_confidence(face, smiles):
    if len(smiles) == 0:
        return 0

    face_area = max(face["w"] * face["h"], 1)
    smile_area = max(s["w"] * s["h"] for s in smiles)
    score = int((smile_area / face_area) * 900)

    if score < 20:
        score = 20
    if score > 100:
        score = 100

    return score


def run_detection(frame):
    start = time.time()
    small, scale = resize_for_speed(frame)

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(70, 70)
    )

    result_faces = []

    for (x, y, w, h) in faces:
        mouth_start = int(h * 0.45)
        mouth = gray[y + mouth_start:y + h, x:x + w]

        smiles = smile_cascade.detectMultiScale(
            mouth,
            scaleFactor=1.7,
            minNeighbors=18,
            minSize=(25, 25)
        )

        face_box = make_box(x, y, w, h, scale)
        smile_boxes = []

        for (sx, sy, sw, sh) in smiles:
            smile_boxes.append(
                make_box(x + sx, y + mouth_start + sy, sw, sh, scale)
            )

        confidence = get_confidence(face_box, smile_boxes)

        result_faces.append({
            "face": face_box,
            "smiles": smile_boxes,
            "smiling": len(smile_boxes) > 0,
            "confidence": confidence
        })

    smiling_count = sum(1 for face in result_faces if face["smiling"])
    processing_ms = int((time.time() - start) * 1000)

    return {
        "ok": True,
        "message": "Smile detected" if smiling_count else "No smile",
        "faces": result_faces,
        "total_faces": len(result_faces),
        "smiling_faces": smiling_count,
        "processing_ms": processing_ms
    }


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/detect", methods=["POST"])
def detect():
    try:
        data = request.get_json(silent=True) or {}
        image = data.get("image")

        if not image:
            return jsonify({"ok": False, "message": "Image missing"}), 400

        frame = decode_frame(image)
        result = run_detection(frame)
        return jsonify(result)

    except Exception as error:
        return jsonify({
            "ok": False,
            "message": str(error),
            "faces": [],
            "total_faces": 0,
            "smiling_faces": 0,
            "processing_ms": 0
        }), 500


@app.route("/health")
def health():
    return jsonify({"ok": True, "message": "Server running"})


if __name__ == "__main__":
    print("=" * 60)
    print("Smile Detection Project Started")
    print("Open this link: http://127.0.0.1:5000")
    print("Press CTRL + C to stop")
    print("=" * 60)
    app.run(host=HOST, port=PORT, debug=True)
