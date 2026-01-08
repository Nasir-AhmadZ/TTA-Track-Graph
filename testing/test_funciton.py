def test_proj_graph(client):
    r=client.get("/graph/proj/693ab9cb2a472cca87e3c75a")
    assert r.status_code == 200

def test_user_graph(client):
    r=client.get("/graph/user/691c8bf8d691e46d00068bf3")
    assert r.status_code == 200