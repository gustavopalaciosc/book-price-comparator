import requests
from bs4 import BeautifulSoup as bs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from text_unidecode import unidecode
from time import time
import concurrent.futures


def search_set(search):
    text = search.replace(" ", "+")
    return text

def get_soup(url):
    try:
        # Agregamos un Header para evitar una respuesta negativa por parte del servidor (403)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        print(response.status_code)
        if response.status_code == 200:
            html_content = response.text
            soup = bs(html_content, 'html.parser')
            return soup
        else:
            return None
    except:
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
            books = soup.find_all("div", class_=lambda x: x and x.startswith('box-producto'))
            for book in books:
                title = book.find('h3', class_='nombre margin-top-10 text-align-left').text
                is_author = text_comp(vectorizer, autor, str(book.find('div', class_='autor').text))
                is_title = text_comp(vectorizer, search, title.lower())
                not_available = book.find('p', class_="precio-ahora margin-0 font-size-medium")
                if is_author and not not_available and is_title:
                    try:
                        price = int(book['data-precio'])
                    except:
                        price = None
                    if price:
                        if min_price_book == None or price < min_price_book:
                            min_price_book = price
            return min_price_book
    else:
        print("False")
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
        books = soup.find_all('div', class_='col-lg-3 col-md-4 col-6')
        for book in books:
            if text_comp(vectorizer, book.find('h3').find('a').text, search):
                ref = book.find('div', class_='product-block').find('a').get('href')
                book_soup = get_soup(f"https://librabooks.cl{ref}")
                author = book_soup.find('div', class_="col-12 mt-5").find('p').text
                price = book_soup.find('span', class_="product-form_price").text
                price = int(price.replace("$", "").replace(".", ""))
                if text_comp(vectorizer, author, autor):
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
    url = f'https://www.antartica.cl/catalogsearch/result/index/?q={search_set(search)}'
    soup = get_soup(url)
    vectorizer = TfidfVectorizer()
    min_price = None
    if soup:
        try:
            books = soup.find_all("li", class_='item product product-item')
            for i in range(0, 9):
                author = books[i].find("a", class_='link-autor-search-result').text
                author_bool = text_comp(vectorizer, autor, author)
                if author_bool:
                    price = float(books[i].find('span', {'data-price-amount': True})['data-price-amount'])
                    price = int(round(price))
                    if not min_price or price < min_price:
                        min_price = price
            return min_price
        except:
            return None
    else:
        return None
    

def scrape_general(search, autor):

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_buscalibre = executor.submit(scrape_buscalibre, search, autor)
        #future_greenlibros = executor.submit(scrape_greenlibros, search, autor)
        future_librabooks = executor.submit(scrape_librabooks, search, autor)
        future_antartica = executor.submit(scrape_antartica, search, autor)

        precio_buscalibre = future_buscalibre.result()
        #precio_greenlibros = future_greenlibros.result()
        precio_librabooks = future_librabooks.result()
        precio_antartica = future_antartica.result()

    return {'buscalibre': precio_buscalibre,
            'librabooks': precio_librabooks, 'antartica': precio_antartica}



if __name__ == "__main__":
    start_time = time()
    #ans = scrape_general("Clean code", "Robert C Martin")
    ans = scrape_buscalibre("Clean Code", "Robert Martin")
    end_time = time()

    exe_time = end_time - start_time
    print(f"Execution time: {exe_time}")
    print("\nResult:\n")
    print(ans)
   