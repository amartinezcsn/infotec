def test_client_and_admin_pages_render(client):
    home = client.get("/")
    admin = client.get("/admin")
    assert home.status_code == 200
    assert "CUP&amp;CAKE" in home.text or "CUP&CAKE" in home.text
    assert admin.status_code == 200
    assert "Supervisión humana" in admin.text

