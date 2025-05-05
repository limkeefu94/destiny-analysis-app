from PIL import Image
import os

def compress_image(input_path, output_path, quality=80):
    img = Image.open(input_path)
    img.save(output_path, optimize=True, quality=quality)

os.makedirs("static/images/optimized", exist_ok=True)
for img in os.listdir("static/images"):
    input_path = f"static/images/{img}"
    output_path = f"static/images/optimized/{img}"
    compress_image(input_path, output_path)