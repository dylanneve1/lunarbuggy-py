import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

rover_prompt = "Generate a photorealistic image of lunar surface from ground level"

def generate_lunar_image(output_path, prompt):
    client = genai.Client(api_key="AIzaSyB7kePqZWzoUAUcJE6zLgxQwwVUsUS9UQM")
    contents = prompt
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )
    
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save(output_path)
            print(f"Generated image saved to '{output_path}'")
            return output_path
    print("Failed to generate image.")
    return None
