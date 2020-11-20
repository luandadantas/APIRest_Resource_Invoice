from hashlib import sha1

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token)
import db


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


@app.route('/invoices', methods=['GET'])
@app.route('/invoices/<int:id>', methods=['GET'])
#@jwt_required
def index(id=None):
    """
    Get invoices according to the request.

    Rotas:
        - /invoices : Get all active invoices
        - /invoices/<int:id> : Get an invoice by id.

    Args:
        page_number (int, optional): Get invoices with pagination. Defaults to None.
        limit (int, optional): Defines the amount of invoices that will be get by pagination. Defaults to 10.
        filter_by (str, optional): Database column that will be filtered. Defaults to None.
        filter_value (int ou str, optional): Value to be fetched within 'filter_by'. Defaults to None.
        order_by (list, optional): Get invoices sorted by month, year or document. Defaults to None.

    Returns:
        dict: Returns a json with the requested invoices.
    """
    if id:
        result, success = db.get_invoice_by_id(id)
        if success and (not result):
            return {"msg": 'Invoice not found'}, 404

    else:
        valid_fields = ['month', 'year', 'document']

        order_by_args = request.args.get('order_by', '')
        order_by_list = order_by_args.split(",")

        order_by = []
        for field in order_by_list:
            if field in valid_fields:
                order_by.append(field)
        
        filter_by = request.args.get('filter_by')
        if filter_by not in valid_fields:
            filter_by = None

        result, success = db.get_invoices(
            page_number=int(request.args.get('page', 0)),
            limit=int(request.args.get('limit', 10)),
            filter_by=filter_by,
            filter_value=request.args.get('filter_value'),
            order_by=order_by
        )

    if not success:
        return {"msg": 'The server found an error that it could not handle'}, 500

    return jsonify({"result": result}), 200


@app.route('/new_invoice', methods=['POST'])
#@jwt_required
def insert_into_db():
    """
    Adds a new invoice to the database.

    Route: /new_invoice

    Args:
        month (int): Invoice month
        year (int): Invoice year
        document (str): Invoice document
        description (str): Invoice description
        amount (float): Invoice amount

    Returns:
        if all goes well:
            dict: {}
            Bool: True
        if something goes wrong:
            dict: Error message.
            Bool: False
    """
    json = request.get_json()

    month = json.get('month')
    year = json.get('year')
    document = json.get('document')
    description = json.get('description', '')
    amount = json.get('amount', 0)

    if not month or not year or not document:
        return {'msg': '"month", "year" and "document" are required fields'}, 400

    try:
        month = int(month)
        year = int(year)
        amount = float(amount)
    except:
        return {'msg': '"month" and "year" have to be int and "amount" have to be decimal'}, 400

    if not (1 <= month <= 12) or year < 1900:
        return {'msg': 'the "month" must be between 1 and 12, and the "year" greater than 1900'}, 400

    success = db.create_new_invoice(month, year, document, description, amount)

    if not success:
        return {"msg": 'The server found an error that it could not handle'}, 500

    return {}, 201


@app.route('/update_invoice/<int:id>', methods=['PUT'])
#@jwt_required
def update_invoice(id):
    """Updates an entire invoice, or just parts of it, in which it is saved in a database.

    Route: /update_invoice/<int:id>

    Args:
        id (int): id referring to the invoice that will be updated.
        month (int): new month value, if there is an update to that value in the request.
        year (int): new year value, if there is an update to that value in the request.
        document (str): new document value, if there is an update to that value in the request.
        description (str): new description value, if there is an update to that value in the request.
        amount (float): new amount value, if there is an update to that value in the request.

    Returns:
        if all goes well:
            dict: {}
            Bool: True
        if something goes wrong:
            dict: Error message.
            Bool: False
    """
    json = request.get_json()

    invoice, success = db.get_invoice_by_id(id)

    if not success:
        return {"msg": 'The server found an error that it could not handle'}, 500

    if not invoice:
        return {"msg": 'invoice not found'}, 404

    new_month = json.get('month')
    new_year = json.get('year')
    new_document = json.get('document')
    new_description = json.get('description')
    new_amount = json.get('amount')

    if (not new_month) and (not new_year) and (not new_document) and (not new_description) and (not new_amount):
        return {"msg": "JSON have to be at least one field to update"}, 400

    month = new_month if new_month else invoice.get('month')
    year = new_year if new_year else invoice.get('year')
    document = new_document if new_document else invoice.get('document')
    description = new_description if new_description else invoice.get('description')
    amount = new_amount if new_amount else invoice.get('amount')

    success = db.update_invoice_by_id(id, month, year, document, description, amount)

    if not success:
        return {"msg": 'The server found an error that it could not handle'}, 500

    return {}, 204


@app.route('/delete_invoice/<int:id>', methods=['DELETE'])
#@jwt_required
def delete_invoice(id):
    """logically deletes the invoice that must be passed by the id.

    Route: /delete_invoice/<int:id>

    Args:
        id (int): id referring to the invoice that will be deleted.

    Returns:
        if all goes well:
            dict: {}
            Bool: True
        if something goes wrong:
            dict: Error message.
            Bool: False
    """
    invoice, success = db.get_invoice_by_id(id)

    if not success:
        return {"msg": 'The server found an error that it could not handle'}, 500

    if not invoice:
        return {"msg": 'Invoice not found'}, 404

    success = db.delete_invoice_by_id(id)

    if not success:
        return {"msg": 'The server found an error that it could not handle'}, 500

    return {}, 204


@app.route('/register', methods=['POST'])
def register():
    """creates a new user who will be allowed to access the database.

    Args:
        username (str): name of the user to be saved in the database.
        password (str): password of the user to be saved in the database.

    Returns:
        if all goes well:
            dict: {}
            Bool: True
        if something goes wrong:
            dict: Error message.
            Bool: False
    """
    json = request.get_json()

    username = json.get('username')
    password = json.get('password')

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user, success = db.get_user_by_username(username)

    if not success:
        return {"msg": 'The server found an error that it could not handle'}, 500
    
    if user:
        return {"msg": "username already exists"}, 409
    
    hash_password = sha1(password.encode('utf-8')).hexdigest()

    if not db.create_new_user(username, hash_password):
        return {"msg": 'The server found an error that it could not handle'}, 500

    return {}, 204


@app.route('/login', methods=['POST'])
def login():
    """creates user login

    Routes: /login

    Args:
        username (str): name of the user.
        password (str): password value.

    Returns:
        if all goes well:
            dict: token
        if something goes wrong:
            dict: Error message 
    """
    json = request.get_json()

    username = json.get('username')
    password = json.get('password')

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    
    current_user, success = db.get_user_by_username(username)

    if not success:
        return {"msg": 'The server found an error that it could not handle'}, 500
    
    if not current_user:
        return {"msg": "user does not exist"}, 404
    
    if not (sha1(password.encode('utf-8')).hexdigest() == current_user['password']):
        return {'msg': 'wrong credentials'}, 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


if __name__ == '__main__':
    app.run(debug=True)