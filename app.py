from flask import Flask, render_template, request, jsonify, redirect, url_for
import time
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#para activar entorno virtual es:
#venv\Scripts\activate.bat
#y luego python app.py

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='uploads'

#gauth=

@app.route("/")
def index():
    #aqui ponemos la carga? 
    #se necesita poner el envio y eso de lo que se recolecte
    return render_template("loading.html")

@app.route("/process-task")
def process_task():
    #aqui ponemos la carta que se abre?
    time.sleep(3)
    return jsonify(status="complete")

@app.route("/sobre")
def sobre():
    #aqui ponemos la carta que se abre? 
    return render_template("sobre.html")

@app.route("/pagina", methods=["POST","GET"])
def pagina():
    #aqui ponemos la carta que se abre? 
    if request.method == "POST":
        return render_template("index.html")
    elif request.method == "GET":
        return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True)