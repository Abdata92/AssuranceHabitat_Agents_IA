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
    return END

def route_after_validation(state: SinistreState) -> str:
    """Aiguille le dossier après le passage de l'Agent Validation."""
    if state.get("garantie_valide"):
        return "expertise"
    return END

# 2. Construction et compilation du graphe

def create_assurhabitat_graph(llm_text, vlm_vision):
    """
    Crée et compile le workflow multi-agents LangGraph.
    """
    workflow = StateGraph(SinistreState)

    # Ajout des nœuds du graphe
    workflow.add_node("declaration", lambda state: declaration_node(state, llm_text))
    workflow.add_node("validation", lambda state: validation_node(state, llm_text))
    workflow.add_node("expertise", lambda state: expertise_node(state, vlm_vision))

    # Point d'entrée
    workflow.set_entry_point("declaration")

    # Edges conditionnels
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

    workflow.add_edge("expertise", END)

    return workflow.compile()