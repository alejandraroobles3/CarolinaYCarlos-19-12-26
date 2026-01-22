from flask import Flask, render_template, request, jsonify, redirect, url_for
import time
import os
# Importamos la librería json para manejar el contenido de las variables
import json 
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gspread
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ... (tus imports igual)

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 1. Definimos drive_global como None al inicio
drive_global = None

def get_drive():
    """Función para obtener la instancia de Drive de forma segura"""
    global drive_global
    if drive_global is None:
        drive_global = login_drive()
    return drive_global

def login_drive():
    gauth = GoogleAuth()
    
    client_secrets_data = os.environ.get("GDRIVE_CLIENT_SECRETS_DATA")
    if not client_secrets_data:
        raise Exception("ERROR: La variable GDRIVE_CLIENT_SECRETS_DATA está vacía.")
    
    with open("client_secrets.json", "w") as f:
        f.write(client_secrets_data)
    
    gauth.LoadClientConfigFile("client_secrets.json")

    creds_data = os.environ.get("GDRIVE_CREDENTIALS_DATA")
    if creds_data:
        with open("mycreds.txt", "w") as f:
            f.write(creds_data)
        gauth.LoadCredentialsFile("mycreds.txt")
    
    if gauth.credentials is None:
        raise Exception("Error: Genera el archivo mycreds.txt en tu PC primero y pégalo en Railway.")
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    
    return GoogleDrive(gauth)

# --- Inicialización de Google Sheets ---
service_account_data = os.environ.get("GOOGLE_SHEETS_SERVICE_ACCOUNT")

if service_account_data:
    with open("service_account.json", "w") as f:
        f.write(service_account_data)
    gc = gspread.service_account(filename="service_account.json")
    # No borres el archivo aquí si gspread lo necesita re-leer, 
    # pero para Railway basta con cargarlo una vez.
else:
    # Si no hay service account, usamos el login tradicional
    tmp_drive = get_drive()
    gc = gspread.authorize(tmp_drive.auth.credentials)

SHEET_ID = "1My2rjonxDkY1CsLDsOmC1N_j60DdfH5RB2EcMSlqlOE"
sheet = gc.open_by_key(SHEET_ID).sheet1

ID_CARPETA_DESTINO = '1K-uqMefDDWUruS_9tHItqmHl5X4xtcww'

# ... (tus rutas index, sobre, pagina igual) ...

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
    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        adultos = request.form.get("adultos")
        ninios = request.form.get("ninios")
        siva = request.form.get("asiste")
        archivo = request.files.get('foto')
        link_drive = '-'

        if archivo and archivo.filename:
            filename = f"{nombre}_{apellido}_{int(time.time())}"
            ruta_local = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archivo.save(ruta_local)

            try:
                # CAMBIO CLAVE AQUÍ: Usamos get_drive() en lugar de la variable global directa
                drive = get_drive() 
                
                archivo_drive = drive.CreateFile({
                    'title': filename,
                    'parents': [{'id': ID_CARPETA_DESTINO}]
                })
                archivo_drive.SetContentFile(ruta_local)
                archivo_drive.Upload()

                archivo_drive.InsertPermission({
                    'type': 'anyone',
                    'value': 'anyone',
                    'role': 'reader'
                })

                link_drive = archivo_drive['alternateLink']

            except Exception as e:
                print(f"Error al subir a Drive: {e}")
                link_drive = "Error en la subida"
            finally:
                if ruta_local and os.path.exists(ruta_local):
                    try:
                        time.sleep(0.2) 
                        os.remove(ruta_local)
                    except: pass

        try:
            sheet.append_row([nombre, apellido, siva, adultos, ninios, link_drive])
        except Exception as e:
            print(f"Error en Sheets: {e}")

        return render_template("exito.html")
    
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", use_reloader=False, port=port)
