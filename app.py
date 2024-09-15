import os
import json
import openai
import openrouter
from flask import Flask, request, send_file
from PIL import Image
import io

app = Flask(__name__)

# Configure API keys
openai.api_key = os.getenv('OPENAI_API_KEY')
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    # Get the uploaded file
    file = request.files['file']

    # Process the file using OCR
    if file.filename.endswith('.pdf'):
        text = process_pdf_ocr(file)
    elif file.filename.endswith(('.png', '.jpg', '.jpeg')):
        text = process_image_ocr(file)
    else:
        return 'Unsupported file type', 400

    # Save the OCR output
    output_file = f'{file.filename.split(".")[0]}.txt'
    with open(output_file, 'w') as f:
        f.write(text)

    return send_file(output_file, as_attachment=True)

def process_pdf_ocr(file):
    # Use OpenAI to perform OCR on the PDF
    image = Image.open(io.BytesIO(file.read()))
    text = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Perform OCR on the following image: {image}",
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.5,
    ).choices[0].text

    return text

def process_image_ocr(file):
    # Use Openrouter to perform OCR on the image
    image = Image.open(io.BytesIO(file.read()))
    text = openrouter.predict(image, api_key=openrouter_api_key)
    return text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)