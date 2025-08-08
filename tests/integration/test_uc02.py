# ---- Test for UC02: View System Information ----

def test_it03_about_render(client):

    # Action: GET /about
    response = client.get('/about', follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert b"How KusiBot Works" in response.data
    assert b"Important Disclaimer" in response.data