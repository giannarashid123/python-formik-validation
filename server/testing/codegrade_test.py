
import pytest
from app import app, db
from models import Customer

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

@pytest.fixture
def sample_customer():
    """Create sample customer data"""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30
    }

def test_codegrade_placeholder():
    """Codegrade placeholder test"""
    assert 1==1

def test_customers_get_empty(client):
    """Test GET /customers returns empty list initially"""
    response = client.get('/customers')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_customers_post_success(client, sample_customer):
    """Test POST /customers creates a new customer"""
    response = client.post('/customers', 
                          json=sample_customer,
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'id' in data
    assert data['name'] == sample_customer['name']
    assert data['email'] == sample_customer['email']
    assert data['age'] == sample_customer['age']

def test_customers_get_with_data(client, sample_customer):
    """Test GET /customers returns created customers"""
    # Create a customer first
    client.post('/customers', 
               json=sample_customer,
               content_type='application/json')
    
    # Get all customers
    response = client.get('/customers')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == sample_customer['name']
    assert data[0]['email'] == sample_customer['email']
    assert data[0]['age'] == sample_customer['age']

def test_customer_model_to_dict():
    """Test Customer model to_dict method"""
    customer = Customer(name='Test User', email='test@test.com', age=25)
    customer.id = 1
    customer_dict = customer.to_dict()
    assert customer_dict['id'] == 1
    assert customer_dict['name'] == 'Test User'
    assert customer_dict['email'] == 'test@test.com'
    assert customer_dict['age'] == 25

def test_email_uniqueness(client):
    """Test that email must be unique"""
    email = 'unique@example.com'
    customer1 = {'name': 'First', 'email': email, 'age': 20}
    customer2 = {'name': 'Second', 'email': email, 'age': 30}
    
    # First customer should be created
    response1 = client.post('/customers', 
                           json=customer1,
                           content_type='application/json')
    assert response1.status_code == 200
    
    # Second customer with same email should fail
    response2 = client.post('/customers', 
                           json=customer2,
                           content_type='application/json')
    # Should return an error status (400 or 500)
    assert response2.status_code != 200

def test_validation_name_required(client):
    """Test name is required"""
    customer = {'email': 'test@example.com', 'age': 25}
    response = client.post('/customers', 
                          json=customer,
                          content_type='application/json')
    # Should fail validation (400 status)
    assert response.status_code != 200

def test_validation_email_required(client):
    """Test email is required"""
    customer = {'name': 'Test User', 'age': 25}
    response = client.post('/customers', 
                          json=customer,
                          content_type='application/json')
    # Should fail validation (400 status)
    assert response.status_code != 200

def test_validation_age_required(client):
    """Test age is required"""
    customer = {'name': 'Test User', 'email': 'test@example.com'}
    response = client.post('/customers', 
                          json=customer,
                          content_type='application/json')
    # Should fail validation (400 status)
    assert response.status_code != 200
