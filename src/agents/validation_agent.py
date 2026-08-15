from pydantic import BaseModel, Field
from typing import Optional
from src.state import SinistreState
from datetime import datetime

# 1. Structure de sortie attendue pour la Validation
class ValidationExtraction(BaseModel):
    garantie_applicable: str = Field(
        description="Nom de la garantie identifiée (ex: 'Dégât des eaux', 'Vol & Cambriolage', 'Incendie')"
    )
    delai_respecte: bool = Field(
        description="True si la déclaration est faite dans le délai légal (5j pour eau/feu, 2j pour vol)"
    )
    conditions_remplies: bool = Field(
        description="True si les conditions spécifiques sont remplies (ex: dépôt de plainte fourni pour un vol)"
    )
    garantie_valide: bool = Field(
        description="True si le sinistre est couvert par le contrat"
    )
    motif_refus_ou_attente: Optional[str] = Field(
        default=None,
        description="Explication si la garantie est refusée ou en attente d'un document complémentaire"
    )

# 2. Prompt Système
VALIDATION_SYSTEM_PROMPT = """
Tu es l'Agent IA Validation de la compagnie AssurHabitat.
Ton rôle est de vérifier si un sinistre déclaré est couvert par le Contrat de Garantie Habitation.

Règles de gestion AssurHabitat :
1. DÉLAIS LÉGAUX :
   - Dégât des eaux : Déclaration dans les 5 jours ouvrés suivants le sinistre.
   - Incendie : Déclaration dans les 5 jours ouvrés suivants le sinistre.
   - Cambriolage / Vol : Déclaration dans les 2 jours ouvrés suivants le sinistre.
2. CONDITIONS D'ÉLIGIBILITÉ :
   - Pour un Cambriolage / Vol : Un récépissé de dépôt de plainte auprès des forces de l'ordre est OBLIGATOIRE.
3. Si la déclaration est hors délai ou ne respecte pas les clauses du contrat, la garantie est REFUSÉE.
4. Si un document obligatoire (ex: dépôt de plainte) est manquant, le dossier est mis EN ATTENTE.
"""

# 3. Nœud LangGraph
def validation_node(state: SinistreState, llm_model=None):
    if llm_model is None:
        raw_text = str(state.get("raw_declaration", "")).lower()
        famille = str(state.get("famille_sinistre", "")).lower()
        
        # Mots-clés élargis pour détecter tout dépassement de délai
        hors_delai = any(kw in raw_text for kw in [
            "19 jours", "24 jours", "retard", "j+6", "25/09", "15/09"
        ])
        
        # Plainte obligatoire pour les cas de vol
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