import pandas as pd
from langchain_ollama import ChatOllama
from src.evaluate import evaluer_pipeline

print("--- Initialisation des modèles sur GPU ---")

llm_gpu = ChatOllama(
    model= "mistral", #"llama3.2", 
    temperature=0.0
    )
vlm_gpu = ChatOllama(
    model="llama3.2-vision", 
    temperature=0.0
    )

print("--- Inférence réelle en cours sur le Golden Dataset ---")

df_results = evaluer_pipeline(
    csv_path="data/golden_dataset.csv",
    llm_model=llm_gpu,
    vlm_model=vlm_gpu
)

print("\n--- Bilan enregistré dans data/evaluation_results.csv ---")
