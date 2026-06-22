def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_bfs_dfs_and_compare_endpoints(client, simple_maze):
    for endpoint in ("bfs", "dfs"):
        response = client.post(f"/api/maze/solve/{endpoint}", json=simple_maze)
        assert response.status_code == 200
        body = response.json()
        assert body["path_found"] is True
        assert body["path_length"] == len(body["path"]) - 1

    comparison = client.post("/api/maze/solve/compare", json=simple_maze)
    assert comparison.status_code == 200
    assert set(comparison.json()) == {"bfs", "dfs", "differences", "conclusion"}


def test_examples_endpoints_return_exactly_five(client):
    response = client.get("/api/maze/examples")
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert [item["id"] for item in response.json()] == [1, 2, 3, 4, 5]

    example = client.get("/api/maze/examples/5")
    assert example.status_code == 200
    assert example.json()["name"] == "Sin solucion"


def test_missing_example_is_404(client):
    response = client.get("/api/maze/examples/99")
    assert response.status_code == 404
    assert "No existe" in response.json()["detail"]


def test_invalid_domain_data_has_clear_message(client, simple_maze):
    simple_maze["obstacles"] = [simple_maze["start"]]
    response = client.post("/api/maze/solve/bfs", json=simple_maze)
    assert response.status_code == 422
    assert "inicial" in response.json()["detail"]


def test_invalid_json_and_missing_fields_are_422(client):
    malformed = client.post(
        "/api/maze/solve/bfs",
        content="{not-json}",
        headers={"content-type": "application/json"},
    )
    assert malformed.status_code == 422
    assert "detail" in malformed.json()

    incomplete = client.post("/api/maze/solve/bfs", json={"rows": 5})
    assert incomplete.status_code == 422
    assert "detail" in incomplete.json()
