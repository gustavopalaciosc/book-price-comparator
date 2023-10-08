import requests
from bs4 import BeautifulSoup as bs
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

"""
*********************
**** Busca Libre ****
*********************
"""
def scrape_buscalibre(search=None, autor=None):

    url = f'https://www.buscalibre.cl/libros/search?q={search}&page=1'
    url_ejemplo = f'https://www.buscalibre.cl/libros/search?q=hacia+rutas+salvajes'
    response = requests.get(url_ejemplo)

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

        for book in books:
            print("\n")
            print(book.find('h3', class_='nombre margin-top-10 text-align-left').text)
            print(book.find('div', class_='autor').text)
            print(book['data-precio'])
            vectors = vectorizer.fit_transform([autor, str(book.find('div', class_='autor').text)])
            similarity = cosine_similarity(vectors)
            print(similarity)

    else:
        print("Algo salió mal")






def scrape_greenlibros(search):
    pass

def scrape_librabooks(search):
    pass

def scrape_antartica(search):
    pass


if __name__ == "__main__":
    scrape_buscalibre()