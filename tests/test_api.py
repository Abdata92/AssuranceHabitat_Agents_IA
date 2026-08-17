from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api import app

client = TestClient(app)


def test_health_endpoint():
    """Vérifie que la route /health répond 200 OK et retourne status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"


def test_process_sinistre_payload_invalide():
    """Vérifie le rejet des payloads incomplets (HTTP 422)."""
    payload_invalide = {"declaration_id": "TEST-422"}
    response = client.post("/api/v1/sinistres/process", json=payload_invalide)
    assert response.status_code == 422


@patch("src.api.create_assurhabitat_graph")
def test_process_sinistre_succes_mocked(mock_create_graph):
    """Teste l'endpoint /process en simulant l'exécution du graphe LangGraph."""
    # Simulation de l'objet graph et de sa méthode .invoke()
    mock_graph_instance = MagicMock()
    mock_graph_instance.invoke.return_value = {
        "declaration_id": "TEST-01",
        "statut_dossier": "TRANSMIS_CONSEILLER",
        "garantie_valide": True,
        "famille_sinistre": "Dégât des eaux",
        "prestataire_recommande": "Plombier",
        "rapport_expertise": None
    }
    mock_create_graph.return_value = mock_graph_instance

    payload = {
        "declaration_id": "TEST-01",
        "raw_declaration": "Fuite d'eau dans la cuisine.",
        "image_paths": []
    }

    response = client.post("/api/v1/sinistres/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["declaration_id"] == "TEST-01"
    assert data["garantie_valide"] is True