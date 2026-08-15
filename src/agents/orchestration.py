from langgraph.graph import StateGraph, END
from src.state import SinistreState
from src.agents.declaration_agent import declaration_node
from src.agents.validation_agent import validation_node
from src.agents.expertise_agent import expertise_node

# 1. Fonctions de routage conditionnel

def route_after_declaration(state: SinistreState) -> str:
    """Aiguille le dossier après le passage de l'Agent Déclaration."""
    if state.get("declaration_complete"):
        return "validation"
    # Si incomplet, le processus s'arrête pour demander les pièces manquantes à l'assuré
    return END

def route_after_validation(state: SinistreState) -> str:
    """Aiguille le dossier après le passage de l'Agent Validation."""
    if state.get("garantie_valide"):
        return "expertise"
    # Si refusé ou en attente de pièce (ex: dépôt de plainte), le flux s'arrête
    return END

def recommander_prestataire(state: SinistreState) -> str:
    """Identifie le prestataire métiers selon la famille de sinistre."""
    famille = state.get("famille_sinistre", "").lower()
    if "eau" in famille:
        return "Plombier partenaire AssurHabitat"
    elif "vol" in famille or "cambriolage" in famille:
        return "Serrurier / Vitrier d'urgence"
    elif "incendie" in famille:
        return "Expert sécurité incendie"
    return "Conseiller généraliste"

# 2. Construction du graphe LangGraph

def create_assurhabitat_graph(llm_text, vlm_vision):
    """
    Crée et compile le workflow multi-agents.
    """
    workflow = StateGraph(SinistreState)

    # Ajout des nœuds du graphe
    workflow.add_node("declaration", lambda state: declaration_node(state, llm_text))
    workflow.add_node("validation", lambda state: validation_node(state, llm_text))
    workflow.add_node("expertise", lambda state: expertise_node(state, vlm_vision))

    # Définition du point d'entrée
    workflow.set_entry_point("declaration")

    # Définition des transitions conditionnelles (Edges)
    workflow.add_conditional_edges(
        "declaration",
        route_after_declaration,
        {
            "validation": "validation",
            END: END
        }
    )

    workflow.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "expertise": "expertise",
            END: END
        }
    )

    # L'expertise termine le workflow automatique et transmet le dossier au conseiller humain
    workflow.add_edge("expertise", END)

    return workflow.compile()