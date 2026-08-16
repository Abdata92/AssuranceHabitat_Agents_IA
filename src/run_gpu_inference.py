import pandas as pd
from langchain_ollama import ChatOllama
from src.evaluate import evaluer_pipeline

print("--- Initialisation des modèles sur GPU (Mistral 7B + LLaVA) ---")

# LLM Texte pour Déclaration et Validation
llm_gpu = ChatOllama(
    model="mistral",
    temperature=0.0
)

# VLM Vision pour l'Expertise (LLaVA)
vlm_gpu = ChatOllama(
    model="llava",
    temperature=0.0
)

print("--- Inférence réelle en cours sur le Golden Dataset ---")

df_results = evaluer_pipeline(
    csv_path="data/golden_dataset.csv",
    llm_model=llm_gpu,
    vlm_model=vlm_gpu
)

print("\n--- Résultats enregistrés dans data/evaluation_results.csv ---")
