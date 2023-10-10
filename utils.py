import requests
from bs4 import BeautifulSoup as bs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def search_set(search):
    text = search.replace(" ", "+")
    return text

"""
*********************
**** Busca Libre ****
*********************
"""
def scrape_buscalibre(search, autor=None):
    url = f'https://www.buscalibre.cl/libros/search?q={search_set(search)}'
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        soup = bs(html_content, 'html.parser')
        book_container = soup.find("div", class_="productos pais42")
        books = book_container.find_all("div", class_=lambda x: x and x.startswith('box-producto'))
        # La lista elementos contienen todos los bloques con la información de los respectivos libros 
        # presentes en la página

        if autor == None:
            autor = books[0].find('div', class_='autor').text
        
        vectorizer = TfidfVectorizer()
        min_price_book = None

        for book in books:
            vectors = vectorizer.fit_transform([autor, str(book.find('div', class_='autor').text)])
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

def scrape_greenlibros(search = None, autor = None):
    url = "https://www.greenlibros.com/search?q=guerra+y+paz"
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        soup = bs(html_content, 'html.parser')
        book_container = soup.find("div", class_="search-list")
        books = book_container.find_all("div", class_="search-item")
        for i in books:
            print("\n")
            print(i.find("a").get('href'))


    
    else:
        return None




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
    scrape_greenlibros()