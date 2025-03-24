class TestMain:
    """Test main routes."""
    
    def test_index_page(self, client):
        """Test if index page loads correctly."""
        
        response = client.get('/')
        assert response.status_code == 200
        assert b'Welcome to KusiBot' in response.data