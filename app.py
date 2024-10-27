from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
from hashlib import sha256
import re

app = Flask(__name__)

# Directory to save downloaded files
DOWNLOADS_DIR = "/downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


# Clean the title to make it safe for filenames
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title)


# Download and convert video to MP3
def download_mp3(url):
    # Use yt-dlp to extract the video title
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = sanitize_filename(info.get("title", "downloaded_video"))

    # Create a unique file path using the title
    output_path = f"{DOWNLOADS_DIR}/{title}"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    # Download and convert to MP3
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return f"{output_path}.mp3"


# Route to handle download requests
@app.route('/download', methods=['GET'])
def download():
    # Check for either 'url' or 'id' parameters
    url = request.args.get("url")
    video_id = request.args.get("id")

    if not url and not video_id:
        return jsonify({"error": "URL or video ID parameter is required"}), 400

    # Construct the full YouTube URL if only video_id is provided
    if video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        # Download the MP3 file with the video title as filename
        mp3_file = download_mp3(url)

        # List files in the downloads directory for debugging
        files_in_directory = os.listdir(DOWNLOADS_DIR)
        print("Files in downloads directory:", files_in_directory)

        return send_file(mp3_file, as_attachment=True, download_name=os.path.basename(mp3_file))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
