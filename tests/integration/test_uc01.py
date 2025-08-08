# ---- Test for UC01: View Crisis Support ----

def test_it01_sos_render(client):

    # Action: GET /sos
    response = client.get('/sos', follow_redirects = True)

    # Assertions
    assert response.status_code == 200
    assert b"National Support" in response.data
    assert b"Regional Support" in response.data

def test_it02_invalid_endpoint(client):

    # Action: GET /invalid
    response = client.get('/invalid', follow_redirects = True)

    # Assertions
    assert response.status_code == 404
    assert b"Not Found" in response.data