from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
from database import service, utils
from datetime import date
import random
import requests
import secrets

password = f"Bearer {secrets.SECRETS['notion_test']}"
databases_id = "a3cedef259db4682bb5529e5035be18d"
headers = {
    "Authorization": password,
    "Notion-version": "2021-05-13"
}
# query = {
#     "filter": {
#         "property":
#             "Realizado",
#             "checkbox": {
#                 "equals": True
#             }
#     }
# }

database = service.retrieveDatabase(
    databaseId=databases_id,
    headers=headers,
    save_to_json=True
)

utils.debugDatabaseObject(database)

database_list = utils.decodeDatabase(database)
dbProperties = utils.databaseProperties(database_list)


def html_table_column(lista_titulos):
    yield "\t    <tr>"
    for columna in lista_titulos:
        yield f"\t\t<th>{columna}</th>"
    yield "\t    </tr>\n"


def html_table_row(lista_filas, lista_columns):
    for fila in lista_filas:
        yield "\t    <tr>"
        for columna in lista_columns:
            if columna not in fila:
                fila[columna] = ""
            yield f"\t\t<td>{fila[columna]}</td>"
        yield "\t    </tr>"


def construct_html_table(columnas, filas):
    return '<table class="styled-table">\n' + columnas + filas + "\n\t</table>"


titulos = "\n".join(html_table_column(dbProperties))
filas = "\n".join(html_table_row(
    database_list,
    dbProperties
))


def construct_html_msg(table, style, quote):
    html_template = f"""\
<html>
    <head>
    <style>
{style}
    </style>
    </head>
    <body>
        <h1>Tareas del dia ✅</h1>
        {table}
        <h1>Frase del dia 🧠</h1>
        {quote}
    </body>
</html>
"""
    return html_template


# Reference https://dev.to/dcodeyt/creating-beautiful-html-tables-with-css-428l
style = """\
        .styled-table {
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9em;
            font-family: sans-serif;
            min-width: 400px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }

        .styled-table thead tr {
            background-color: #009879;
            color: #ffffff;
            text-align: left;
        }

        .styled-table th,
        .styled-table td {
            padding: 12px 15px;
        }

        .styled-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }

        .styled-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }

        .styled-table tbody tr:last-of-type {
            border-bottom: 2px solid #009879;
        }

        .styled-table tbody tr.active-row {
            font-weight: bold;
            color: #009879;
        }

        h1 {
            color: #009879;
            font-family: arial, sans-serif;
            font-size: 16px;
            font-weight: bold;
            margin-top: 0px;
            margin-bottom: 1px;
        }
"""


def random_stoic_quote() -> tuple[str, str]:
    # url contract
    random_id = random.randint(0, 1000)
    url = f"https://stoic-server.herokuapp.com/quotes/{random_id}"

    # GET
    response = requests.get(url=url)

    if response.status_code == 200:
        return response.json()[0]["author"], response.json()[0]["body"]
    else:
        return "Error", "Error en random_stoic_quote"


author, stoic_quote = random_stoic_quote()


def quote_html(author, quote):
    quote_html = f"""\
<div>
    <blockquote>
        <p>{quote}</p>
        <cite>{author}</cite>
    </blockquote>
</div>
"""
    return quote_html


table = construct_html_table(titulos, filas)
html = construct_html_msg(table, style, quote_html(author, stoic_quote))
print(html)


send_mail = True
if send_mail:
    me = "carles.serra33@gmail.com"
    you = "carles.serra33@gmail.com"

    # Create message container - the correct MIME type is multipart/alternative
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Today schedule {date.today().strftime('%B %d, %Y')}"
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    # text = "Buenos días Carles!\n"

    # Record the MIME types of both parts - text/plain and text/html.
    # part1 = MIMEText(text)
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    # msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("carles.serra33@gmail.com", secrets.SECRETS['gmail'])

    # send email
    server.sendmail(me, you, msg.as_string())
    server.quit()
