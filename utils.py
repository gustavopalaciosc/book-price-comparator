import requests
from bs4 import BeautifulSoup as bs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from text_unidecode import unidecode
from time import sleep
import re


def search_set(search):
    text = search.replace(" ", "+")
    return text

def get_soup(url):
    try:
        response = requests.get(url)
    except:
        return None
    if response.status_code == 200:
        html_content = response.text
        soup = bs(html_content, 'html.parser')
        return soup
    else:
        return None

def text_comp(vectorizer, text1, text2):
    vectors = vectorizer.fit_transform([unidecode(text1), unidecode(text2)])
    similarity = cosine_similarity(vectors)
    bool_author = float(similarity[0][1]) > 0.25 
    return bool_author

"""
*********************
**** Busca Libre ****
*********************
"""
def scrape_buscalibre(search, autor):
    url = f'https://www.buscalibre.cl/libros/search?q={search_set(search)}'
    soup = get_soup(url)
    min_price_book = None
    vectorizer = TfidfVectorizer()
    if soup:
        book_container = soup.find("div", class_="productos pais42")
        if book_container:
            books = book_container.find_all("div", class_=lambda x: x and x.startswith('box-producto'))
            for book in books:
                is_author = text_comp(vectorizer, autor, str(book.find('div', class_='autor').text))
                if is_author:
                    #title = book.find('h3', class_='nombre margin-top-10 text-align-left').text
                    try:
                        price = int(book['data-precio'])
                    except:
                        price = None
                    if price:
                        if min_price_book == None:
                            min_price_book = price
                        else:
                            if price < min_price_book:
                                min_price_book = price
            return min_price_book
        else:
            return None
    else:
        return None

"""
**********************
**** Green Libros ****
**********************
"""

def scrape_greenlibros(search, autor):
    page = 1
    busqueda = search_set(search)
    min_price_book = None
    vectorizer = TfidfVectorizer()
    
    while True:
        url = f'https://www.greenlibros.com/search?page={page}&q={busqueda}'
        soup = get_soup(url)
        
        if soup:
            book_container = soup.find("div", class_="search-list")
            books = book_container.find_all("div", class_="search-item")
            if len(books) > 0:
                for book in books:
                    url_libro = f'https://www.greenlibros.com{book.find("a").get("href")}'
                    try:
                        sleep(0.5)
                        soup_book = get_soup(url_libro)
                        soup_book = soup_book.find("div", class_="product-info-main product-details")
                        autor_tag = soup_book.find("div", class_="product_meta").find_all("a")
                        titulo = soup_book.find(id="popup_cart_title").text
                        precio = soup_book.find("div", class_="price-final").find("span").text
                        precio = int(precio.replace("$", "").replace(".", ""))
                        author = autor_tag[0]['title']
                        bool_author = text_comp(vectorizer, autor, author)
                        bool_title = text_comp(vectorizer, search, titulo)
                        if bool_author and bool_title:
                            if min_price_book == None or precio < min_price_book:
                                min_price_book = precio  
                        else:
                            pass
                    except:
                        pass
                page += 1
            else:
                break
        else:
            break
    
    if min_price_book:
        return min_price_book
    else:
        return None
            
"""
**********************
**** Libra Books ****
**********************
"""

def scrape_librabooks(search, autor):
    url = f'https://librabooks.cl/search?q={search_set(search)}'
    soup = get_soup(url)
    min_price = None
    vectorizer = TfidfVectorizer()
    
    if soup:
        books = soup.find_all('div', class_='product-block')
        for book in books:
            not_available = book.find("a").get("class")
            if not not_available:
                ref = book.find("a").get("href")
                book_url = f'https://librabooks.cl{ref}'
                sleep(0.5)
                book_soup = get_soup(book_url)
                if book_soup:
                    book_content = book_soup.find("div", class_='tab-content')\
                    .find("div", class_='tab-pane fade')
                    author = book_content.find("p").text
                    if text_comp(vectorizer, autor, author):
                        price = book_soup.find("span", class_='product-form_price').text
                        price = int(price.replace(".", "").replace("$", ""))
                        if not min_price or price < min_price:
                            min_price = price
        return min_price
    else:
        return None
        

"""
****************************
**** Librería Antartida ****
****************************
"""

def scrape_antartica(search, autor):
    url = f'https://www.antartica.cl/catalogsearch/result/index/?q=+{search_set(search)}'
    soup = get_soup(url)
    vectorizer = TfidfVectorizer()
    min_price = None
    if soup:
        books = soup.find_all("li", class_='item product product-item')
        for book in books:
            author = book.find("a", class_='link-autor-search-result').text
            author_bool = text_comp(vectorizer, autor, author)
            if author_bool:
                price = float(book.find('span', {'data-price-amount': True})['data-price-amount'])
                price = int(round(price))
                if not min_price or price < min_price:
                    min_price = price
        return min_price
    else:
        return None
    
def scrape_general(search, autor):
    precio_buscalibre = scrape_buscalibre(search, autor)
    precio_greenlibros = scrape_greenlibros(search, autor)
    precio_librabooks = scrape_librabooks(search, autor)
    precio_antartica = scrape_antartica(search, autor)

    return {'buscalibre': precio_buscalibre, 'greenlibros': precio_greenlibros,
            'librabooks': precio_librabooks, 'antartica': precio_antartica}



    
   