from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from transformers import pipeline
import PyPDF2
import docx
from youtube_transcript_api import YouTubeTranscriptApi
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
CORS(app)

# 🔥 REAL AI MODEL (BART)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# 📄 PDF reader
def extract_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() or "" for p in reader.pages])

# 📝 DOCX reader
def extract_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

# 🎥 YouTube transcript
def extract_youtube(url):
    try:
        video_id = re.search(r"(?:v=|youtu.be/)([a-zA-Z0-9_-]+)", url).group(1)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t['text'] for t in transcript])
    except:
        return "Transcript not available for this video."

# 📥 Create PDF
def create_pdf(text):
    file = "output.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(text, styles["Normal"])])
    return file

# 📥 Create DOCX
def create_docx(text):
    file = "output.docx"
    doc = docx.Document()
    doc.add_paragraph(text)
    doc.save(file)
    return file

# 🌐 Home
@app.route("/")
def home():
    return render_template("index.html")

# 🚀 Main API
@app.route("/process", methods=["POST"])
def process():
    try:
        text = ""

        # 📁 FILE INPUT
        if request.files:
            file = request.files['file']

            if file.filename.endswith(".pdf"):
                text = extract_pdf(file)

            elif file.filename.endswith(".docx"):
                text = extract_docx(file)

            else:
                return jsonify({"output": "Unsupported file format!"})

        # 📄 TEXT / YOUTUBE
        else:
            data = request.json

            if data.get("type") == "text":
                text = data.get("content")

            elif data.get("type") == "youtube":
                text = extract_youtube(data.get("content"))

        # ❗ No content
        if not text.strip():
            return jsonify({"output": "No content found!"})

        # ⚠️ BART LIMIT
        text = text[:1024]

        # 🧠 SUMMARIZATION (REAL AI)
        result = summarizer(
            text,
            max_length=150,
            min_length=40,
            do_sample=False
        )

        output = result[0]['summary_text']

        # 📥 Create downloadable files
        create_pdf(output)
        create_docx(output)

        return jsonify({
            "output": output,
            "pdf": "/download/pdf",
            "docx": "/download/docx"
        })

    except Exception as e:
        return jsonify({"output": "Error: " + str(e)})

# 📥 Download routes
@app.route("/download/pdf")
def download_pdf():
    return send_file("output.pdf", as_attachment=True)

@app.route("/download/docx")
def download_docx():
    return send_file("output.docx", as_attachment=True)

# ▶ Run
if __name__ == "__main__":
    app.run(debug=True)