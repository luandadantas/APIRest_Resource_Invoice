import sqlite3
from datetime import datetime


DATABASE = 'database.db'


def dict_factory(cursor, row):
    '''
    Function to return dict from sqlite query
    Solution found in StackOverFlow:
        https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
    '''
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_cursor():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    return conn.cursor()


def get_invoice_by_id(id):
    try:
        cursor = get_cursor()
        query = '''
            SELECT
                id,
                ReferenceMonth,
                ReferenceYear,
                Document,
                Description,
                Amount
            FROM
                invoice
            WHERE
                IsActive = 1 AND id = ?;
        '''
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        # import pdb; pdb.set_trace()
        return result, True
    except:
        return [], False


def get_many_invoices(page_number=None, limit=None, filter_by=None, order_by="CreatedAt"):
    if page_number is None and limit is None:
        return get_all_invoices()
    



def get_all_invoices():
    try:
        cursor = get_cursor()
        query = '''
            SELECT
                id,
                ReferenceMonth,
                ReferenceYear,
                Document,
                Description,
                Amount
            FROM
                invoice
            WHERE
                IsActive = 1;
        '''
        cursor.execute(query)
        result = cursor.fetchall()
        return result, True
    except:
        return [], False


def create_new_invoice(month, year, document, description, amount):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        is_active = True
        now = datetime.now()
        query = '''
            INSERT INTO invoice
            (ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, CreatedAt)
            values
            (?, ?, ?, ?, ?, ?, ?)'''
        cursor.execute(query, (month, year, document, description, amount, is_active, now))
        conn.commit()
        cursor.close()
        return True
    except:
        return False


def update_invoice_by_id(id, month, year, document, description, amount):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = '''
            UPDATE invoice
            SET ReferenceMonth=?, ReferenceYear=?, Document=?, Description=?, Amount=?
            WHERE id = ?
        '''
        cursor.execute(query, (int(month), int(year), document, description, float(amount), id))
        conn.commit()
        cursor.close()
        return True
    except:
        return False


def delete_invoice_by_id(id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        is_active = False
        now = datetime.now()
        query = '''
            UPDATE invoice
            SET IsActive=?, DeactivatedAt=?
            WHERE id=?'''

        cursor.execute(query, (is_active, now, id))
        conn.commit()
        cursor.close()
        return True
    except:
        return False


def get_invoices_by_document(document):
    try:
        cursor = get_cursor()
        query = '''
            SELECT
                id,
                ReferenceMonth,
                ReferenceYear,
                Document,
                Description,
                Amount
            FROM
                invoice
            WHERE
                IsActive = 1 AND Document=?;
        '''
        cursor.execute(query, (document,))
        result = cursor.fetchall()
        return result, True
    except:
        return [], False


def get_invoices_by_month(month):
    try:
        cursor = get_cursor()
        query = '''
            SELECT
                id,
                ReferenceMonth,
                ReferenceYear,
                Document,
                Description,
                Amount
            FROM
                invoice
            WHERE
                IsActive = 1 AND ReferenceMonth=?;
        '''
        cursor.execute(query, (month,))
        result = cursor.fetchall()
        return result, True
    except:
        return [], False


def get_invoices_by_year(year):
    try:
        cursor = get_cursor()
        query = '''
            SELECT
                id,
                ReferenceMonth,
                ReferenceYear,
                Document,
                Description,
                Amount
            FROM
                invoice
            WHERE
                IsActive = 1 AND ReferenceYear=?;
        '''
        cursor.execute(query, (year,))
        result = cursor.fetchall()
        return result, True
    except:
        return [], False


def get_pagination_invoice(page_number, limit=10, order_by="CreatedAt"):
    try:
        cursor = get_cursor()
        query = f"""
            SELECT
                id,
                ReferenceMonth,
                ReferenceYear,
                Document,
                Description,
                Amount
            FROM
                invoice
            WHERE
                id NOT IN ( SELECT
                        id
                    FROM
                        invoice
                    ORDER BY
                        {order_by} ASC LIMIT {limit*(page_number-1)} )
            ORDER BY
                {order_by} ASC LIMIT {limit}
        """
        cursor.execute(query)
        result = cursor.fetchall()
        return result, True
    except Exception as err:
        print(err)
        return [], False