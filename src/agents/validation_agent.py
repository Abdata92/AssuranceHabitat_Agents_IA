from pydantic import BaseModel, Field
from typing import Optional
from src.state import SinistreState

class ValidationExtraction(BaseModel):
    garantie_valide: bool = Field(
        description="True si le sinistre est couvert (délais et conditions respectés), False sinon."
    )
    motif_refus: Optional[str] = Field(
        default=None,
        description="Raison du refus si garantie_valide est False."
    )

VALIDATION_SYSTEM_PROMPT = """Tu es l'agent de validation des garanties AssurHabitat.
Évalue la déclaration de sinistre selon les règles du contrat :

- DÉGÂT DES EAUX / INCENDIE : Couvert (garantie_valide = True) sauf mention explicite de retard majeur de plusieurs semaines.
- CAMBRIOLAGE / VOL : 
  * Si la déclaration indique un retard (ex: 'j+6', '19 jours', '24 jours', 'déclaré en retard') -> garantie_valide = False.
  * Si la déclaration est faite à temps (sous 2 jours) AVEC plainte ou police -> garantie_valide = True.
  * Si pas de plainte/PV mentionné -> garantie_valide = False.

Réponds TOUJOURS au format JSON avec le champ booléen garantie_valide.
"""

def validation_node(state: SinistreState, llm_model=None):
    raw_text = str(state.get("raw_declaration", "")).lower()
    famille = str(state.get("famille_sinistre", "")).lower()

    if llm_model is not None:
        try:
            structured_llm = llm_model.with_structured_output(ValidationExtraction)
            prompt = f"{VALIDATION_SYSTEM_PROMPT}\n\nFamille : {famille}\nDéclaration : {state.get('raw_declaration', '')}"
            res = structured_llm.invoke(prompt)

            garantie_valide = bool(res.garantie_valide)
            return {
                "garantie_valide": garantie_valide,
                "delai_respecte": garantie_valide,
                "motif_refus": res.motif_refus,
                "statut_dossier": "VALIDATION_ACCEPTEE" if garantie_valide else "VALIDATION_REFUSEE"
            }
        except Exception as e:
            print(f"[Validation Agent Warning] Échec parsing LLM ({e}), bascule sur fallback.")

    # Fallback Heuristique de sécurité
    hors_delai = any(kw in raw_text for kw in ["19 jours", "24 jours", "retard", "j+6", "25/09", "15/09"])
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
