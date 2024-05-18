# from flask import Flask, request, render_template_string, send_file
# import os
# import sqlite3
# from pytube import YouTube
# from io import BytesIO


# index_html = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Download YouTube Audio</title>
# </head>
# <body>
#     <h1>Download YouTube Audio</h1>
#     <form action="/download" method="post">
#         <label for="url">YouTube URL:</label>
#         <input type="text" id="url" name="url" required>
#         <button type="submit">Download</button>
#     </form>
# </body>
# </html>

# """


# # from flask import Flask

# # app = Flask(__name__)

# # @app.route('/')
# # def home():
# #     return 'Hello, World!'

# # @app.route('/about')
# # def about():
# #     return 'About'



# app = Flask(__name__)

# # Create an in-memory SQLite database
# conn = sqlite3.connect(':memory:', check_same_thread=False)
# c = conn.cursor()
# c.execute('''CREATE TABLE IF NOT EXISTS audios
#              (id INTEGER PRIMARY KEY, audio BLOB)''')

# def download_audio(url):
#     # Create a YouTube object
#     yt = YouTube(url)

#     # Accessing streaming data
#     metadata = yt.streaming_data
#     adaptive_formats_list = metadata.get("adaptiveFormats")

#     # Filter list of dictionaries for audio-only streams
#     audio_streams = [stream for stream in adaptive_formats_list if stream['mimeType'].startswith('audio/')]

#     # Find the audio stream with the highest bitrate
#     highest_quality_stream = max(audio_streams, key=lambda x: x['bitrate'])

#     # Get the itag of the highest quality stream
#     itag = highest_quality_stream['itag']

#     # Download the highest quality audio stream
#     audio_stream = yt.streams.get_by_itag(itag)
#     audio_bytes = audio_stream.stream_to_buffer()
#     return audio_bytes

# @app.route('/')
# def index():
#     return render_template_string(index_html)

# @app.route('/download', methods=['POST'])
# def download():
#     url = request.form['url']
#     audio_bytes = download_audio(url)

#     # Save the audio in the database
#     c.execute("INSERT INTO audios (audio) VALUES (?)", (audio_bytes,))
#     conn.commit()

#     # Retrieve the audio from the database
#     c.execute("SELECT audio FROM audios ORDER BY id DESC LIMIT 1")
#     audio_data = c.fetchone()[0]

#     return send_file(BytesIO(audio_data), mimetype='audio/mp3', as_attachment=True, attachment_filename='highest_quality_audio.mp3')

# if __name__ == '__main__':
#     app.run(debug=False)
from flask import Flask, send_file, render_template_string, request
from pytube import YouTube
import io

app = Flask(__name__)

# Function to download the video and store it in memory
def download_video_to_memory(video_url):
    yt = YouTube(video_url)
    # stream = yt.streams.get_highest_resolution()
    stream = yt.streams.filter(only_audio=True).first()
    video_buffer = io.BytesIO()
    stream.stream_to_buffer(video_buffer)
    video_buffer.seek(0)
    return video_buffer

@app.route('/')
def index():
    return render_template_string('''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>YouTube Video Downloader</title>
      </head>
      <body>
        <div class="container">
          <h1 class="mt-5">Download YouTube Video</h1>
          <form method="post" action="/download">
            <div class="form-group">
              <label for="videoUrl">YouTube Video URL</label>
              <input type="text" class="form-control" id="videoUrl" name="videoUrl" placeholder="Enter YouTube URL">
            </div>
            <button type="submit" class="btn btn-primary">Download</button>
          </form>
        </div>
      </body>
    </html>
    ''')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['videoUrl']
    video_buffer = download_video_to_memory(video_url)
    video_buffer.seek(0)
    return send_file(
        video_buffer,
        as_attachment=True,
        download_name='video.mp4',
        mimetype='video/mp4'
    )

if __name__ == '__main__':
    app.run(debug=True)
