from flask import Flask, render_template, request, jsonify, redirect, url_for
import time
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gspread
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

#para activar entorno virtual es:
#venv\Scripts\activate.bat
#y luego python app.py

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def login_drive():
    gauth = GoogleAuth()
    # Carga credenciales guardadas
    gauth.LoadCredentialsFile("mycreds.txt")
    
    if gauth.credentials is None:
        # IMPORTANTE: Configurar acceso offline para obtener el refresh_token
        # y permitir que el servidor funcione sin intervención humana después
        auth_url = gauth.GetAuthUrl() # Genera la URL
        
        # Estas dos líneas son la clave:
        gauth.GetFlow()
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})
        
        # Abre el navegador para loguear
        gauth.LocalWebserverAuth()
        
    elif gauth.access_token_expired:
        # Ahora gauth.Refresh() funcionará porque tendrá el token de refresco
        gauth.Refresh()
    else:
        gauth.Authorize()
    
    # Guarda las credenciales corregidas
    gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)


# Inicializamos Drive y Sheets
drive = login_drive()

# Para Sheets, usaremos la misma autenticación de drive
# gspread puede usar las credenciales de pydrive2
gc = gspread.authorize(drive.auth.credentials)
SHEET_ID = "1My2rjonxDkY1CsLDsOmC1N_j60DdfH5RB2EcMSlqlOE"
sheet = gc.open_by_key(SHEET_ID).sheet1


ID_CARPETA_DESTINO = '1K-uqMefDDWUruS_9tHItqmHl5X4xtcww'

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
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", use_reloader=False, port=port)