from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token)
import db


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


@app.route('/invoices', methods=['GET'])
@app.route('/invoices/<int:id>', methods=['GET'])
@jwt_required
def index(id=None):
    if id:
        result, success = db.get_invoice_by_id(id)
        if success and (not result):
            return {"msg": 'Invoice not found'}, 404

    else:
        db_names = {
            'month': 'ReferenceMonth',
            'year': 'ReferenceYear',
            'document': 'Document'
        }

        order_by_list = request.args.get('order_by', '')
        order_by_list = order_by_list.split(",")

        order_by = []
        for ob in order_by_list:
            field = db_names.get(ob)
            if field:
                order_by.append(field)

        result, success = db.get_invoices(
            page_number=int(request.args.get('page', 0)),
            limit=int(request.args.get('limit', 10)),
            filter_by=request.args.get('filter_by'),
            filter_value=request.args.get('filter_value'),
            order_by=order_by
        )

    if not success:
        return jsonify({"msg": 'deu ruim alguma coisa'}), 400

    return jsonify({"result": result}), 200


@app.route('/new_invoice', methods=['POST'])
@jwt_required
def insert_into_db():
    # month, year, document, description, amount
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
        return jsonify({"msg": 'deu ruim alguma coisa'}), 400

    return {}, 201


@app.route('/update_invoice/<int:id>', methods=['PUT'])
@jwt_required
def update_invoice(id):
    json = request.get_json()

    invoice, success = db.get_invoice_by_id(id)

    if not success:
        return {"msg": 'deu ruim alguma coisa'}, 400

    if not invoice:
        return {"msg": 'Invoice not found'}, 404

    new_month = json.get('month')
    new_year = json.get('year')
    new_document = json.get('document')
    new_description = json.get('description')
    new_amount = json.get('amount')

    if (not new_month) and (not new_year) and (not new_document) and (not new_description) and (not new_amount):
        return {"msg": "JSON have to be at least one field to update"}, 400

    month = new_month if new_month else invoice.get('ReferenceMonth')
    year = new_year if new_year else invoice.get('ReferenceYear')
    document = new_document if new_document else invoice.get('Document')
    description = new_description if new_description else invoice.get('Description')
    amount = new_amount if new_amount else invoice.get('Amount')

    success = db.update_invoice_by_id(id, month, year, document, description, amount)

    if not success:
        return jsonify({"msg": 'deu ruim alguma coisa'}), 400

    return {}, 204


@app.route('/delete_invoice/<int:id>', methods=['DELETE'])
@jwt_required
def delete_invoice(id):
    invoice, success = db.get_invoice_by_id(id)

    if not success:
        return {"msg": 'deu ruim alguma coisa'}, 400

    if not invoice:
        return {"msg": 'Invoice not found'}, 404

    success = db.delete_invoice_by_id(id)

    if not success:
        return jsonify({"msg": 'deu ruim alguma coisa'}), 400

    return {}, 204


@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


if __name__ == '__main__':
    app.run(debug=True)