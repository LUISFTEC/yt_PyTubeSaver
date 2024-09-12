from tkinter import font
from pytube import YouTube # Importar pytube
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import threading
import time
import subprocess
import re  # Importado para limpieza de nombres de archivo
import webbrowser
from PIL import Image, ImageTk
import sys
from tkinter import messagebox as tkmsgbox

# Limpiar el nombre del título para hacerlo seguro para archivos
def titulo_seguro(titulo):
    return re.sub(r'[\\/*?:"<>|]', "", titulo)

# Función de progreso personalizada
def progreso_hook(stream, chunk, bytes_remaining):
    """Función de progreso personalizada para actualizar la barra de progreso."""
    total_bytes = stream.filesize
    downloaded_bytes = total_bytes - bytes_remaining
    porcentaje = int((downloaded_bytes / total_bytes) * 100)
    progress_bar['value'] = porcentaje
    root.update_idletasks()


def combinar_video_audio_ffmpeg(video_path, audio_path, output_path):
    # Construir el comando de ffmpeg
    comando = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_path
    ]

    try:
        # Ejecutar el comando
        subprocess.run(comando, check=True)
        print(f"Archivo combinado guardado en: {output_path}")

        # Eliminar archivos temporales después de combinar
        os.remove(video_path)
        os.remove(audio_path)
    except subprocess.CalledProcessError as e:
        print(f"Error al combinar archivos: {e}")



def descargar_video_1080p(url, path):

    yt = YouTube(url)
    inicio_descarga = time.time()

    yt_title = titulo_seguro(yt.title)
    
    # Filtrar y seleccionar el flujo de video de 1080p
    video_stream = yt.streams.filter(res="1080p", mime_type="video/mp4", progressive=False).first()
    print(f"Video Stream: {video_stream}")  # Depuración
    if not video_stream:
        print("No se encontró el flujo de video.")
        return

    # Filtrar y seleccionar el flujo de audio
    audio_stream = yt.streams.filter(only_audio=True).first()
    print(f"Audio Stream: {audio_stream}")  # Depuración
    if not audio_stream:
        print("No se encontró el flujo de audio.")
        return

    # Descargar video y audio
    video_path = video_stream.download(output_path=path, filename_prefix="video_")
    print(f"Video Path: {video_path}")  # Depuración
    audio_path = audio_stream.download(output_path=path, filename_prefix="audio_")
    print(f"Audio Path: {audio_path}")  # Depuración

    # Combinar video y audio
    output_path = f"{path}/{yt_title}.mp4"
    combinar_video_audio_ffmpeg(video_path, audio_path, output_path)

    fin_descarga = time.time()
    tiempo_total = fin_descarga - inicio_descarga
    tk.messagebox.showinfo("Descarga completada", f"El video se ha descargado y procesado en {tiempo_total:.2f} segundos.")


def descargar_video(url, path, calidad, formato):
    try:
        yt = YouTube(url, on_progress_callback=progreso_hook)
        yt_title = titulo_seguro(yt.title)

        if formato == "MP4":
            # Filtrar por resolución y formato de video
            video_stream = yt.streams.filter(file_extension='mp4', res=calidad).first()
            audio_stream = yt.streams.filter(only_audio=True).first()

            if video_stream and audio_stream:
                # Descargar el video y el audio por separado
                video_path = video_stream.download(output_path=path, filename_prefix="video_")
                audio_path = audio_stream.download(output_path=path, filename_prefix="audio_")

                # Combinar video y audio usando ffmpeg
                output_path = f"{path}/{yt_title}.mp4"
                combinar_video_audio_ffmpeg(video_path, audio_path, output_path)
                messagebox.showinfo("Éxito", f"El video se ha descargado exitosamente en formato {formato}")
            else:
                messagebox.showerror("Error", "No se encontraron flujos de video o audio.")
        
        elif formato == "MP3":
            # Seleccionar solo el audio
            audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

            if audio_stream:
                audio_path = audio_stream.download(output_path=path, filename=f"{yt_title}.mp3")
                messagebox.showinfo("Éxito", f"El audio se ha descargado exitosamente en formato MP3")
            else:
                messagebox.showerror("Error", "No se encontró flujo de audio.")
    
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al descargar el video: {e}")
    finally:
        progress_bar['value'] = 0  # Resetear la barra de progreso al finalizar la descarga



def seleccionar_path():
    path = filedialog.askdirectory()
    if path:  # Verifica si se seleccionó un directorio
        path_label.config(text=path)

def comenzar_descarga():
    url = url_entry.get()
    path = path_label.cget("text")
    calidad = calidad_combo.get()
    formato = formato_combo.get()
    threading.Thread(target=descargar_video, args=(url, path, calidad, formato), daemon=True).start()

def abrir_url(url):
    webbrowser.open(url)

