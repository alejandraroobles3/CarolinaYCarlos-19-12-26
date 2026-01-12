from flask import Flask, render_template, request, jsonify
import time
#para activar entorno virtual es:
#venv\bin\activate.bat
#y luego python app.py

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)