from flask import Flask, request, render_template_string, send_file
import os
import sqlite3
from pytube import YouTube
from io import BytesIO


index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download YouTube Audio</title>
</head>
<body>
    <h1>Download YouTube Audio</h1>
    <form action="/download" method="post">
        <label for="url">YouTube URL:</label>
        <input type="text" id="url" name="url" required>
        <button type="submit">Download</button>
    </form>
</body>
</html>

"""


# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return 'Hello, World!'

# @app.route('/about')
# def about():
#     return 'About'



app = Flask(__name__)

# Create an in-memory SQLite database
conn = sqlite3.connect(':memory:', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS audios
             (id INTEGER PRIMARY KEY, audio BLOB)''')

def download_audio(url):
    # Create a YouTube object
    yt = YouTube(url)

    # Accessing streaming data
    metadata = yt.streaming_data
    adaptive_formats_list = metadata.get("adaptiveFormats")

    # Filter list of dictionaries for audio-only streams
    audio_streams = [stream for stream in adaptive_formats_list if stream['mimeType'].startswith('audio/')]

    # Find the audio stream with the highest bitrate
    highest_quality_stream = max(audio_streams, key=lambda x: x['bitrate'])

    # Get the itag of the highest quality stream
    itag = highest_quality_stream['itag']

    # Download the highest quality audio stream
    audio_stream = yt.streams.get_by_itag(itag)
    audio_bytes = audio_stream.stream_to_buffer()
    return audio_bytes

@app.route('/')
def index():
    return render_template_string(index_html)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    audio_bytes = download_audio(url)

    # Save the audio in the database
    c.execute("INSERT INTO audios (audio) VALUES (?)", (audio_bytes,))
    conn.commit()

    # Retrieve the audio from the database
    c.execute("SELECT audio FROM audios ORDER BY id DESC LIMIT 1")
    audio_data = c.fetchone()[0]

    return send_file(BytesIO(audio_data), mimetype='audio/mp3', as_attachment=True, attachment_filename='highest_quality_audio.mp3')

if __name__ == '__main__':
    app.run(debug=False)
