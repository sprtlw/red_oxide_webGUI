import subprocess
import uuid
import secrets
from discord_webhook import DiscordWebhook, DiscordEmbed

from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room
from decouple import config

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

socketio = SocketIO(app)

# In-memory storage for URLs
url_list = []


@app.route('/add_url', methods=['POST'])
def add_url():
    data = request.get_json()
    new_url = data.get('url')
    if new_url:
        url_list.append(new_url)
    return jsonify(url_list=url_list)


@app.route('/remove_url', methods=['POST'])
def remove_url():
    data = request.get_json()
    url_to_remove = data.get('url')
    if url_to_remove in url_list:
        url_list.remove(url_to_remove)
    return jsonify(url_list=url_list)


def process_urls_and_run_commands(api_key, input_dir, transcode_dir, torrent_dir, spectrogram_dir, selected_formats, session_id):
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
        command.extend(["-m", "-a", url])
        # Start background task to run command
        socketio.start_background_task(
            target=run_command, command=command, session_id=session_id)

    # Clear URL list after processing
    url_list.clear()


@app.route('/start_transcode', methods=['POST'])
def start_transcode():
    session_id = str(uuid.uuid4())
    session['id'] = session_id

    input_dir = "/data/torrents/music"
    selected_formats = request.form.getlist('formats')
    api_key = config('API_KEY')
    transcode_dir = "/data/torrents/music/tmp/transcodes"
    torrent_dir = "/data/torrents/music/watch"
    spectrogram_dir = "/data/torrents/music/tmp/spectrograms"

    # Process the submitted URLs and run commands for transcoding
    process_urls_and_run_commands(
        api_key, input_dir, transcode_dir, torrent_dir, spectrogram_dir, selected_formats, session_id)

    return render_template('index.html', session_id=session_id, url_list=url_list)


@app.route('/', methods=['GET'])
def index():
    # Generate a new session ID for GET requests
    session_id = str(uuid.uuid4())
    session['id'] = session_id
    return render_template('index.html', session_id=session_id, url_list=url_list)


def run_command(command, session_id):
    # Run subprocess command
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')

    # Setup Discord Webhook
    webhook_url = config('DISCORD_WEBHOOK_URL')
    webhook = DiscordWebhook(url=webhook_url, content="Process started")
    webhook.execute()

    # Read and emit command output to session
    for line in process.stdout:
        embed = DiscordEmbed(title="Command Output", description=line)
        webhook.add_embed(embed)
        webhook.execute()
        socketio.emit('command_output', {'data': line}, to=session_id)

    for line in process.stderr:
        embed = DiscordEmbed(title="Command Error", description=line)
        webhook.add_embed(embed)
        webhook.execute()
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
