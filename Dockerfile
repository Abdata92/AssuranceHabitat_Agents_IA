FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential git \
    && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN pip install poetry

# Copie des fichiers de configuration du projet
COPY pyproject.toml poetry.lock /app/

# Installation des dépendances Python
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copie du code source et des données
COPY src/ /app/src/
COPY data/ /app/data/

EXPOSE 8000

# Lancement du serveur d'API Uvicorn
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]