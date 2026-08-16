from langgraph.graph import StateGraph, END
from src.state import SinistreState
from src.agents.declaration_agent import declaration_node
from src.agents.validation_agent import validation_node
from src.agents.expertise_agent import expertise_node

def route_after_declaration(state: SinistreState) -> str:
    return "validation"

def route_after_validation(state: SinistreState) -> str:
    if state.get("garantie_valide", False):
        return "expertise"
    return "orchestration"

def orchestration_node(state: SinistreState):
    if not state.get("garantie_valide", False):
        prestataire = "Conseiller generaliste"
    else:
        famille = str(state.get("famille_sinistre", "")).lower()
        
        # Ingestion élargie des synonymes générés par les LLMs
        if any(kw in famille for kw in ["eau", "eaux", "dégât", "degat", "fuite", "infiltration", "inondation", "inonde"]):
            prestataire = "Plombier partenaire AssurHabitat"
        elif any(kw in famille for kw in ["vol", "cambriol", "effraction", "serrure", "velo", "vélo"]):
            prestataire = "Serrurier / Vitrier d'urgence"
        elif any(kw in famille for kw in ["incendie", "feu", "fumee", "fumée", "explosion"]):
            prestataire = "Expert sécurité incendie"
        else:
            prestataire = "Conseiller generaliste"
            
    return {"prestataire_recommande": prestataire}

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
