from typing import TypedDict, List, Optional

class SinistreState(TypedDict, total=False):
    # Entrées initiales fournies par l'assuré
    raw_declaration: str
    image_paths: List[str]

    # Données extraites par l'Agent Déclaration
    famille_sinistre: Optional[str]
    date_sinistre: Optional[str]
    description: Optional[str]
    has_photos: bool
    declaration_complete: bool
    champs_manquants: List[str]

    # Données évaluées par l'Agent Validation
    garantie_valide: bool
    delai_respecte: bool
    motif_refus: Optional[str]

    # Données évaluées par l'Agent Expertise
    analyse_image: Optional[str]
    estimation_degats: Optional[str]

    # Suivi global
    statut_dossier: str
    prestataire_recommande: Optional[str]