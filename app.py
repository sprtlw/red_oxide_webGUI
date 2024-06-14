import subprocess
import uuid
import secrets
import json

from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room
from decouple import config

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(
    16)

socketio = SocketIO(app)

# File to store URLs
URL_FILE = 'urls.json'


def read_urls():
    try:
        with open(URL_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def write_urls(urls):
    with open(URL_FILE, 'w', encoding='utf-8') as file:
        json.dump(urls, file)


@app.route('/add_url', methods=['POST'])
def add_url():
    data = request.get_json()
    new_url = data.get('url')
    if new_url:
        url_list = read_urls()
        url_list.append(new_url)
        write_urls(url_list)
    return jsonify(url_list=url_list)


@app.route('/remove_url', methods=['POST'])
def remove_url():
    data = request.get_json()
    url_to_remove = data.get('url')
    url_list = read_urls()
    if url_to_remove in url_list:
        url_list.remove(url_to_remove)
        write_urls(url_list)
    return jsonify(url_list=url_list)


def process_urls_and_run_commands(api_key, input_dir, transcode_dir, torrent_dir, spectrogram_dir, selected_formats, session_id):
    # Read URL list
    url_list = read_urls()

    # Loop through URL list and create command
    for url in url_list:
        command = [
            "red_oxide",
            "transcode",
            "--api-key", api_key,
            "--content-directory", input_dir,
            "--transcode-directory", transcode_dir,
            "--torrent-directory", torrent_dir,
            "--spectrogram-directory", spectrogram_dir,
            "--skip-spectrogram",
        ]
        for file_format in selected_formats:
            command.extend(["-f", file_format])
        command.extend(["-m", "-a", "-d", url])
        print(command)
        # Start background task to run command
        socketio.start_background_task(
            target=run_command, command=command, session_id=session_id)

    # Clear URL list after processing
    url_list.clear()
    write_urls(url_list)


@app.route('/', methods=['GET', 'POST'])
def index():
    # Generate a unique session ID for each request
    if request.method == 'POST':
        session_id = str(uuid.uuid4())
        session['id'] = session_id

        input_dir = "Z:/data/torrents/music"
        selected_formats = request.form.getlist('formats')
        api_key = config('API_KEY')
        transcode_dir = "Z:/data/torrents/music/tmp/transcodes"
        torrent_dir = "Z:/data/torrents/music/watch"
        spectrogram_dir = "Z:/data/torrents/music/tmp/spectrograms"

        # Process the submitted URLs and run commands for transcoding
        process_urls_and_run_commands(
            api_key, input_dir, transcode_dir, torrent_dir, spectrogram_dir, selected_formats, session_id)

        return render_template('index.html', session_id=session_id)
    else:
        # Generate a new session ID for GET requests
        session_id = str(uuid.uuid4())
        session['id'] = session_id
        url_list = read_urls()
        return render_template('index.html', session_id=session_id, url_list=url_list)


def run_command(command, session_id):
    # Run subprocess command
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')

    # Read and emit command output to session
    for line in process.stdout:
        print(line)
        socketio.emit('command_output', {'data': line}, to=session_id)

    for line in process.stderr:
        print(line)
        socketio.emit('command_output', {'data': line}, to=session_id)

    process.wait()


@socketio.on('connect')
def handle_connect():
    # Handle client connection
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    # Handle client disconnection
    print('Client disconnected')


@socketio.on('join')
def on_join(data):
    # Join a room
    session_id = data['session_id']
    join_room(session_id)


@socketio.on('leave')
def on_leave(data):
    # Leave a room
    session_id = data['session_id']
    leave_room(session_id)


if __name__ == '__main__':
    socketio.run(app, debug=True)
