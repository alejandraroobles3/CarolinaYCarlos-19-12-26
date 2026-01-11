from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    #aqui ponemos la carga? 
    #se necesita poner el envio y eso de lo que se recolecte
    return render_template("index.html")

@app.route("/inicio")
def inicio():
    #aqui ponemos la carga? 
    return render_template("inicio.html")


