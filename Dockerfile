# Option multi-stage build pour un conteneur léger et rapide
FROM python:3.11-slim as builder

# Définition du répertoire de travail
WORKDIR /app

# Empêcher Python d'écrire des fichiers .pyc et forcer l'affichage immédiat des logs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Installation des dépendances système de base
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Ajout de Poetry au PATH
ENV PATH="/root/.local/bin:$PATH"

# Copie uniquement des fichiers de dépendances pour maximiser la mise en cache Docker
COPY pyproject.toml poetry.lock* ./

# Installation des dépendances du projet
RUN poetry install --no-root --no-dev

# ----------------------------------------------------
# Stage Final
# ----------------------------------------------------
FROM python:3.11-slim as runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Copie de l'environnement virtuel depuis le builder
COPY --from=builder /app/.venv /app/.venv

# Copie du code source de l'application
COPY src/ ./src/
COPY data/ ./data/

# Commande par défaut lors du démarrage du conteneur : exécute le script d'évaluation
CMD ["python", "-c", "from src.evaluate import evaluer_pipeline; evaluer_pipeline('data/golden_dataset.csv', None, None)"]