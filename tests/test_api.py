import pytest
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def test_health(client):
    result = client.get("/health")
    assert result.status_code == 200
    assert result.json["status"] == "ok"


def test_create_and_list(client):
    result = client.post("/tasks", json={"title": "Estudar GitHub Actions"})
    assert result.status_code == 201
    assert result.json["id"] == 1
    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert len(listed.json) == 1
    assert listed.json[0]["title"] == "Estudar GitHub Actions"


def test_invalid_title(client):
    assert client.post("/tasks", json={"title": "  "}).status_code == 400


def test_mark_done(client):
    item = client.post("/tasks", json={"title": "Deploy"}).json
    result = client.patch(f'/tasks/{item["id"]}', json={"done": True})
    assert result.status_code == 200
    assert client.get("/tasks").json[0]["done"] is True


def test_not_found(client):
    assert client.patch("/tasks/999", json={"done": True}).status_code == 404

# --- TESTES DO ENDPOINT DELETE ---

def test_delete_task_success():
    """ Teste de exclusão de tarefa existente (Esperado: 204) """
    response = client.delete("/tasks/1")
    assert response.status_code == 204
    
    response_get = client.get("/tasks/1")
    assert response_get.status_code == 404

def test_delete_task_not_found():
    """ Teste de exclusão de tarefa inexistente """
    response = client.delete("/tasks/9999")
    assert response.status_code == 404


# --- TESTE DA TASK ADICIONAL ---

def test_get_task_by_id_success():
    """ Teste de busca por ID existente """
    response = client.get("/tasks/2")
    assert response.status_code == 200
    assert response.json()["id"] == 2
