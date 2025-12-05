# 1. Imagen base: Usamos Python 3.11 slim
FROM python:3.11-slim

# 2. Configurar el entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# 4. Copiar los archivos de dependencias
COPY requirements.txt /usr/src/app/

# 5. Instalar dependencias del backend
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# 6. Copiar el código fuente de Django (tu API)
COPY . /usr/src/app/

# 7. Comando predeterminado para iniciar Gunicorn (servidor de producción)
CMD ["gunicorn", "hospital_project.wsgi:application", "--bind", "0.0.0.0:8000"]