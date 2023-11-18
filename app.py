from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/crear')
def crear():
    return render_template('crear.html')

@app.route('/submit', methods=['POST'])
def submit():
    #Aquí obtenemos las restricciones y llamamos al modelo
    name = request.form['name']
    return render_template('pista.html', message='Hello, Flask!')

if __name__ == "__main__":
    app.run(debug=True)