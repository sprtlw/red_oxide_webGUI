from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_dir = "/data/torrents/music"
        selected_formats = request.form.getlist('formats')
        api_key = os.environ.get('RED_API')
        transcode_dir = "/config/transcodes"
        torrent_dir = "/data/torrents/music/watch"
        spectrogram_dir = "/config/spectrogram"
        permalink = request.form['url']

        for audio_format in selected_formats:
            command = [
                "red_oxide",
                "transcode",
                "--api-key", api_key,
                "--content-directory", input_dir,
                "--transcode-directory", transcode_dir,
                "--torrent-directory", torrent_dir,
                "--spectrogram-directory", spectrogram_dir,
                "-f", audio_format,
                "-m",
                "-d",
                permalink
            ]
            subprocess.run(command)
            output = subprocess.check_output(command, universal_newlines=True)

        return render_template('index.html', console_output=output)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
