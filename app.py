import subprocess
import uuid
import secrets

from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(
    16)

socketio = SocketIO(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session_id = str(uuid.uuid4())
        session['id'] = session_id

        input_dir = "Z:/data/torrents/music"
        selected_formats = request.form.getlist('formats')
        api_key = ""
        transcode_dir = "Z:/data/torrents/music/tmp/transcodes"
        torrent_dir = "Z:/data/torrents/music/watch"
        spectrogram_dir = "Z:/data/torrents/music/tmp/spectrograms"
        permalink = request.form['permalink']

        for audio_format in selected_formats:
            command = [
                "red_oxide",
                "transcode",
                "--api-key", api_key,
                "--content-directory", input_dir,
                "--transcode-directory", transcode_dir,
                "--torrent-directory", torrent_dir,
                "--spectrogram-directory", spectrogram_dir,
                "--skip-spectrogram",
                "-f", audio_format,
                "-m",
                "-a",
                # "-d",
                permalink
            ]
            socketio.start_background_task(
                target=run_command, command=command, session_id=session_id)

        return render_template('index.html', session_id=session_id)
    else:
        session_id = str(uuid.uuid4())
        session['id'] = session_id
        return render_template('index.html', session_id=session_id)


def run_command(command, session_id):
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
    for line in iter(process.stdout.readline, ''):
        socketio.emit('command_output', {'data': line}, to=session_id)
    for line in iter(process.stderr.readline, ''):
        socketio.emit('command_output', {'data': line}, to=session_id)
    process.stdout.close()
    process.stderr.close()
    process.wait()


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('join')
def on_join(data):
    session_id = data['session_id']
    join_room(session_id)


@socketio.on('leave')
def on_leave(data):
    session_id = data['session_id']
    leave_room(session_id)


if __name__ == '__main__':
    socketio.run(app, debug=True)
