import requests
from bs4 import BeautifulSoup as bs

"""
*********************
**** Busca Libre ****
*********************
"""
def scrape_buscalibre(search=None):


    url = f'https://www.buscalibre.cl/libros/search?q={search}'

    url_ejemplo = 'https://www.buscalibre.cl/libros/search?q=1984&page=1'

    response = requests.get(url_ejemplo)

    if response.status_code == 200:
        html_content = response.text
        soup = bs(html_content, 'html.parser')

        element = soup.find("div", class_="productos pais42")
        elementos = element.find_all("div", class_=lambda x: x and x.startswith('box-producto'))
        # La lista elementos contienen todos los bloques con la información de los respectivos libros 
        # presentes en la página
    
        #elementos = soup.find_all("div", class_="productos pais42")
        print(elementos[0].find('h3', class_='nombre margin-top-10 text-align-left').text)
        print(elementos[0].find('div', class_='autor').text)
        print(elementos[0]['data-precio'])

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