from flask import Flask, jsonify, request
import db


app = Flask(__name__)


@app.route('/invoices', methods=['GET'])
@app.route('/invoices/<int:id>', methods=['GET'])
def index(id=None):
    if id is None:
        page = request.args.get('page')
        limit = request.args.get('limit')
        filter_by = request.args.get('filter_by')
        order_by = request.args.get('order_by')

        result, success = db.get_all_invoices()
    else:
        result, success = db.get_invoice_by_id(id)
        if success and (not result):
            return {"msg": 'Invoice not found'}, 404

    if not success:
        return jsonify({"msg": 'deu ruim alguma coisa'}), 400

    return jsonify({"result": result}), 200


@app.route('/new_invoice', methods=['POST'])
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


@app.route('/edit_resource/<int:id>', methods=['PUT'])
def edit_resource(id):
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


@app.route('/invoices_by_year/<int:year>', methods=['GET'])
def invoices_by_year(year):
    result, success = db.get_invoices_by_year(year)

    if not success:
        return jsonify({"msg": 'deu ruim alguma coisa'}), 400

    return {"result": result}, 200


@app.route('/invoices_by_month/<int:month>', methods=['GET'])
def invoices_by_month(month):
    result, success = db.get_invoices_by_month(month)

    if not success:
        return jsonify({"msg": 'deu ruim alguma coisa'}), 400

    return {"result": result}, 200


@app.route('/invoices_by_document/<string:document>', methods=['GET'])
def invoices_by_document(document):
    result, success = db.get_invoices_by_document(document)

    if not success:
        return jsonify({"msg": 'deu ruim alguma coisa'}), 400

    return {"result": result}, 200


# @app.route('/invoices_filter/<int:month>', methods=['GET'])
# @app.route('/invoices_filter/<int:year>', methods=['GET'])
# @app.route('/invoices_filter/<string:document>', methods=['GET'])
# def invoices_filter(month=None, year=None, document=None):
#     if month is not None :
#         result, success = get_invoices_by_month(month)
#     elif year is not None:
#         result, success = get_invoices_by_year(year)
#     elif document is not None:
#         result, success = get_invoices_by_document(document)

#     if not success:
#         return jsonify({"msg": 'deu ruim alguma coisa'}), 400

#     return {"result": result}, 200


@app.route('/invoices_by_pagination', methods=['GET'])
def invoices_by_pagination():
    page = request.args.get('page', 1)
    limit = request.args.get('limit', 10)

    result, success = db.get_pagination_invoice(int(page), int(limit))

    if not success:
        return jsonify({"msg": 'deu ruim alguma coisa'}), 400

    return {"result": result}, 200


# @app.route('', methods=['PATCH'])


if __name__ == '__main__':
    app.run(debug=True)