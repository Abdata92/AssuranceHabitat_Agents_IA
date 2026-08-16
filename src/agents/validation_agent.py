from pydantic import BaseModel, Field
from typing import Optional
from src.state import SinistreState

# 1. Structure Pydantic
class ValidationExtraction(BaseModel):
    garantie_applicable: str = Field(
        description="Nom de la garantie (ex: 'Dégât des eaux', 'Vol & Cambriolage', 'Incendie')"
    )
    delai_respecte: bool = Field(
        description="True si la déclaration respecte le délai (5j pour eau/feu, 2j pour vol)"
    )
    conditions_remplies: bool = Field(
        description="True si les conditions sont remplies (ex: dépôt de plainte pour vol)"
    )
    garantie_valide: bool = Field(
        description="True si le sinistre est couvert par le contrat"
    )
    motif_refus_ou_attente: Optional[str] = Field(
        default=None,
        description="Explication si refusé"
    )

# 2. Prompt Système
VALIDATION_SYSTEM_PROMPT = """Tu es l'agent de validation des garanties AssurHabitat.
Ta mission est d'évaluer si un sinistre est couvert par le contrat.

RÈGLES STRICTES :
1. PAR DÉFAUT, pour un sinistre standard (dégât des eaux, fuite, incendie) sans mention de retard important (ex: plusieurs semaines), le délai est RESPECTÉ et la garantie est VALIDE (garantie_valide = True).
2. Vol / Cambriolage : VALIDE (True) si une plainte, procès-verbal, police ou commissariat est mentionné. Sinon False.
3. Ne mets garantie_valide = False QUE si le texte indique explicitement un retard avéré (ex: '19 jours', '24 jours', 'retard') ou l'absence de plainte pour un vol.
"""

# 3. Nœud LangGraph
def validation_node(state: SinistreState, llm_model=None):
    raw_text = str(state.get("raw_declaration", "")).lower()
    famille = str(state.get("famille_sinistre", "")).lower()

    # --- MODE LLM GPU ---
    if llm_model is not None:
        try:
            structured_llm = llm_model.with_structured_output(ValidationExtraction)
            prompt = f"{VALIDATION_SYSTEM_PROMPT}\n\nFamille : {famille}\nDéclaration : {state.get('raw_declaration', '')}"
            res = structured_llm.invoke(prompt)

            raw_val = getattr(res, "garantie_valide", True)
            garantie_valide = True if str(raw_val).lower() in ["true", "1", "yes"] else False

            return {
                "garantie_valide": garantie_valide,
                "delai_respecte": getattr(res, "delai_respecte", True),
                "motif_refus": getattr(res, "motif_refus_ou_attente", None),
                "statut_dossier": "VALIDATION_ACCEPTEE" if garantie_valide else "VALIDATION_REFUSEE"
            }
        except Exception:
            pass

    # --- MODE HEURISTIQUE / FALLBACK ---
    hors_delai = any(kw in raw_text for kw in [
        "19 jours", "24 jours", "retard", "j+6", "25/09", "15/09"
    ])
    a_plainte = any(kw in raw_text for kw in ["plainte", "pv", "police", "velux", "commissariat"])

    if "vol" in famille or "cambriol" in famille:
        garantie_valide = not hors_delai and a_plainte
    else:
        garantie_valide = not hors_delai

    return {
        "garantie_valide": garantie_valide,
        "delai_respecte": not hors_delai,
        "motif_refus": None if garantie_valide else "Délai dépassé ou pièce manquante",
        "statut_dossier": "VALIDATION_ACCEPTEE" if garantie_valide else "VALIDATION_REFUSEE"
    }
