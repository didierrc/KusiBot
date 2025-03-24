from flask_login import current_user
from kusibot.database.models import User

class TestAuth:
    """Test authentication functionality (login, register, logout)."""
    
    ##### TEST CORRECTLY LOADING PAGES #####

    def test_login_page(self, client):
        """Test if login page loads correctly."""
        
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_register_page(self, client):
        """Test if register page loads correctly."""
        
        response = client.get('/auth/signup')
        assert response.status_code == 200
        assert b'Register' in response.data

    ##### TEST LOGIN FUNCTIONALITY #####

    def test_successful_login_user(self, client):
        """Test successful login with correct credentials."""
        
        with client:
            response = client.post(
                '/auth/login',
                data={
                    'username': 'test_user', 
                    'password': 'password123',
                    'csrf_token': self._get_csrf_token(client)
                },
                follow_redirects=True
            )
            
            # Check if login was successful
            assert response.status_code == 200
            assert current_user.is_authenticated
            assert current_user.username == 'test_user'
            assert current_user.email == 'test@example.com'
            assert b'Hello! I\'m KusiBot and I am ready to help. How are you feeling today?' in response.data

    def test_login_with_incorrect_password_user(self, client):
        """Test login with incorrect password."""
        
        response = client.post(
            '/auth/login',
            data={
                'username': 'test_user', 
                'password': 'wrongpassword',
                'csrf_token': self._get_csrf_token(client)
            },
            follow_redirects=True
        )
        
        # Check login failure
        assert b'Invalid username or password' in response.data
        assert not current_user.is_authenticated

    def test_login_with_nonexistent_user(self, client):
        """Test login with non-existent user."""
        
        response = client.post(
            '/auth/login',
            data={
                'username': 'non_existent_user', 
                'password': 'password123',
                'csrf_token': self._get_csrf_token(client)
            },
            follow_redirects=True
        )
        
        # Check login failure
        assert b'Invalid username or password' in response.data
        assert not current_user.is_authenticated

    ##### TEST REGISTER FUNCTIONALITY #####

    def test_successful_registration_user(self, client, app):
        """Test successful user registration."""
        
        with client:
            response = client.post(
                '/auth/signup',
                data={
                    'username': 'newuser',
                    'email': 'newuser@example.com',
                    'password': 'newpassword123',
                    'confirm_password': 'newpassword123',
                    'csrf_token': self._get_csrf_token(client)
                },
                follow_redirects=True
            )
            
            # Check if registration was successful
            assert response.status_code == 200
            
            # Verify the user was added to the database
            with app.app_context():
                user = User.query.filter_by(email='newuser@example.com').first()
                assert user is not None
                assert user.username == 'newuser'
                assert user.is_professional == False
    
    def test_registration_with_existing_email(self, client):
        """Test registration with an email that already exists."""
        
        response = client.post(
            '/auth/signup',
            data={
                'username': 'anotheruser',
                'email': 'test@example.com',  # This email already exists
                'password': 'password123',
                'confirm_password': 'password123',
                'csrf_token': self._get_csrf_token(client)
            },
            follow_redirects=True
        )
        
        # Check registration failure
        assert response.status_code == 200
        assert b'That email is already registered.' in response.data
    
    def test_registration_with_existing_username(self, client):
        """Test registration with an username that already exists."""
        
        response = client.post(
            '/auth/signup',
            data={
                'username': 'test_user', # This username already exists
                'email': 'other@example.com',  
                'password': 'password123',
                'confirm_password': 'password123',
                'csrf_token': self._get_csrf_token(client)
            },
            follow_redirects=True
        )
        
        # Check registration failure
        assert response.status_code == 200
        assert b'That username is already taken.' in response.data

    def test_registration_passwords_mismatch(self, client):
        """Test registration with mismatched passwords."""
        
        response = client.post(
            '/auth/signup',
            data={
                'username': 'other_user',
                'email': 'other@example.com',  
                'password': 'password123',
                'confirm_password': '123password',
                'csrf_token': self._get_csrf_token(client)
            },
            follow_redirects=True
        )
        
        # Check registration failure
        assert response.status_code == 200
        assert b'must be equal to password' in response.data

    def test_registration_empty_fields(self, client):
        """Test registration with mismatched passwords."""
        
        response = client.post(
            '/auth/signup',
            data={
                'username': '',
                'email': 'other@example.com',  
                'password': '',
                'confirm_password': '123password',
                'csrf_token': self._get_csrf_token(client)
            },
            follow_redirects=True
        )
        
        # Check registration failure
        assert response.status_code == 200
        assert b'This field is required.' in response.data

    ##### TEST LOGOUT FUNCTIONALITY #####

    def test_logout(self, authenticated_client):
        """Test user logout functionality."""
        
        with authenticated_client as client:
            # Verify user is authenticated before logout
            assert current_user.is_authenticated
            
            # Logout
            response = client.get('/auth/logout', follow_redirects=True)
            
            # Check if logout was successful
            assert response.status_code == 200
            assert not current_user.is_authenticated
            assert b'Login' in response.data
    
    ##### UTILS #####

    def _get_csrf_token(self, client):
        """Helper method to get CSRF token from Login Form."""
        response = client.get('/auth/login')
        csrf_token = response.data.decode('utf-8').split('name="csrf_token" type="hidden" value="')[1].split('"')[0]
        return csrf_token

