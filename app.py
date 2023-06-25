from flask import Flask, render_template, Response
from camera import VideoCamera
import cv2
import cvzone.HandTrackingModule as handTracking
import math
import numpy as np

app = Flask(__name__)

DETECTION_CONFIDENCE = 0.8
NO_OF_HANDS = 1

TEXT_COLOUR = (255, 255, 255)
PURPLE = (255, 0, 255)
GREEN = (0, 255, 0)
NAVY_BLUE = (175, 0, 175)

HORIZONTAL_OFFSET = 20
VERTICAL_OFFSET = 65
FONT_SIZE = 4
BUTTON_SIZE = [85, 85]
TEXT_BOX_FONT = 5
BOX_COOR = [(50, 350), (700, 450), (60, 425)]
Resolution_w, Resolution_h = 1280, 720

video_feed = cv2.VideoCapture(0)
video_feed.set(3, Resolution_w)
video_feed.set(4, Resolution_h)

handDetector = handTracking.HandDetector(
    detectionCon=DETECTION_CONFIDENCE, maxHands=NO_OF_HANDS)
list_buttons = []

qwerty_layout = {
    "1": ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    "2": ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    "3": ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "<"]
}
qwerty_keyboard = [qwerty_layout["1"], qwerty_layout["2"], qwerty_layout["3"]]


class Buttons():
    def __init__(self, position, txt, size=BUTTON_SIZE):
        self.size = size
        self.location = position
        self.data = txt


x = 0
while x < len(qwerty_keyboard):
    j = 0
    while j < len(qwerty_keyboard[x]):
        key = qwerty_keyboard[x][j]
        list_buttons.append(Buttons([100 * j + 50, 100 * x + 50], key))
        j += 1
    x += 1


def display_buttons(image, list_buttons):
    i = 0
    while i < len(list_buttons):
        b = list_buttons[i]
        horizontal, vertical = b.location
        width, height = b.size
        cv2.rectangle(image, b.location, (horizontal + width, vertical + height), PURPLE, cv2.FILLED)
        cv2.putText(image, b.data, (horizontal + HORIZONTAL_OFFSET, vertical + VERTICAL_OFFSET),
                    cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOUR, FONT_SIZE)
        i += 1
    return image


def gen(camera):
    textbox_string = ""  # Initialize textbox_string variable
    while True:
        frame = camera.get_frame()
        image = cv2.imdecode(np.frombuffer(frame, np.uint8), -1)
        image = cv2.flip(image, 1)

        hands, bbox_Info = handDetector.findHands(image, draw=True)
        image = display_buttons(image, list_buttons)

        if hands:
            hand = hands[0]
            lm_List = hand["lmList"]
            for b in list_buttons:
                horizontal, vertical = b.location
                width, height = b.size
                if horizontal < lm_List[8][0] < horizontal + width and vertical < lm_List[8][1] < vertical + height:
                    cv2.rectangle(image, b.location, (horizontal + width, vertical + height), NAVY_BLUE, cv2.FILLED)
                    cv2.putText(image, b.data, (horizontal + HORIZONTAL_OFFSET, vertical + VERTICAL_OFFSET),
                                cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOUR, FONT_SIZE)

                    l = math.hypot(lm_List[8][0] - lm_List[12][0], lm_List[8][1] - lm_List[12][1])
                    if l < 35:
                        cv2.rectangle(image, b.location, (horizontal + width, vertical + height), GREEN, cv2.FILLED)
                        cv2.putText(image, b.data, (horizontal + HORIZONTAL_OFFSET, vertical + VERTICAL_OFFSET),
                                    cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOUR, FONT_SIZE)

                        textbox_string += b.data

            fingertips = []
            for h in hands:
                for i, l in enumerate(h["lmList"]):
                    if i in [4, 12, 8, 20, 16]:
                        fingertips.append(l)

            for tip in fingertips:
                cv2.circle(image, tip[:2], 10, (0, 255, 0), cv2.FILLED)

        cv2.rectangle(image, BOX_COOR[0], BOX_COOR[1], NAVY_BLUE, cv2.FILLED)
        cv2.putText(image, textbox_string, BOX_COOR[2], cv2.FONT_HERSHEY_PLAIN, TEXT_BOX_FONT, TEXT_COLOUR,
                    TEXT_BOX_FONT)

        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run()
