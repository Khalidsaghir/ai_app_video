import os
import base64
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from runway_client import text_to_video
import firebase_admin
from firebase_admin import credentials, storage
import requests

# ------------------ Flask App ------------------
app = Flask(__name__)
CORS(app)

# ------------------ Firebase Init ------------------
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    "storageBucket": "ap-app-b6420.appspot.com"  # Use your bucket name here
})
bucket = storage.bucket()

GEMINI_API_KEY = "AIzaSyDnkIugSFNbrZAzMynL5212k1ZeOJzaVS8"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def generate_images(prompt, num_images=5, size="1024x1024"):
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    payload = {
        "prompt": prompt,
        "image_count": num_images,
        "size": size
    }
    response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Gemini API Error: {response.text}")
    result = response.json()

    os.makedirs("output", exist_ok=True)
    image_paths = []

    for i, img in enumerate(result.get("images", [])):
        img_base64 = img.get("image")
        if not img_base64:
            continue
        img_path = os.path.join("output", f"img_{i}.png")
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(img_base64))
        image_paths.append(img_path)

    if not image_paths:
        raise Exception("No images generated")

    return image_paths

# ------------------ Routes ------------------
@app.route("/")
def home():
    # Serve main.html from the parent ai_app directory
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.html"))
    if not os.path.exists(html_path):
        return "<h3>main.html not found!</h3>", 404
    return send_file(html_path)

@app.route("/generate", methods=["POST"])
def generate():
    import traceback
    try:
        prompt = request.form.get("prompt", "Epic cinematic AI video")
        num_images = int(request.form.get("num_images", 5))
        fps = int(request.form.get("fps", 6))
        size = request.form.get("size", "1024x1024")

        print(f"[DEBUG] Prompt: {prompt}, Num Images: {num_images}, FPS: {fps}, Size: {size}")

        # Generate images
        images = generate_images(prompt, num_images, size)
        print(f"[DEBUG] Generated images: {images}")

        # Convert images to video
        video_path = text_to_video(images, fps=fps)
        print(f"[DEBUG] Video path: {video_path}")

        # Upload video to Firebase
        blob = bucket.blob(os.path.basename(video_path))
        blob.upload_from_filename(video_path)
        blob.make_public()
        video_url = blob.public_url
        print(f"[DEBUG] Video URL: {video_url}")

        return jsonify({"video_url": video_url})

    except Exception as e:
        print("[ERROR] Exception in /generate route:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join("output", filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=False)

# ------------------ Run ------------------
if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    app.run(host="127.0.0.1", port=5000, debug=True)
