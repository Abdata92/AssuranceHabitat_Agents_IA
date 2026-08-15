# test_local.py
from src.graph import create_assurhabitat_graph

# 1. Mocks légers simulant le comportement des modèles LLM et VLM
class MockLLM:
    def with_structured_output(self, schema):
        self.schema = schema
        return self

    def invoke(self, prompt: str):
        schema_name = getattr(self.schema, "__name__", "")
        
        # Simulation réponse Agent Déclaration
        if "DeclarationExtraction" in schema_name:
            return self.schema(
                famille_sinistre="Dégât des eaux",
                date_sinistre="hier soir",
                description="Fuite lave-vaisselle voisin du dessus, mur infiltré",
                has_photos=True,
                champs_manquants=[],
                declaration_complete=True
            )
        
        # Simulation réponse Agent Validation
        if "ValidationExtraction" in schema_name:
            return self.schema(
                garantie_applicable="Dégâts des eaux",
                delai_respecte=True,
                conditions_remplies=True,
                garantie_valide=True,
                motif_refus_ou_attente=None
            )
        return None

class MockVLM:
    def with_structured_output(self, schema):
        self.schema = schema
        return self

    def invoke(self, prompt: str):
        # Simulation réponse Agent Expertise
        return self.schema(
            description_visuelle="Traces d'humidité importantes et peinture écaillée sur le mur haut.",
            severite_dommages="MOYEN",
            estimation_cout_dommages=850.0,
            montant_indemnisation_estime=700.0, # 850€ - 150€ franchise
            elements_cles_conseiller=["Vérifier assèchement du mur avant peinture"],
            rapport_expertise="Infiltration constatée suite à fuite lave-vaisselle. Prévoir réfection peinture et sous-couche."
        )

# 2. Exécution du test du graphe
if __name__ == "__main__":
    print("🚀 Lancement du test local du pipeline LangGraph...\n")
    
    mock_llm = MockLLM()
    mock_vlm = MockVLM()
    
    # Compilation du graphe
    app = create_assurhabitat_graph(mock_llm, mock_vlm)

    # État initial de test (Exemple 1 : Fuite cuisine)
    etat_initial = {
        "raw_declaration": "Bonjour, Il y a eu une fuite dans ma cuisine hier soir à cause de mon voisin du dessus. Son lave-vaisselle a été mal installé et du coup, le mur est infiltré d'eau et la peinture se détache.",
        "image_paths": ["data/images/IMG_4580.jpg"]
    }

    # Exécution du flux
    resultat_final = app.invoke(etat_initial)

    # Affichage des résultats
    print("✅ --- RÉSULTAT DU DOSSIER ---")
    print(f"Famille identifiée : {resultat_final.get('famille_sinistre')}")
    print(f"Complétude         : {resultat_final.get('declaration_complete')}")
    print(f"Garantie validée   : {resultat_final.get('garantie_valide')}")
    print(f"Estimation dégâts  : {resultat_final.get('estimation_degats')}")
    print(f"Statut final       : {resultat_final.get('statut_dossier')}")