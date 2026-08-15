from pydantic import BaseModel, Field
from typing import List, Optional
from src.state import SinistreState

class DeclarationExtraction(BaseModel):
    famille_sinistre: Optional[str] = Field(
        description="Type de sinistre : 'Dégât des eaux', 'Incendie' ou 'Cambriolage'"
    )
    date_sinistre: Optional[str] = Field(
        description="Date du sinistre si mentionnée (ex: 'hier soir', '10/09/2025')"
    )
    description: Optional[str] = Field(
        description="Résumé des faits déclarés par l'assuré"
    )
    has_photos: bool = Field(
        description="True si au moins une photo/pièce jointe est fournie"
    )
    champs_manquants: List[str] = Field(
        default_factory=list,
        description="Éléments manquants parmi ['date', 'description', 'photos']"
    )
    declaration_complete: bool = Field(
        description="True si Date + Description + Photos sont présents"
    )

DECLARATION_SYSTEM_PROMPT = """
Tu es l'Agent IA Déclaration d'AssurHabitat.
Analyse la déclaration de l'assuré et vérifie la présence de :
- La DATE du sinistre.
- La DESCRIPTION des dommages.
- Les PHOTOS / pièces jointes.

NE VALIDE PAS les garanties à cette étape : vérifie uniquement la COMPLÉTUDE.
"""

def declaration_node(state: SinistreState, llm_model=None):
    raw_text = state.get("raw_declaration", "")
    images_presentes = len(state.get("image_paths", [])) > 0

    # 1. Fallback si aucun modèle LLM n'est fourni (Mode Test / Sans GPU)
    if llm_model is None:
        text_lower = raw_text.lower()
        famille = "Dégât des eaux"
        if "incendie" in text_lower or "feu" in text_lower:
            famille = "Incendie"
        elif "cambriol" in text_lower or "vol" in text_lower:
            famille = "Cambriolage"

        has_desc = len(raw_text.strip()) > 10
        champs_m = []
        if not images_presentes:
            champs_m.append("photos")
        if not has_desc:
            champs_m.append("description")

        is_complete = len(champs_m) == 0

        return {
            "famille_sinistre": famille,
            "date_sinistre": "Inconnue",
            "description": raw_text,
            "has_photos": images_presentes,
            "declaration_complete": is_complete,
            "champs_manquants": champs_m,
            "statut_dossier": "DECLARATION_VALIDEE" if is_complete else "DECLARATION_INCOMPLETE"
        }

    # 2. Exécution normale avec extraction structurée LLM
    prompt = f"""
    {DECLARATION_SYSTEM_PROMPT}

    Déclaration : \"\"\"{raw_text}\"\"\"
    Nombre d'images : {len(state.get('image_paths', []))}
    """

    structured_llm = llm_model.with_structured_output(DeclarationExtraction)
    result: DeclarationExtraction = structured_llm.invoke(prompt)

    return {
        "famille_sinistre": result.famille_sinistre,
        "date_sinistre": result.date_sinistre,
        "description": result.description,
        "has_photos": result.has_photos or images_presentes,
        "declaration_complete": result.declaration_complete,
        "champs_manquants": result.champs_manquants,
        "statut_dossier": "DECLARATION_VALIDEE" if result.declaration_complete else "DECLARATION_INCOMPLETE"
    }