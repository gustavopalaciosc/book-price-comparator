from flask import Flask, render_template
import subprocess
from utils import scrape_antartica



app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/scrape')
def scrape():
    ans = [scrape_antartica("guerra y paz", "leon tolstoi")]
    return render_template("price_comparison.html", headlines = ans)

    


    




