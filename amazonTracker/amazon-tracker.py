from bs4 import BeautifulSoup as bs
import requests
import re
import smtplib
import time
import os.path


def check_amazon_price(URL: str) -> float:
    """Devuelve el precio de un producto de AMAZON.ES

    Args:
        URL (str): URL de AMAZON.ES

    Returns:
        float or None: Precio del producto, pero si no se encuentra devuelve
        None
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15"
    }

    # Https url call
    try:
        page = requests.get(URL, headers=headers)
    except:
        raise Exception('La URL no existe: ' + URL)

    try:
        # Tranform https reponse to soup object (html)
        soup = bs(page.content, "html.parser")
        euro_price = soup.find(id="priceblock_ourprice").get_text().strip()

        # Obtened only the price digits and cast to float
        return float(re.search("\d+", euro_price).group())
    except:
        print('No se ha encontrado el precio, el articulo no disponible.')
        return 0.0


def send_mail(mail, password, URL):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(mail, password)

    subject = 'El precio ha bajado!'
    body = 'Link de amazon ' + URL
    message = f"Subject: {subject}\n\n{body}"

    server.sendmail(
        mail,
        mail,
        message
    )


def read_password():
    filename = '../web-scraping/password.txt'
    if not os.path.isfile(filename):
        raise Exception('Archivo', filename, 'no se ha encontrado!')
    else:
        with open(filename) as f:
            password = f.read()
            return password


URL = 'https://www.amazon.es/Beyerdynamic-770-PRO-Auriculares-estudio/dp/B008POFOHM/ref=sr_1_1?__mk_es_ES=ÅMÅŽÕÑ&crid=329TBG9NTEBJV&dchild=1&keywords=beyerdynamic+dt+770+pro&qid=1611488181&sprefix=beyer%2Caps%2C206&sr=8-1'
mail = "carles.serra33@gmail.com"
buy_price = 110
resquest_time_interval = 60 * 60 * 24
password = read_password()

while(True):
    price = check_amazon_price(URL)
    if price is not None and price <= buy_price:
        send_mail(mail, password, URL)
        print('Correo enviado!')
    else:
        print(f"Precio todavía alto: {price} >  {buy_price}")

    time.sleep(resquest_time_interval)
