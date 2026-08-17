from fastapi.testclient import TestClient
from unittest.mock import patch
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


@patch("src.api.agent_graph.invoke")
def test_process_sinistre_succes_mocked(mock_invoke):
    """Teste l'endpoint /process en simulant la méthode invoke du graphe agent_graph."""
    mock_invoke.return_value = {
        "declaration_id": "TEST-01",
        "statut_dossier": "TRANSMIS_CONSEILLER",
        "garantie_valide": True,
        "famille_sinistre": "Dégât des eaux",
        "prestataire_recommande": "Plombier",
        "rapport_expertise": None
    }

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
    assert data["statut_dossier"] == "TRANSMIS_CONSEILLER"