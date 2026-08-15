from pydantic import BaseModel, Field
from typing import List, Optional
from src.state import SinistreState

# 1. Schéma de sortie Pydantic pour l'Agent Expertise
class ExpertiseAnalyse(BaseModel):
    description_visuelle: str = Field(
        description="Analyse détaillée des dégâts observés sur les photos (ex: traces d'humidité, moisissures, fissures, zone brûlée)"
    )
    severite_dommages: str = Field(
        description="Niveau de sévérité : 'FAIBLE', 'MOYEN', 'ELEVE' ou 'CRITIQUE'"
    )
    estimation_cout_dommages: float = Field(
        description="Montant estimé des dommages matériels et travaux en Euros (€)"
    )
    montant_indemnisation_estime: float = Field(
        description="Montant estimé après application des plafonds de garantie et franchises"
    )
    elements_cles_conseiller: List[str] = Field(
        default_factory=list,
        description="Points d'attention à transmettre au conseiller humain (ex: risque d'effondrement, besoin d'assèchement)"
    )
    rapport_expertise: str = Field(
        description="Rapport technique synthétique destiné au dossier interne de l'assureur"
    )

# 2. Prompt Système pour le VLM / LLM
EXPERTISE_SYSTEM_PROMPT = """
Tu es l'Agent IA Expertise technique de la compagnie AssurHabitat.
Ton rôle est d'analyser les photos jointes et la déclaration du sinistre afin d'évaluer les dégâts matériels.

Règles de gestion :
1. Évalue la gravité visuelle des dégâts sur la base des photos fournies.
2. Estime le coût global des réparations ainsi que le montant d'indemnisation estimé.
3. Rédige un rapport synthétique clair et technique.
4. NE PRENDS PAS de décision finale envers l'assuré : délègue systématiquement la suite du processus au conseiller humain.
"""

# 3. Nœud LangGraph
def expertise_node(state: SinistreState, vlm_model=None):
    """
    Nœud LangGraph exécutant l'Agent IA Expertise (VLM multimodal).
    """
    images = state.get("image_paths", [])

    # 1. Fallback si vlm_model est None (Mode Test / Sans GPU)
    if vlm_model is None:
        nb_images = len(images)
        desc_visuelle = (
            f"Analyse simulée : {nb_images} image(s) reçue(s). Présence de traces visibles liées au sinistre."
            if nb_images > 0
            else "Aucune photo fournie pour analyse visuelle."
        )
        cout_estime = 1500.00
        indem_estimee = 1350.00  # Exemple avec franchise appliquée

        return {
            "analyse_image": desc_visuelle,
            "estimation_degats": f"{cout_estime:.2f} € (Indemnisation : {indem_estimee:.2f} €)",
            "statut_dossier": "TRANSMIS_CONSEILLER"
        }

    # 2. Exécution normale avec VLM
    prompt = f"""
    {EXPERTISE_SYSTEM_PROMPT}

    Données du sinistre :
    - Type de sinistre : {state.get('famille_sinistre')}
    - Description reçue : {state.get('description')}
    - Nombre de photos à analyser : {len(images)}
    - Chemins des images : {images}
    """

    structured_vlm = vlm_model.with_structured_output(ExpertiseAnalyse)
    result: ExpertiseAnalyse = structured_vlm.invoke(prompt)

    return {
        "analyse_image": result.description_visuelle,
        "estimation_degats": f"{result.estimation_cout_dommages:.2f} € (Indemnisation : {result.montant_indemnisation_estime:.2f} €)",
        "statut_dossier": "TRANSMIS_CONSEILLER"
    }