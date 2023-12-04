from flask import Flask, render_template, request
from utils import scrape_general, scrape_antartica, scrape_buscalibre



app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/search",  methods=['GET', 'POST'])
def search_book():
    if request.method == 'POST':
        # Procesa los datos del formulario aquí
        titulo = request.form['title']
        autor = request.form['author']
        ans = scrape_general(titulo, autor)
        # Realiza alguna acción con los datos, por ejemplo, mostrarlos en otra página
        return render_template("price_comparison.html", books = ans)
    return render_template('search.html')



@app.route("/about")
def about():
    return render_template('about.html')



    


    




