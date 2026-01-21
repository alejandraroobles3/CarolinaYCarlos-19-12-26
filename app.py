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

gauth = GoogleAuth()

# Archivo descargado de Google Cloud
gauth.LoadClientConfigFile("client_secrets.json")

# Configurar backend de credenciales
gauth.settings['save_credentials'] = True
gauth.settings['save_credentials_file'] = "token.json"
gauth.settings['get_refresh_token'] = True
gauth.settings['oauth_scope'] = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Cargar token si existe
gauth.LoadCredentialsFile("token.json")

# Autenticar según estado
if gauth.credentials is None:
    # Primera vez: abrir navegador (solo local)
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

# Guardar token actualizado
gauth.SaveCredentialsFile("token.json")

# Conexión con Drive
drive = GoogleDrive(gauth)

# -------------------------
# Configuración Sheets (Service Account)
# -------------------------
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json', scope
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(
    "1My2rjonxDkY1CsLDsOmC1N_j60DdfH5RB2EcMSlqlOE"
).sheet1


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


@app.route("/enviar", methods=["POST"])
def enviar():
    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    adultos = request.form.get("adultos")
    ninios = request.form.get("ninios")
    siva = request.form.get("asiste")

    archivo = request.files.get("foto")
    link_drive = ""

    if archivo and archivo.filename:
        # Genera nombre único para evitar duplicados
        filename = f"{nombre}_{apellido}_{int(time.time())}_{archivo.filename}"
        ruta_local = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        archivo.save(ruta_local)

         # Subir archivo a Drive
        archivo_drive = drive.CreateFile({'title': filename})
        archivo_drive.SetContentFile(ruta_local)
        archivo_drive.Upload()

        # Permiso de lectura pública
        archivo_drive.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })

        link_drive = archivo_drive['alternateLink']

    # Guardar datos en Google Sheets
    sheet.append_row([
        nombre,
        apellido,
        siva,
        adultos,
        ninios,
        link_drive
    ])

    return render_template("exito.html")

if __name__ == "__main__":
    app.run(debug=True)