def cargar_imagen(ruta, nuevo_ancho=50, nuevo_alto=50):
    imagen = Image.open(ruta)
    # Usar Image.Resampling.LANCZOS para alta calidad
    imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    foto = ImageTk.PhotoImage(imagen)
    return foto

def resource_path(relative_path):
    """Devuelve la ruta absoluta del recurso, funciona para desarrollo y para PyInstaller"""
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


icon_path = resource_path('img/icono.ico')

# Modifica la función cargar_imagen para usar resource_path
def cargar_imagen(ruta, nuevo_ancho=50, nuevo_alto=50):
    ruta_completa = resource_path(ruta)
    imagen = Image.open(ruta_completa)
    imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    foto = ImageTk.PhotoImage(imagen)
    return foto

# Interfaz de usuario (UI)
root = tk.Tk()
root.resizable(False, False)

# Crear la fuente en negrita
negrita_fuente = font.Font(weight="bold")

# Usar la función resource_path para obtener la ruta correcta al archivo del ícono
icon_path = resource_path('img/icono.ico')
root.iconbitmap(icon_path)

root.title("yt_PyTubeSaver")
root.geometry("500x350")  # Tamaño de ventana ajustado para incluir la barra de progreso

# Configurar el tema para ttk widgets
style = ttk.Style()
style.theme_use('clam')  # Cambia 'clam' por el tema que prefieras

# Personalizaciones de estilo
miFuente = ("Arial", 12, "bold")
miColorFondo = "#334455"  # Un ejemplo de color hexadecimal
miColorTexto = "#FFFFFF"

# Crear un Frame como contenedor principal
frame = tk.Frame(root, bg=miColorFondo)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Crear un Label con el estilo personalizado
label = tk.Label(frame, text="© 2024 Desarrollado por luisftec con fines educativos ", font=miFuente, bg=miColorFondo, fg=miColorTexto)
label.pack(padx=5, pady=5)

# Centra la ventana en la pantalla
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 700
window_height = 350
position_x = int((screen_width / 2) - (window_width / 2))
position_y = int((screen_height / 2) - (window_height / 2))
root.geometry(f'{window_width}x{window_height}+{position_x}+{position_y}')


# URL del video
tk.Label(root, text="Pegar URL Aqui:", font=negrita_fuente,).pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Calidad del video
tk.Label(root, text="Calidad:", font=negrita_fuente,).pack()
calidad_combo = ttk.Combobox(root, values=["144p", "240p", "360p", "480p", "720p", "1080p"], state="readonly")
calidad_combo.pack(pady=5)
calidad_combo.set("720p")

# Formato del video
tk.Label(root, text="Formato:", font=negrita_fuente,).pack()
formato_combo = ttk.Combobox(root, values=["MP4", "MP3"], state="readonly")
formato_combo.pack(pady=5)
formato_combo.set("MP4")

# Seleccionar ruta de descarga
path_button = tk.Button(root, text="Seleccionar Carpeta de Descarga", command=seleccionar_path)
path_button.pack(pady=5)

path_label = tk.Label(root, text="No se ha seleccionado ninguna carpeta")
path_label.pack()

# Crear estilo personalizado para la barra de progreso (solo barra interna verde)
style = ttk.Style()
style.theme_use('default')  # Usar el tema por defecto
style.configure("TProgressbar", background='green')  # Cambiar solo la barra interna a verde

# Crear Barra de progreso
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", maximum=100)
progress_bar.pack(pady=5)

# Crear un Frame para los botones de redes sociales y descarga
botones_frame = tk.Frame(root)
botones_frame.pack(pady=10)

# Cargar y redimensionar logos para los botones
logo_github = cargar_imagen('img/github.png', 20, 20)
logo_instagram = cargar_imagen('img/ig.png', 20, 20)
logo_donar = cargar_imagen('img/donar.png', 20, 20)

# Botón de GitHub con logo
github_button = tk.Button(botones_frame, image=logo_github, 
                          command=lambda: abrir_url("https://github.com/LUISFTEC"))
github_button.image = logo_github  # Mantén una referencia
github_button.grid(row=0, column=0, padx=5)

# Botón de Descarga
download_button = tk.Button(botones_frame, text="Descargar", font=negrita_fuente, command=comenzar_descarga)
download_button.grid(row=0, column=1, padx=5)

# Botón de Donar con ícono y texto
donar_button = tk.Button(botones_frame, text="Donar ", image=logo_donar, compound="right", font=negrita_fuente, command=lambda: abrir_url("https://paypal.me/luisftec?country.x=PE&locale.x=es_XC"))
donar_button.grid(row=0, column=2, padx=5)

# Botón de Instagram con logo
instagram_button = tk.Button(botones_frame, image=logo_instagram, 
                             command=lambda: abrir_url("https://www.instagram.com/luisftec/"))
instagram_button.image = logo_instagram  # Mantén una referencia
instagram_button.grid(row=0, column=3, padx=5)

root.mainloop()