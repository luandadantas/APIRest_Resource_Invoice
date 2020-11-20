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
    """returns the invoice that was passed by the id,
        along with the 'invoices/<int:id>' route.

    Args:
        id (int): value that corresponds to the invoice id
         that will be returned in the request.

    Returns:
        if all goes well, it will return a dictionary format
        json file with the invoice of the id called in the
        request and a Boolean value of True. if something goes wrong, 
        it will return an empty dictionary and a false Boolean value.
    """
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
    """
    Main function, which is responsible for get invoices according to the request.

        - all invoices;
        - invoices with pagination;
        - invoices filtered by month, year and document;
        - and invoices ordered by month, year, document or combinations between.
        Can also make filters by mixing pagination, filters and sorting.

    Args:
        page_number (int, optional): [description]. Defaults to None.
        limit (int, optional): [description]. Defaults to 10.
        filter_by (str, optional): [description]. Defaults to None.
        filter_value ([type], optional): [description]. Defaults to None.
        order_by ([type], optional): [description]. Defaults to None.

    Returns:
        str: [description]
    """
    where_filter = ""
    
    if not order_by:
        order_by = ["CreatedAt"]
    
    order_by = [ob + " ASC" for ob in order_by]
    order_by = ", ".join(order_by)

    if page_number:
        pagination_filter = f"""
            id NOT IN (
            SELECT
                id
            FROM
                invoice
            ORDER BY
                {order_by} LIMIT {limit*(page_number-1)} )
        """
        where_filter += "AND " + pagination_filter
        order_by += f" LIMIT {limit}"
    
    if filter_by and filter_value:
        if filter_by == 'document':
            filter_value = f'"{filter_value}"'

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
    """adds a new invoice to the database.

    Args:
        month (int): Invoice month
        year (int): Invoice year
        document (str): Invoice document
        description (str): Invoice description
        amount (float): Invoice amount

    Returns:
        if all goes well - bool: True
        if something goes wrong - bool: False
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
    """Updates an entire invoice, or just parts of it, in which it is saved in a database.

    Args:
        id (int): id referring to the invoice that will be updated.
        month (int): new month value, if there is an update to that value in the request.
        year (int): new year value, if there is an update to that value in the request.
        document (str): new document value, if there is an update to that value in the request.
        description (str): new description value, if there is an update to that value in the request.
        amount (float): new amount value, if there is an update to that value in the request.

    Returns:
        if all goes well - bool: True
        if something goes wrong - bool: False
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
    """logically deletes the invoice that must be passed by the id.

    Args:
        id (int): id referring to the invoice that will be deleted.

    Returns:
        if all goes well - bool: True
        if something goes wrong - bool: False
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
    

def get_user_by_username(username):
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        query = f'''
            SELECT
                Username as username,
                Password as password
            FROM
                user
            WHERE
                username = "{username}";
        '''
        cursor.execute(query)
        result = cursor.fetchone()
        return result, True
    except:
        return {}, False


def create_new_user(username, hash_password):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        query = '''
            INSERT INTO user
            (Username, Password)
            values
            (?, ?)'''
        cursor.execute(query, (username, hash_password))
        conn.commit()
        cursor.close()
        return True
    except:
        return False