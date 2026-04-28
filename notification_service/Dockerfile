FROM python:3.9-slim

WORKDIR /app

# Mettre à jour pip d'abord
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .

# Afficher le contenu de requirements.txt pour debug
RUN cat requirements.txt

# Installer avec verbose pour voir l'erreur
RUN pip install --no-cache-dir -r requirements.txt -v

COPY . .

EXPOSE 5000

CMD ["python", "manage.py", "runserver", "0.0.0.0:5000"]