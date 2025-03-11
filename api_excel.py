from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import re
import io
import os

app = FastAPI()

# Función para limpiar nombres de columnas
def limpiar_nombre_columna(nombre):
    return re.sub(r'[^a-z]', '', nombre.lower())

# Modelo para recibir respuestas con 40 entradas predefinidas en Swagger
class RespuestasInput(BaseModel):
    respuestas: list[str] = ["a", "b", "c", "d"] * 10  # 40 respuestas predefinidas

@app.post("/subir_excel/")
async def subir_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        excel_data = io.BytesIO(contents)  
        df = pd.read_excel(excel_data)

        # Limpiar nombres de columnas
        df.columns = [limpiar_nombre_columna(col) for col in df.columns]

        # Filtrar solo las columnas 'pregunta' y 'respuesta'
        columnas_deseadas = ['pregunta', 'respuesta']
        df = df[[col for col in columnas_deseadas if col in df.columns]]

        # Convertir la columna 'respuesta' a minúsculas
        if 'respuesta' in df.columns:
            df['respuesta'] = df['respuesta'].astype(str).str.lower()

        df.to_csv("preguntas_respuestas.csv", index=False)

        return {"message": "Archivo subido y procesado correctamente.", "total_preguntas": len(df)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/enviar_respuestas/")
async def enviar_respuestas(data: RespuestasInput):
    try:
        df = pd.read_csv("preguntas_respuestas.csv")

        if len(data.respuestas) != len(df):
            raise HTTPException(status_code=400, detail="La cantidad de respuestas no coincide con la cantidad de preguntas.")

        # Validar respuestas solo permiten 'a', 'b', 'c', 'd'
        respuestas_validas = {'a', 'b', 'c', 'd'}
        data.respuestas = [r.lower() for r in data.respuestas]

        if not all(r in respuestas_validas for r in data.respuestas):
            raise HTTPException(status_code=400, detail="Todas las respuestas deben ser 'a', 'b', 'c' o 'd'.")

        df['respuesta_usuario'] = data.respuestas

        # Filtrar respuestas incorrectas y solo mantener la columna "pregunta"
        respuestas_incorrectas = df[df['respuesta'] != df['respuesta_usuario']][['pregunta']]

        # Guardar solo la columna "pregunta" en el archivo
        file_path = "respuestas_incorrectas.xlsx"
        respuestas_incorrectas.to_excel(file_path, index=False)

        # Devolver el archivo de respuestas incorrectas directamente
        return FileResponse(
            path=file_path,
            filename="respuestas_incorrectas.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
