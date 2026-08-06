from flask import Flask, Response
from picamera import PiCamera
from picamera.array import PiRGBArray
import json
import time
from PIL import Image
from io import BytesIO


app = Flask(__name__)


with open("config.json") as f:
    config = json.load(f)


VISIT_ID = config["visitId"]


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24


time.sleep(2)


def generate_frames():

    raw_capture = PiRGBArray(
        camera,
        size=(640, 480)
    )

    for frame in camera.capture_continuous(
        raw_capture,
        format="bgr",
        use_video_port=True
    ):

        image = frame.array

        buffer = BytesIO()

        img = Image.fromarray(
            image
        )

        img.save(
            buffer,
            format="JPEG"
        )

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

    if visit_id != VISIT_ID:
        return "Unauthorized", 403


    return Response(
        generate_frames(),
        mimetype=
        "multipart/x-mixed-replace; boundary=frame"
    )



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
