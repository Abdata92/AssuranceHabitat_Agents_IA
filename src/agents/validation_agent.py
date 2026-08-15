from pydantic import BaseModel, Field
from typing import Optional
from src.state import SinistreState

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
def validation_node(state: SinistreState, llm_model):
    """
    Nœud LangGraph exécutant l'Agent IA Validation.
    """
    prompt = f"""
    {VALIDATION_SYSTEM_PROMPT}

    Données du sinistre transmis par l'Agent Déclaration :
    - Famille de sinistre : {state.get('famille_sinistre')}
    - Date du sinistre : {state.get('date_sinistre')}
    - Description : {state.get('description')}
    - Déclaration initiale du client : \"\"\"{state.get('raw_declaration')}\"\"\"
    """

    structured_llm = llm_model.with_structured_output(ValidationExtraction)
    result: ValidationExtraction = structured_llm.invoke(prompt)

    # Détermination du nouveau statut du dossier
    if result.garantie_valide:
        nouveau_statut = "VALIDATION_ACCEPTEE"
    elif not result.conditions_remplies and "plainte" in (result.motif_refus_ou_attente or "").lower():
        nouveau_statut = "EN_ATTENTE_PLAINTE"
    else:
        nouveau_statut = "VALIDATION_REFUSEE"

    return {
        "garantie_valide": result.garantie_valide,
        "delai_respecte": result.delai_respecte,
        "motif_refus": result.motif_refus_ou_attente,
        "statut_dossier": nouveau_statut
    }