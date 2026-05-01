import cv2
import time
import numpy as np
from flask import Flask, request, jsonify
import base64
import HandTrackingModule as htm
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# ----------------------------
# INIT DETECTOR (unchanged logic)
# ----------------------------
detector = htm.handDetector(detectionCon=0)


# ----------------------------
# HEALTH CHECK (RENDER FIX)
# ----------------------------
@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "message": "Sign Language API is live 🚀"
    })


# ----------------------------
# IMAGE UPLOAD API
# ----------------------------
@app.route('/upload', methods=['POST'])
def upload_image():
    start_time = time.time()

    try:
        data = request.get_json()
        image_data = data.get('image', None)

        if not image_data:
            return jsonify({"message": "No image data received"}), 400

        # Decode image
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"message": "Invalid image"}), 400

        # Process hand detection
        img = detector.findHands(img)
        posList = detector.findPosition(img, draw=False)

        if posList is None or len(posList) < 21:
            return jsonify({"message": "No hand detected"}), 200

        result = recognize_gesture(posList)

        print("Processing time:", round(time.time() - start_time, 2), "sec")

        return jsonify({"message": result})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "message": "Server error",
            "error": str(e)
        }), 500


# ----------------------------
# YOUR FULL GESTURE LOGIC (UNCHANGED)
# ----------------------------
def recognize_gesture(posList):
    result = ""
    fingers = []

    finger_mcp = [5, 9, 13, 17]
    finger_dip = [6, 10, 14, 18]
    finger_pip = [7, 11, 15, 19]
    finger_tip = [8, 12, 16, 20]

    for id in range(4):
        if (posList[finger_tip[id]][1] + 25 < posList[finger_dip[id]][1] and
            posList[16][2] < posList[20][2]):
            fingers.append(0.25)

        elif posList[finger_tip[id]][2] > posList[finger_dip[id]][2]:
            fingers.append(0)

        elif posList[finger_tip[id]][2] < posList[finger_pip[id]][2]:
            fingers.append(1)

        elif (posList[finger_tip[id]][1] > posList[finger_pip[id]][1] and
              posList[finger_tip[id]][1] > posList[finger_dip[id]][1]):
            fingers.append(0.5)

    # ----------------------------
    # YOUR ORIGINAL CONDITIONS (FULL RESTORED)
    # ----------------------------

    if (posList[3][2] > posList[4][2]) and (posList[3][1] > posList[6][1]) and (posList[4][2] < posList[6][2]) and fingers.count(0) == 4:
        result = "A"

    elif (posList[3][1] > posList[4][1]) and fingers.count(1) == 4:
        result = "B"

    elif (posList[3][1] > posList[6][1]) and fingers.count(0.5) >= 1 and (posList[4][2] > posList[8][2]):
        result = "C"

    elif (fingers[0] == 1) and fingers.count(0) == 3 and (posList[3][1] > posList[4][1]):
        result = "D"

    elif (posList[3][1] < posList[6][1]) and fingers.count(0) == 4 and posList[12][2] < posList[4][2]:
        result = "E"

    elif (fingers.count(1) == 3) and (fingers[0] == 0) and (posList[3][2] > posList[4][2]):
        result = "F"

    elif (fingers[0] == 0.25) and fingers.count(0) == 3:
        result = "G"

    elif (fingers[0] == 0.25) and (fingers[1] == 0.25) and fingers.count(0) == 2:
        result = "H"

    elif (posList[4][1] < posList[6][1]) and fingers.count(0) == 3:
        if (len(fingers) == 4 and fingers[3] == 1):
            result = "I"

    elif (posList[4][1] < posList[6][1] and posList[4][1] > posList[10][1] and fingers.count(1) == 2):
        result = "K"

    elif (fingers[0] == 1) and fingers.count(0) == 3 and (posList[3][1] < posList[4][1]):
        result = "L"

    elif (posList[4][1] < posList[16][1]) and fingers.count(0) == 4:
        result = "M"

    elif (posList[4][1] < posList[12][1]) and fingers.count(0) == 4:
        result = "N"

    elif (posList[4][1] > posList[12][1]) and posList[4][2] < posList[6][2] and fingers.count(0) == 4:
        result = "T"

    elif (posList[4][1] > posList[12][1]) and posList[4][2] < posList[12][2] and fingers.count(0) == 4:
        result = "S"

    elif (posList[4][2] < posList[8][2]) and (posList[4][2] < posList[12][2]) and (posList[4][2] < posList[16][2]) and (posList[4][2] < posList[20][2]):
        result = "O"

    elif (fingers[2] == 0) and (posList[4][2] < posList[12][2]) and (posList[4][2] > posList[6][2]):
        if (len(fingers) == 4 and fingers[3] == 0):
            result = "P"

    elif (fingers[1] == 0) and (fingers[2] == 0) and (fingers[3] == 0) and (posList[8][2] > posList[5][2]) and (posList[4][2] < posList[1][2]):
        result = "Q"

    elif (posList[8][1] < posList[12][1]) and (fingers.count(1) == 2) and (posList[9][1] > posList[4][1]):
        result = "R"

    elif (posList[4][1] < posList[6][1] and posList[4][1] < posList[10][1] and fingers.count(1) == 2 and posList[3][2] > posList[4][2] and (posList[8][1] - posList[11][1]) <= 50):
        result = "U"

    elif (posList[4][1] < posList[6][1] and posList[4][1] < posList[10][1] and fingers.count(1) == 2 and posList[3][2] > posList[4][2]):
        result = "V"

    elif (posList[4][1] < posList[6][1] and posList[4][1] < posList[10][1] and fingers.count(1) == 3):
        result = "W"

    elif (fingers[0] == 0.5 and fingers.count(0) == 3 and posList[4][1] > posList[6][1]):
        result = "X"

    elif (fingers.count(0) == 3) and (posList[3][1] < posList[4][1]):
        if (len(fingers) == 4 and fingers[3] == 1):
            result = "Y"

    return result


# ----------------------------
# RUN SERVER (RENDER SAFE)
# ----------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
