import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Response, jsonify, abort
from picamera2 import Picamera2
from libcamera import Transform
from pyzbar.pyzbar import decode
import os
import requests
import time
import threading
import cv2
import atexit
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

camera = None
latest_data = None
fetched_data = "Scanning..."

def start_camera():
    global camera
    if camera is None:
        camera = Picamera2()
        camera.configure(camera.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}, transform=Transform(vflip=False)))
        camera.start()

def stop_camera():
    global camera
    if camera:
        camera.stop()
        camera.close()
        camera = None


def handle_qr_data(latest_data):
    global fetched_data

    parsed_url = urllib.parse.urlparse(latest_data)

    if parsed_url.scheme and parsed_url.scheme.lower() not in ['http', 'https']:
        error_message = f"Invalid protocol detected: {parsed_url.scheme}. Only 'http' or 'https' are allowed."
        print(error_message)
        fetched_data = error_message
        time.sleep(0.3)
        return

    try:
        response = requests.get(latest_data)
        response.raise_for_status()
        print("Success:",response.status_code)
        fetched_data = response.text
        time.sleep(0.3)
    except Exception as e:
        print(f"An error occurred: {e}")
        fetched_data = str(e)
        time.sleep(0.3)


def generate_frames():
    global latest_data
    try:
        while True:
            frame = camera.capture_array()

            decoded_objects = decode(frame)
            for obj in decoded_objects:

                (x, y, w, h) = obj.rect
                cv2.rectangle(frame, (x, y), (x+w, y+h), (60, 20, 220), 2)
                qr_data = obj.data.decode('UTF-8')

                if latest_data != qr_data:
                    latest_data = qr_data
                    print(f"Data detected: {latest_data}")
                    handle_qr_data(latest_data)


            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        stop_camera()


@app.route('/data')
def get_data():
    return Response(fetched_data, mimetype='text/plain')

@app.route('/video_feed')
def video_feed():
    start_camera()
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('/home/raspberry/kawaiicon_box/webapp/static/user.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM USERS WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials'
            return render_template('login.html', error=error)


    resp = make_response(render_template('login.html'))
    resp.set_cookie('sessions', 'guest_sess_001')
    return resp

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])


    sess_id = request.cookies.get('sessions', '')

    conn = sqlite3.connect('/home/raspberry/kawaiicon_box/static/user.db')
    cursor = conn.cursor()

    try:
        query = f"SELECT * FROM USERS WHERE SESSION = '{sess_id}'"
        cursor.execute(query)
        user = cursor.fetchone()
    except Exception as e:
        user = None
    conn.close()

    if user:
        return render_template('dashboard.html', username=user[0])
    else:
        return redirect(url_for('login'))

@app.route('/system_configuration', methods=['GET'])
def system_configuration():
    if request.remote_addr not in ['127.0.0.1', '::1']:
        abort(403)
    return jsonify({'PIN Code': 123})



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



atexit.register(stop_camera)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)