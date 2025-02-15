from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import json
import re
import os
import uvicorn

# Configurar la API key de Gemini
genai.configure(api_key="AIzaSyBgGXl6kjQP_ruptOFecqWalKB_5cIEzzA")

# Seleccionar el modelo de Gemini
model = genai.GenerativeModel("gemini-1.5-flash")

# Inicializar FastAPI
app = FastAPI()

# Definir el esquema de entrada
class SurveyRequest(BaseModel):
    input_text: str

# Función para generar la encuesta
def generate_survey(user_input: str):
    """
    Generates a JSON survey based on the user's request.
    """
    prompt = f"""
    Generate a valid JSON for a SurveyJS survey based on the following user request:
    "{user_input}"

    ⚠️ IMPORTANT:
    - Respond ONLY with the JSON, without explanations or additional text.
    - Do not include text outside the JSON.
    - The JSON must be correct and well-formed.
    - Ensure it includes a title and description.
    """

    response = model.generate_content(prompt)

    if response and response.candidates:
        text_response = response.candidates[0].content.parts[0].text

        try:
            return json.loads(text_response)
        except json.JSONDecodeError:
            json_match = re.search(r'{.*}', text_response, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError as e:
                    return {"error": f"Invalid JSON: {e}"}
            else:
                return {"error": "No valid JSON found in the response."}
    else:
        return {"error": "No valid response received from the model."}

# Ruta para generar la encuesta
@app.post("/generate-survey/")
async def generate_survey_endpoint(request: SurveyRequest):
    return generate_survey(request.input_text)

# Ejecutar el servidor con uvicorn (en entorno de producción)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Usar el puerto proporcionado por Railway o 8000 por defecto
    uvicorn.run(app, host="0.0.0.0", port=port)
