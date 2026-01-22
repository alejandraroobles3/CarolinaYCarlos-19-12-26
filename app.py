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

# NOTA: Para este código, necesitarás definir 3 variables de entorno en Railway/Local:
# 1. GDRIVE_CREDENTIALS_DATA (El contenido de tu mycreds.txt)
# 2. GDRIVE_CLIENT_SECRETS_DATA (El contenido de tu client_secrets.json)
# 3. GOOGLE_SHEETS_SERVICE_ACCOUNT (El contenido de tu service_account.json para gspread)

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def login_drive():
    gauth = GoogleAuth()
    
    # 1. Forzar la carga de secretos desde la variable de entorno
    client_secrets_data = os.environ.get("GDRIVE_CLIENT_SECRETS_DATA")
    if not client_secrets_data:
        raise Exception("ERROR: La variable GDRIVE_CLIENT_SECRETS_DATA está vacía.")
    
    # Escribir el archivo físico que pydrive2 exige
    with open("client_secrets.json", "w") as f:
        f.write(client_secrets_data)
    
    # Configurar pydrive para usar ese archivo
    gauth.LoadClientConfigFile("client_secrets.json")

    # 2. Cargar tokens (mycreds)
    creds_data = os.environ.get("GDRIVE_CREDENTIALS_DATA")
    if creds_data:
        with open("mycreds.txt", "w") as f:
            f.write(creds_data)
        gauth.LoadCredentialsFile("mycreds.txt")
    
    # 3. Lógica de autenticación sin navegador
    if gauth.credentials is None:
        # Si llega aquí en Railway, va a fallar porque no puede abrir navegador
        # Debes asegurarte de que GDRIVE_CREDENTIALS_DATA sea válido
        raise Exception("Error: No hay credenciales válidas en GDRIVE_CREDENTIALS_DATA. Genera el archivo mycreds.txt en tu PC primero.")
    elif gauth.access_token_expired:
        print("Token expirado, refrescando...")
        gauth.Refresh()
    else:
        gauth.Authorize()
    
    return GoogleDrive(gauth)



# --- Inicialización de servicios ---

# Para Sheets, usaremos un enfoque de Cuenta de Servicio (Service Account)
# que es mucho mejor para servidores que usar las credenciales del Drive personal.

# 3. Leer Service Account desde variable de entorno
service_account_data = os.environ.get("GOOGLE_SHEETS_SERVICE_ACCOUNT")

if service_account_data:
    # Creamos un archivo temporal para gspread
    with open("service_account.json", "w") as f:
        f.write(service_account_data)
    
    # Autenticar gspread usando el archivo temporal
    gc = gspread.service_account(filename="service_account.json")
    os.remove("service_account.json") # Borrar archivo temporal inmediatamente
else:
    # Si la variable no existe (ej. en desarrollo local sin configurar), usar el método anterior
    drive = login_drive()
    gc = gspread.authorize(drive.auth.credentials)


SHEET_ID = "1My2rjonxDkY1CsLDsOmC1N_j60DdfH5RB2EcMSlqlOE"
sheet = gc.open_by_key(SHEET_ID).sheet1


ID_CARPETA_DESTINO = '1K-uqMefDDWUruS_9tHItqmHl5X4xtcww'

# ... El resto de tus rutas (@app.route) permanecen sin cambios ...

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
        link_drive='-'

        
        if archivo and archivo.filename:
            filename = f"{nombre}_{apellido}_{int(time.time())}"
            ruta_local = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archivo.save(ruta_local)

            try:
                # Subida directa usando TU espacio de 15GB
                # NOTA: Debes acceder a la variable global 'drive' si no usas la Service Account
                global drive 
                archivo_drive = drive.CreateFile({
                    'title': filename,
                    'parents': [{'id': ID_CARPETA_DESTINO}]
                })
                archivo_drive.SetContentFile(ruta_local)
                archivo_drive.Upload()

                # Hacer público
                archivo_drive.InsertPermission({
                    'type': 'anyone',
                    'value': 'anyone',
                    'role': 'reader'
                })

                link_drive = archivo_drive['alternateLink']
                del archivo_drive

            except Exception as e:
                print(f"Error al subir a Drive: {e}")
                link_drive = "Error en la subida"
            finally:
            # El bloque finally se ejecuta SIEMPRE, incluso si hubo error arriba
                if ruta_local and os.path.exists(ruta_local):
                    try:
                        # Esperar un microsegundo para que Windows suelte el archivo
                        time.sleep(0.2) 
                        os.remove(ruta_local)
                        print(f"Archivo temporal {filename} borrado con éxito.")
                    except Exception as e:
                        print(f"No se pudo borrar el archivo: {e}")
        # Guardar en Google Sheets
        try:
            sheet.append_row([
                nombre,
                apellido,
                siva,
                adultos,
                ninios,
                link_drive
            ])
        except Exception as e:
            print(f"Error en Sheets: {e}")

        return render_template("exito.html")

    
    elif request.method == "GET":
        return render_template("index.html")

    else:
        return render_template("index.html")


if __name__ == "__main__":
    # Asegúrate de tener gunicorn instalado y usar un Procfile para Railway
    port = int(os.environ.get("PORT",5000))
    # use_reloader=False es importante para evitar la doble ejecución
    app.run(host="0.0.0.0", use_reloader=False, port=port)
