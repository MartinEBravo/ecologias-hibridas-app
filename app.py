from flask import Flask, render_template, request, url_for

app = Flask(__name__)

import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin

url = "http://127.0.0.1:7860"

# Ruta para la página de inicio
@app.route('/')
def home():
    # Render the initial form
    return render_template('index.html', image_url=None)

# Ruta para la página donde se genera la imagen
@app.route('/generate', methods=['POST'])
def generate_image():
    # Get the input data from the form
    prompt = request.form.get('prompt')

    # Your code for generating images based on the 'prompt' here

    payload = {
        # Ejemplo: "prompt": "joker in the style of 0mib",
        "prompt": f"<lora:0mibNEW:1> {prompt}, realistic",
        # Ejmplo: "negative_prompt": "glass, pedestal, socle, basement, camera, subsurface, underwater, hypermaximalist, diamond, (flowers), water, (leaves), (woman:2), (1girl:2), human, (worst quality:2), (low quality:2), (normal quality:2), border, frame, poorly drawn, childish, hands, hand, ((dof))",
        "negative_prompt": "",
        "height": 512,
        "width": 512,
        "steps": 5
    }

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

    r = response.json()

    image_saved = False  # Variable para rastrear si la imagen se ha guardado correctamente

    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save('static/output.png', pnginfo=pnginfo)
        image_saved = True  # Marcar la imagen como guardada correctamente

    # Después de generar la imagen, proporciona su URL a la plantilla si se ha guardado correctamente
    if image_saved:
        image_url = url_for('static', filename='output.png')  # Generar la URL para la imagen estática
    else:
        image_url = None  # Si no se guardó correctamente, establecer la URL en None

    return render_template('index.html', image_url=image_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

