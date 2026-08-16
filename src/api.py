from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langchain_ollama import ChatOllama
from src.agents.orchestration import create_assurhabitat_graph

app = FastAPI(
    title="AssurHabitat Multi-Agent AI API",
    version="1.0.0",
    description="API de production pour le traitement automatisé des sinistres habitation"
)

# Initialisation des modèles au démarrage de l'API
llm_gpu = ChatOllama(model="mistral", temperature=0.0)
vlm_gpu = ChatOllama(model="llava", temperature=0.0)
agent_graph = create_assurhabitat_graph(llm_gpu, vlm_gpu)

class SinistreRequest(BaseModel):
    declaration_id: str
    raw_declaration: str
    image_paths: Optional[List[str]] = []

@app.get("/health")
def health_check():
    return {"status": "ok", "models": ["mistral:7b", "llava"]}

@app.post("/api/v1/sinistres/process")
async def process_sinistre(request: SinistreRequest):
    try:
        # Invocations de la pipeline LangGraph
        initial_state = {
            "raw_declaration": request.raw_declaration,
            "image_paths": request.image_paths
        }
        final_state = agent_graph.invoke(initial_state)
        
        return {
            "declaration_id": request.declaration_id,
            "statut_dossier": final_state.get("statut_dossier"),
            "garantie_valide": final_state.get("garantie_valide"),
            "famille_sinistre": final_state.get("famille_sinistre"),
            "prestataire_recommande": final_state.get("prestataire_recommande"),
            "rapport_expertise": final_state.get("rapport_expertise")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur traitement pipeline : {str(e)}")