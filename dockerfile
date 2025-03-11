# Usa una imagen oficial de Python como base
FROM python:3.10

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY api_excel.py .
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que corre FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "api_excel:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
