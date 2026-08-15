import pandas as pd
from src.graph import create_assurhabitat_graph

def reinitialiser_state(row):
    return {
        "raw_declaration": row["texte_declaration"],
        "image_paths": ["fake_path.jpg"] if row["has_photos"] else [],
    }

def evaluer_pipeline(csv_path: str, llm_model, vlm_model):
    df = pd.read_csv(csv_path)
    app = create_assurhabitat_graph(llm_model, vlm_model)
    
    resultats = []

    for idx, row in df.iterrows():
        state_initial = reinitialiser_state(row)
        final_state = app.invoke(state_initial)

        # 1. Métrique Déclaration (Complétude)
        completude_ok = (final_state.get("declaration_complete") == row["declaration_complete_attendue"])
        
        # 2. Métrique Validation (Conformité Contrat)
        validation_ok = (final_state.get("garantie_valide") == row["garantie_valide_attendue"])
        
        # 3. Métrique Orchestration (Choix Prestataire)
        prestataire_trouve = final_state.get("prestataire_recommande", "Conseiller generaliste")
        prestataire_ok = (prestataire_trouve.lower() in row["prestataire_attendu"].lower())

        resultats.append({
            "id": row["id"],
            "famille": row["famille_sinistre"],
            "Completude_Declaration_Score": 1.0 if completude_ok else 0.0,
            "Conformite_Contrat_Score": 1.0 if validation_ok else 0.0,
            "Precision_Prestataire_Score": 1.0 if prestataire_ok else 0.0
        })

    df_results = pd.DataFrame(resultats)
    df_results.to_csv("data/evaluation_results.csv", index=False)
    
    print("--- BILAN DE L'ÉVALUATION ---")
    print(df_results.mean(numeric_only=True))
    return df_results