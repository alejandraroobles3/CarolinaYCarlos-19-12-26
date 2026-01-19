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
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

#drive
gauth = GoogleAuth()
gauth.LoadClientConfigFile("client_secrets.json")  # tu archivo descargado
gauth.LoadCredentialsFile("token.json")


if gauth.credentials is None:
    # Primera vez que se corre: abre navegador para autorizar
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Si el token expiró, refrescarlo
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile("token.json")

drive = GoogleDrive(gauth)

gc = gspread.authorize(creds)
sheet = gc.open_by_key("1My2rjonxDkY1CsLDsOmC1N_j60DdfH5RB2EcMSlqlOE").sheet1


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
    else: 
        return render_template("index.html")


@app.route("/enviar", methods=["POST","GET"])
def enviar():
    #aqui ponemos la carta que se abre? 
    if request.method == "POST":
        nombre=request.form.get("nombre")
        apellido=request.form.get("apellido")
        adultos=request.form.get("adultos")
        ninios=request.form.get("ninios")
        siva=request.form.get("asiste")

        archivo = request.files.get('foto')

        if archivo:
            ruta_local = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
            archivo.save(ruta_local)

            # Subir a tu Drive
            archivo_drive = drive.CreateFile({'title': archivo.filename, 'parents': [{'id': '1K-uqMefDDWUruS_9tHItqmHl5X4xtcww'}]})
            archivo_drive.SetContentFile(ruta_local)
            archivo_drive.Upload()

            # Dar permiso de lectura (opcional)
            archivo_drive.InsertPermission({
                'type': 'anyone',
                'value': 'anyone',
                'role': 'reader'
            })

            link_drive = archivo_drive['alternateLink']

        else:
            link_drive=""
    
        
        sheet.append_row([
            nombre,
            apellido,
            siva,
            adultos,
            ninios,
            link_drive
        ])
        return render_template("exito.html")
        
        
    elif request.method == "GET":
        return render_template("index.html")

    else:
        return render_template("index.html")
    

if __name__ == "__main__":
    app.run(debug=True)