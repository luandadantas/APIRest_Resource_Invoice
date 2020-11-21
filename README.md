# API Rest - Resource Invoice
Project created with the objective of participating in a selection process
for a junior developer position at Stone.

&nbsp;

## Description
This project is an API Rest, which will have a Resource Invoice. It was created using Python, Flask,
SQLite database and JWT for authentication. As requested, no type of ORM was used.

&nbsp;

## My Enviroment
- Linux Mint 20
- Python 3.9.0
- SQLite

&nbsp;

## Setup
it is necessary to create the database tables, executing:
`create_invoice_table.sql` and `create_user_table.sql`
```
$ pip install -r requirements.txt
$ FLASK_APP=app.py flask run
```

## Routes

`GET - /invoices/<int:id>`

Returns the invoice for the id passed in the route.

`GET - /invoices`

Returns all invoices sorted by creation date (default)

* Pagination: `/invoices?page=<int:page_number>`
Returns invoices by pagination, each page will have 10 invoices (limit default).

* Pagination with diferente limit: `/invoices?page=<int:page_number>&limit=<int:quant_inv_by_page>`
Returns the page with the number of invoices added in the limit.

* Filter by Month: `/invoices?filter_by=month&filter_value=<value_to_filter>`
Returns invoices filtered by the month called in 'filter_value'.

* Filter by Year: `/invoices?filter_by=year&filter_value=<value_to_filter>`
Returns invoices filtered by the year called in 'filter_value'.

* Filter by Document: `/invoices?filter_by=document&filter_value=<value_to_filter>`
Returns invoices filtered by the document called in 'filter_value'.

* Order by Month: `/invoices?order_by=month` Returns invoices ordered by month.
* Order by Year: `/invoices?order_by=year` Returns invoices ordered by year.
* Order by Document: `/invoices?order_by=document` Returns invoices ordered by document.
* Ordering between month, year and document: `/invoices?order_by=<month,year,document>` Add two filters or the three, separated by commas, and will return the invoices sorted between the fields informed in the request.

It is also possible:
* Pagination + filter: `/invoices?page=<int:page_number>&filter_by=<month,year or document>&filter_value=<value_to_filter>` Returns invoices paginated and filtered by what was requested, which can be month, year or document.
* Pagination + ordination: `/invoices?page=<int:page_number>&order_by=<month,year or document>` Returns invoices paginated and ordered by what was requested, which can be month, year or document.
* Filter + ordination: `/invoices?filter_by=<month,year or document>&filter_value=<value_to_filter>&order_by=<month,year or document>` Returns invoices filtered and sorted according to what was requested, both filters and sorting can come with month, year and document.

`POST - /new_invoice`
Adds a new invoice to the database.
```
{
    "month": int, (Required field)
    "year": int, (Required field)
    "document": str, (Required field)
    "description": str,
    "amount": float
}
```

`PUT - /update_invoice/<int:id>`
Update an entire invoice or just isolated information. In the request body, insert the fields that will be updated, with their new values

`DELETE - /delete_invoice/<int:id>`
A logical deletion is made to the id passed on the route.

`POST - /register`
Creates a new user who will be allowed to access the database.
```
{
    "username": str, (Required field)
    "password": str, (Required field)
}
```

`POST - /login`
logs in the user to access the database.

```
{
    "username": str, (Required field)
    "password": str, (Required field)
}
```