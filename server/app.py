from distutils.log import debug
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models  import Customer, db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)

db.init_app(app)

@app.route("/customers", methods=['GET', 'POST'])
def customers():
    if request.method == 'GET':
        print(([customer.to_dict() for customer in Customer.query.all()]))
        return make_response(jsonify([customer.to_dict() for customer in Customer.query.all()]))

    if request.method == 'POST':
        data = request.get_json()
        
        # Server-side validation
        if not data.get('name') or not data.get('name').strip():
            return make_response(jsonify({'error': 'Name is required'}), 400)
        if not data.get('email') or not data.get('email').strip():
            return make_response(jsonify({'error': 'Email is required'}), 400)
        if not data.get('age') and data.get('age') != 0:
            return make_response(jsonify({'error': 'Age is required'}), 400)
        
        try:
            customer = Customer(name=data.get('name'), email=data.get('email'), age=data.get('age'))
            db.session.add(customer)
            db.session.commit()
            return make_response(
                jsonify(
                    {'id': customer.id, 'name': customer.name, 'email': customer.email, 'age': customer.age }))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                return make_response(jsonify({'error': 'Email already exists'}), 400)
            return make_response(jsonify({'error': str(e)}), 400)

if __name__ == "__main__":
    app.run(port="5555", debug=True)
