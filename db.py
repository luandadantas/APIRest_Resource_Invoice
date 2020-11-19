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


def get_invoice_by_id(id):
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        query = '''
            SELECT
                id,
                ReferenceMonth AS month,
                ReferenceYear AS year,
                Document AS document,
                Description AS description,
                Amount AS amount
            FROM
                invoice
            WHERE
                IsActive = 1 AND id = ?;
        '''
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        return result, True
    except:
        return [], False


def get_invoices(
    page_number=None,
    limit=10,
    filter_by=None,
    filter_value=None,
    order_by=None
):
    where_filter = ""
    
    if not order_by:
        order_by = ["CreatedAt"]
    
    order_by = [ob + " ASC" for ob in order_by]
    order_by = ", ".join(order_by)

    if page_number:
        pagination_filter = f"""
            id NOT IN ( SELECT
                id
            FROM
                invoice
            ORDER BY
                {order_by} LIMIT {limit*(page_number-1)} )
        """
        where_filter += "AND " + pagination_filter
        order_by += f" LIMIT {limit}"
    
    if filter_by and filter_value:
        where_filter += f"AND {filter_by} = {filter_value}"
    
    query = f"""
        SELECT
            id,
            ReferenceMonth AS month,
            ReferenceYear AS year,
            Document AS document,
            Description AS description,
            Amount AS amount
        FROM
            invoice
        WHERE
            IsActive = 1
            {where_filter}
        ORDER BY
            {order_by}
        ;
    """

    # print(query)

    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result, True
    except Exception as err:
        print(err)
        return [], False


def create_new_invoice(month, year, document, description, amount):
    """adds a new invoice to the database

    Args:
        month (int): [description]
        year (int): [description]
        document (str): [description]
        description (str): [description]
        amount (float): [description]

    Returns:
        bool: True
        or
        bool: False
    """
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
    """Updates an entire resource, or just parts of it, in which it is saved in a database.

    Args:
        id (int): [description]
        month (int]): [description]
        year (int): [description]
        document (str): [description]
        description (str): [description]
        amount (float): [description]

    Returns:
        bool: True
        or
        bool: False
    """
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
    """logically deletes the invoice that must be passed by the id

    Args:
        id (int): [description]

    Returns:
        bool: True
        or
        bool: False
    """
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