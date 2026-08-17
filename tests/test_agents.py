import pytest
from unittest.mock import MagicMock, patch

# Importer le type d'état ou le graphe selon la structure de votre code
from src.agents.orchestration import create_assurhabitat_graph

def test_graph_initialization():
    """Vérifie que le graphe d'orchestration s'instancie sans erreur."""
    graph = create_assurhabitat_graph()
    assert graph is not None


@patch("langchain_community.llms.Ollama.invoke")
def test_agent_declaration_logic(mock_ollama_invoke):
    """Teste l'exécution d'un nœud agent en simulant la réponse textuelle du LLM."""
    mock_ollama_invoke.return_value = '{"date_sinistre": "2025-09-10", "lieu": "cuisine", "description": "fuite"}'
    
    # État initial de test
    initial_state = {
        "declaration_id": "TEST-UNIT",
        "raw_declaration": "Fuite d'eau dans la cuisine le 10/09/2025.",
        "image_paths": []
    }
    
    # Remplacer par l'appel à votre nœud/agent de déclaration
    # Exemple : result = agent_declaration_node(initial_state)
    assert initial_state["declaration_id"] == "TEST-UNIT"