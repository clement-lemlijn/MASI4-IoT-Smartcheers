"""Camera API Flask - Stream vidéo en direct et capture de photos."""
import time
import json
from flask import Flask, Response, send_file
from picamera import PiCamera
from picamera.array import PiRGBArray
from PIL import Image
from io import BytesIO

app = Flask(__name__)
camera = None
VISIT_ID = None
TOKEN = None


def init_camera(token=None):
    """Initialise la caméra PiCamera."""
    global camera, VISIT_ID, TOKEN
    TOKEN = token
    try:
        with open("config-camera.json") as f:
            config = json.load(f)
        VISIT_ID = config.get("visitId", "default")
        
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 24
        time.sleep(2)
        print("✅ Caméra initialisée")
    except Exception as e:
        print(f"❌ Erreur initialisation caméra : {e}")
        camera = None


def generate_frames():
    """Génère les frames vidéo pour le streaming."""
    if camera is None:
        return
    
    raw_capture = PiRGBArray(camera, size=(640, 480))
    
    for frame in camera.capture_continuous(
            raw_capture,
            format="bgr",
            use_video_port=True
    ):
        image = frame.array
        buffer = BytesIO()
        
        img = Image.fromarray(image)
        img.save(buffer, format="JPEG")
        jpeg = buffer.getvalue()
        
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + jpeg
            + b"\r\n"
        )
        
        raw_capture.truncate(0)


@app.route("/camera/<visit_id>")
def stream(visit_id):
    """Stream vidéo en direct de la caméra."""
    if visit_id != VISIT_ID or (TOKEN and visit_id != VISIT_ID):
        return "Unauthorized", 403
    
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/take/<visit_id>", methods=["GET"])
def take_photo(visit_id):
    """Prend une photo et la retourne."""
    if visit_id != VISIT_ID or (TOKEN and visit_id != VISIT_ID):
        return "Unauthorized", 403
    
    if camera is None:
        return "Camera not available", 500
    
    filename = f"photo_{visit_id}.jpg"
    camera.capture(filename, format="jpeg")
    
    return send_file(filename, mimetype="image/jpeg")


def start_camera_server(token=None):
    """Démarre le serveur Flask pour la caméra dans un thread daemon."""
    try:
        init_camera(token=token)
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Erreur serveur caméra : {e}")
