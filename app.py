from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_dir = "Z:/data/torrents/music"
        selected_formats = request.form.getlist('formats')
        api_key = ""
        transcode_dir = "Z:/data/torrents/music/tmp/transcodes"
        torrent_dir = "Z:/data/torrents/music/watch"
        spectrogram_dir = "Z:/data/torrents/music/tmp/spectrograms"
        permalink = request.form['permalink']

        command_output = ""
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
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True, encoding='utf-8', errors='replace', env=os.environ)
                command_output += (result.stdout or "") + (result.stderr or "")
            except Exception as e:
                command_output += str(e)

        return render_template('index.html', console_output=command_output)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
