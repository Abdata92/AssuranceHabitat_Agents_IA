from langgraph.graph import StateGraph, END
from src.state import SinistreState
from src.agents.declaration_agent import declaration_node
from src.agents.validation_agent import validation_node
from src.agents.expertise_agent import expertise_node

# 1. Routage : passer à la validation même si la déclaration a des champs manquants
def route_after_declaration(state: SinistreState) -> str:
    return "validation"

# 2. Routage : aller à l'expertise si valide, sinon aller directement à l'orchestration
def route_after_validation(state: SinistreState) -> str:
    if state.get("garantie_valide"):
        return "expertise"
    return "orchestration"

# 3. Nœud d'orchestration (attribue systématiquement un prestataire)
def orchestration_node(state: SinistreState):
    if not state.get("garantie_valide", False):
        prestataire = "Conseiller generaliste"
    else:
        famille = str(state.get("famille_sinistre", "")).lower()
        if "eau" in famille:
            prestataire = "Plombier partenaire AssurHabitat"
        elif "vol" in famille or "cambriol" in famille:
            prestataire = "Serrurier / Vitrier d'urgence"
        elif "incendie" in famille:
            prestataire = "Expert sécurité incendie"
        else:
            prestataire = "Conseiller generaliste"
            
    return {"prestataire_recommande": prestataire}

# 4. Graphe multi-agents
def create_assurhabitat_graph(llm_text=None, vlm_vision=None):
    workflow = StateGraph(SinistreState)

    workflow.add_node("declaration", lambda state: declaration_node(state, llm_text))
    workflow.add_node("validation", lambda state: validation_node(state, llm_text))
    workflow.add_node("expertise", lambda state: expertise_node(state, vlm_vision))
    workflow.add_node("orchestration", orchestration_node)

    workflow.set_entry_point("declaration")

    workflow.add_conditional_edges(
        "declaration",
        route_after_declaration,
        {"validation": "validation"}
    )
    workflow.add_conditional_edges(
        "validation",
        route_after_validation,
        {"expertise": "expertise", "orchestration": "orchestration"}
    )
    
    workflow.add_edge("expertise", "orchestration")
    workflow.add_edge("orchestration", END)

    return workflow.compile()