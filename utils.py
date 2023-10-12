import requests
from bs4 import BeautifulSoup as bs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from text_unidecode import unidecode
from time import sleep

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

def is_author(vectorizer, autor1, autor2):
    vectors = vectorizer.fit_transform([autor1, autor2])
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

    if soup:
        book_container = soup.find("div", class_="productos pais42")
        books = book_container.find_all("div", class_=lambda x: x and x.startswith('box-producto'))
        # La lista elementos contienen todos los bloques con la información de los respectivos libros 
        # presentes en la página

        if autor == None:
            autor = unidecode(books[0].find('div', class_='autor').text)
        
        vectorizer = TfidfVectorizer()
        min_price_book = None

        for book in books:
            vectors = vectorizer.fit_transform([autor, unidecode(str(book.find('div', class_='autor').text))])
            similarity = cosine_similarity(vectors)
            is_author = float(similarity[0][1]) > 0.25 
            if is_author:
                #title = book.find('h3', class_='nombre margin-top-10 text-align-left').text
                #author = book.find('div', class_='autor').text
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
        return {'Autor': autor, 'Titulo': search, 'Precio': min_price_book}

    else:
        return None



"""
**********************
**** Green Libros ****
**********************
"""

def scrape_greenlibros(search, autor = None):
    page = 1
    busqueda = search_set(search)
    
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
                        sleep(2)
                        soup_book = get_soup(url_libro)
                        soup_book = soup_book.find("div", class_="product-info-main product-details")
                        autor_tag = soup_book.find("div", class_="product_meta").find_all("a")
                        precio = soup_book.find("div", class_="price-final").find("span").text
                        precio = precio.replace("$", "").replace(".", "")

                        for tag in autor_tag:
                            try:
                                autor = tag['title']
                                break
                            except KeyError:
                                pass
                        print(autor)
                        print(precio)
                    except:
                        pass




                page += 1
            else:
                return None

        else:
            return soup
            




"""
**********************
**** Libra Books ****
**********************
"""

def scrape_librabooks(search, autor = None):
    pass


"""
****************************
**** Librería Antartida ****
****************************
"""

def scrape_antartica(search, autor = None):
    pass


def scrape_general(search, autor = None):
    pass


if __name__ == "__main__":
    #a = scrape_buscalibre('guerra y paz')
    #print(a)
    scrape_greenlibros("don quijote de la mancha")