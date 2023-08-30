import tkinter as tk
from tkinter import filedialog
import cv2
import torch
import shutil
from PIL import ImageTk, Image, ImageDraw
import os
from PIL import ImageFont
import datetime

# Variables globales
ruta_imagen_cargada = ""  # Ruta de la imagen cargada
ruta_imagen_detectada = ""
coordenadas_circulos = []  # Lista para almacenar las coordenadas de los círculos
contador_estomas = 0  # Contador de estomas

# Función para cargar y procesar la imagen
def cargar_imagen():
    global ruta_imagen_cargada
    
    # Abrir el cuadro de diálogo para seleccionar la imagen
    ruta_imagen = filedialog.askopenfilename(initialdir="./", title="Seleccionar imagen",
                                             filetypes=(("Archivos de imagen", ".png;.jpg;.jpeg"), ("Todos los archivos", ".*")))
    
    if ruta_imagen:
        # Cargar la imagen seleccionada
        ruta_imagen_cargada = ruta_imagen
        
        # Mostrar la imagen cargada en el segundo marco
        imagen_cargada = Image.open(ruta_imagen)
      #  imagen_cargada = imagen_cargada.resize((500, 400), Image.ANTIALIAS)
        #imagen_cargada = imagen_cargada.resize((500, 400), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.ANTIALIAS)
        imagen_cargada = imagen_cargada.resize((500, 400))

        imagen_cargada_tk = ImageTk.PhotoImage(imagen_cargada)
        
        etiqueta_imagen_cargada.configure(image=imagen_cargada_tk)
        etiqueta_imagen_cargada.image = imagen_cargada_tk
        
def cambiar_puntero():
    global ruta_imagen_detectada, coordenadas_circulos

    # Cargar la imagen deseada en el recuadro de la imagen detectada
    ruta_imagen = "deteccion.png"
    
    
    imagen_detectada = Image.open(ruta_imagen)

    # Redimensionar la imagen al tamaño del marco de la imagen detectada
    ancho_marco = marco_imagen_detectada.winfo_width()
    alto_marco = marco_imagen_detectada.winfo_height()
    imagen_detectada = imagen_detectada.resize((ancho_marco, alto_marco))

    #imagen_detectada = imagen_detectada.resize((ancho_marco, alto_marco), Image.ANTIALIAS)
    imagen_detectada = imagen_detectada.rotate(180)

    # Mostrar la imagen en el marco de la imagen detectad
    imagen_detectada_tk = ImageTk.PhotoImage(imagen_detectada)
    etiqueta_imagen.configure(image=imagen_detectada_tk)
    etiqueta_imagen.image = imagen_detectada_tk

    # Actualizar la ruta de la imagen detectada y reiniciar la lista de coordenadas de los círculos
    ruta_imagen_detectada = ruta_imagen
    coordenadas_circulos = []
    etiqueta_imagen.bind("<Button-1>", dibujar_circulo)
    etiqueta_imagen.bind("<Button-3>", dibujar_circulo) 


def dibujar_circulo(event):
    global ruta_imagen_cargada, coordenadas_circulos, contador_estomas

    if ruta_imagen_cargada:
        # Obtener el tamaño del marco de imagen detectada
        ancho_marco = marco_imagen_detectada.winfo_width()
        alto_marco = marco_imagen_detectada.winfo_height()

        # Cargar la imagen detectada original
        imagen_detectada = Image.open(ruta_imagen_detectada)

        # Redimensionar la imagen al tamaño del marco
        imagen_detectada = imagen_detectada.resize((ancho_marco, alto_marco))
        imagen_detectada = imagen_detectada.rotate(180)

        # Crear una imagen en blanco del mismo tamaño que la imagen detectada
        imagen_con_circulo = Image.new("RGB", (ancho_marco, alto_marco))

        # Copiar la imagen detectada original a la imagen con círculo
        imagen_con_circulo.paste(imagen_detectada, (0, 0))

        # Dibujar los círculos existentes en la imagen con círculo
        dibujo = ImageDraw.Draw(imagen_con_circulo)
        for coordenada in coordenadas_circulos:
            color = coordenada[2]
            x, y, radio = coordenada[0], coordenada[1], coordenada[3]
            dibujo.ellipse((x, y, x + radio * 2, y + radio * 2), outline=color, width=2)

        # Calcular la escala para convertir las coordenadas del evento al tamaño de la imagen detectada
        escala_x = imagen_detectada.size[0] / ancho_marco
        escala_y = imagen_detectada.size[1] / alto_marco

        # Calcular el radio del círculo
        radio = int(min(ancho_marco, alto_marco) / 20)  # La mitad del tamaño del círculo actual

        # Calcular las coordenadas desplazadas para dibujar el círculo
        x = int(event.x * escala_x) - radio
        y = int(event.y * escala_y) - radio

        # Agregar las coordenadas del círculo a la lista
        coordenadas_circulos.append((x, y, "red" if event.num == 3 else "yellow", radio))

        # Dibujar el círculo recién agregado en la imagen con círculo
        color = "red" if event.num == 3 else "yellow"
        dibujo.ellipse((x, y, x + radio * 2, y + radio * 2), outline=color, width=2)

        # Mostrar la imagen con los círculos en el marco de imagen detectada
        imagen_con_circulo_tk = ImageTk.PhotoImage(imagen_con_circulo)
        etiqueta_imagen.configure(image=imagen_con_circulo_tk)
        etiqueta_imagen.image = imagen_con_circulo_tk

        if event.num == 3:  # Solo si es clic derecho
            contador_estomas -= 1
        elif event.num == 1:
            contador_estomas += 1
        etiqueta_cantidad_estomas.configure(text=f"Estomas detectados: {contador_estomas}")


def descargar_imagen_cargada4():
    global ruta_imagen_detectada, coordenadas_circulos, contador_estomas

    if ruta_imagen_detectada:
        # Cargar la imagen detectada
        imagen_detectada = Image.open(ruta_imagen_detectada)
        imagen_detectada = imagen_detectada.resize((500, 400))

        # Rotar la imagen detectada horizontalmente en forma de espejo
        imagen_detectada = imagen_detectada.rotate(180)

        # Redimensionar los círculos según el tamaño de la imagen detectada
        ancho_marco = marco_imagen_detectada.winfo_width()
        alto_marco = marco_imagen_detectada.winfo_height()
        escala_x = imagen_detectada.size[0] / ancho_marco
        escala_y = imagen_detectada.size[1] / alto_marco

        # Crear una nueva imagen para dibujar los círculos
        imagen_circulos = Image.new("RGBA", imagen_detectada.size)

        # Dibujar los círculos en la nueva imagen con el desplazamiento
        dibujo = ImageDraw.Draw(imagen_circulos)
        for coordenada in coordenadas_circulos:
            x = int(coordenada[0] * escala_x) + 20
            y = int(coordenada[1] * escala_y) + 18
            radio = int(coordenada[3] * escala_x)  # Obtener el radio desde la coordenada
            color = coordenada[2]  # Obtener el color desde la coordenada
            dibujo.ellipse(
                (x - radio, y - radio, x + radio, y + radio),
                outline=color, width=2
                )

        # Combinar la imagen detectada y la imagen de los círculos
        imagen_resultado = Image.alpha_composite(imagen_detectada.convert("RGBA"), imagen_circulos)

        # Agregar un encabezado centrado a la imagen resultante
        encabezado = f"Total de estomas: {contador_estomas}"
        header_height = 30
        header_color = (255, 255, 255, 200)  # Blanco con transparencia

        # Agregar un pie de página centrado a la imagen resultante
        fecha_solo = datetime.date.today()
        pie_pagina = f"{fecha_solo}. Uniamazonia. ING Sistemas               "
        footer_height = 30
        footer_color = (255, 255, 255, 200)  # Blanco con transparencia
        footer_font_color = (0, 0, 0)  # Negro

        # Crear una nueva imagen con el tamaño de la imagen resultante más el encabezado y el pie de página
        imagen_final = Image.new(
            "RGBA",
            (imagen_resultado.width, imagen_resultado.height + header_height + footer_height),
            (255, 255, 255, 0),  # Fondo transparente
        )

        # Crear una imagen blanca para la ventana del encabezado
        header_window = Image.new(
            "RGBA",
            (imagen_final.width, header_height),
            header_color
        )
        imagen_final.paste(header_window, (0, 0))

        # Copiar la imagen resultante en la nueva imagen
        imagen_final.paste(imagen_resultado, (0, header_height))

        # Crear un objeto ImageDraw para dibujar en la nueva imagen
        draw = ImageDraw.Draw(imagen_final)

        # Dibujar el texto del encabezado en la nueva imagen
        draw.text(((imagen_final.width - (header_height+295)), (header_height-25)), encabezado, font=ImageFont.truetype("arial.ttf", 18),fill=footer_font_color)

        # Crear una imagen blanca para la ventana del pie de página
        footer_window = Image.new(
            "RGBA",
            (imagen_final.width, footer_height),
            footer_color
        )
        imagen_final.paste(footer_window, (0, imagen_resultado.height + header_height))

        # Dibujar el texto del pie de página en la nueva imagen
        draw.text((97, 435), pie_pagina, font=ImageFont.truetype("arial.ttf", 18), fill=footer_font_color)

        # Guardar la imagen resultante en un archivo
        ruta_imagen_descargada = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=(("Archivos de imagen", ".png"), ("Todos los archivos", ".*"))
        )
        if ruta_imagen_descargada:
            imagen_final.save(ruta_imagen_descargada)


            
def descargar_imagen_detectada():
    #imagen detectada
    global ruta_imagen_detectada
    
    if ruta_imagen_detectada:
        # Copiar el archivo de la imagen detectada
        shutil.copyfile(ruta_imagen_detectada, "imagen_detectada.png")

def realizar_diagnostico(modelo):
    global ruta_imagen_cargada, contador_estomas
    contador_estomas=0
    

    if ruta_imagen_cargada:
        # Cargar la imagen seleccionada
        imagen = cv2.imread(ruta_imagen_cargada)

        # Aplicar una rotación de 90 grados a la imagen en sentido horario
        imagen = cv2.rotate(imagen, cv2.ROTATE_90_CLOCKWISE)

        # Realizar la detección de estomas
        resultados = modelo(imagen)

        # Obtener los cuadros delimitadores de los estomas
        cuadros = resultados.pandas().xyxy[0][['xmin', 'ymin', 'xmax', 'ymax']]

        # Mostrar la cantidad de estomas en el Label
        cantidad_estomas = cuadros.shape[0]
        contador_estomas += cantidad_estomas
        etiqueta_cantidad_estomas.configure(text=f"Estomas detectados: {contador_estomas}")

        # Crear una copia de la imagen original
        imagen_detectada = imagen.copy()

        # Dibujar los cuadros delimitadores de los estomas
        for _, cuadro in cuadros.iterrows():
            x1, y1, x2, y2 = int(cuadro['xmin']), int(cuadro['ymin']), int(cuadro['xmax']), int(cuadro['ymax'])
            cv2.rectangle(imagen_detectada, (x1, y1), (x2, y2), (0, 255, 0), 5)

        # Guardar la imagen detectada sin el nombre de la clase ni el porcentaje de confianza en un archivo
        nombre_archivo = "deteccion.png"
        ruta_imagen_detectada = os.path.join(os.getcwd(), nombre_archivo)
        cv2.imwrite(ruta_imagen_detectada, imagen_detectada)

        # Rotar la imagen detectada en sentido horario
        imagen_detectada = cv2.rotate(imagen_detectada, cv2.ROTATE_180)

        # Mostrar la imagen con los estomas detectados en el marco de detección
        imagen_detectada = Image.fromarray(imagen_detectada)
        imagen_detectada = imagen_detectada.resize((500, 400))

        #imagen_detectada = imagen_detectada.resize((500, 400), Image.ANTIALIAS)
        imagen_tk = ImageTk.PhotoImage(imagen_detectada)

        etiqueta_imagen.configure(image=imagen_tk)
        etiqueta_imagen.image = imagen_tk

ventana = tk.Tk()
ventana.title("Detector Estomas")
ventana.geometry("1200x550")
ventana.configure(bg="#222222") 

# Crear el título centrado en negrita, cursiva y tamaño 18
titulo = tk.Label(ventana, text="Detector de estomas", font=("Arial", 28, "bold italic"), bg="#222222", fg="white")
titulo.pack(pady=20)

# Cargar el modelo YOLOv5
try:
     model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')
     
     #model = torch.hub.load('ultralytics/yolov5:v5.0.0', 'yolov5s',path='C:/Users/LENOVO/Desktop/ProyectoEstomas/best.pt', pretrained=True, force_reload=True)

     print("Model loaded successfully.")
except Exception as e:
   
     print("Error loading the model:", e)
finally:
     #model = torch.hub.load('ultralytics/yolov5:v5.0.0', 'yolov5s',path='C:/Users/LENOVO/Desktop/ProyectoEstomas/best.pt', pretrained=True, force_reload=True)
     model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')

# Crear el segundo marco para mostrar la imagen cargada
marco_imagen_cargada = tk.LabelFrame(ventana, text="Imagen Cargada", width=500, height=400, relief=tk.SOLID, bd=2)
marco_imagen_cargada.pack(side=tk.LEFT, padx=10, pady=20)
marco_imagen_cargada.pack_propagate(False)

# Crear un lienzo dentro del segundo marco para mostrar la imagen cargada
lienzo_imagen_cargada = tk.Canvas(marco_imagen_cargada, width=500, height=400)
lienzo_imagen_cargada.pack()

# Etiqueta para mostrar la imagen cargada
etiqueta_imagen_cargada = tk.Label(lienzo_imagen_cargada)
etiqueta_imagen_cargada.pack()

# Crear el primer marco para mostrar la imagen detectada
marco_imagen_detectada = tk.LabelFrame(ventana, text="Imagen Detectada", width=500, height=400, relief=tk.SOLID, bd=2)
marco_imagen_detectada.pack(side=tk.LEFT, padx=10, pady=20)
marco_imagen_detectada.pack_propagate(False)

# Crear un lienzo dentro del primer marco para mostrar la imagen detectada
lienzo_imagen_detectada = tk.Canvas(marco_imagen_detectada, width=500, height=400)
lienzo_imagen_detectada.pack()

# Etiqueta para mostrar la imagen detectada
etiqueta_imagen = tk.Label(lienzo_imagen_detectada)
etiqueta_imagen.pack()

# espacio 1
esp3 = tk.Label(ventana, text="", font=("Arial", 12, "bold"), bd=2, bg="#222222")
esp3.pack()

# espacio 2
esp4 = tk.Label(ventana, text="", font=("Arial", 12, "bold"), bd=2, bg="#222222")
esp4.pack()

# Crear el Label para controles
controles = tk.Label(ventana, text="Controles", font=("Arial", 14, "bold"), bd=2, bg="#222222", fg="white")
controles.pack()

# espacio 1
esp1 = tk.Label(ventana, text="", font=("Arial", 12, "bold"), bd=2, bg="#222222")
esp1.pack()

# espacio 2
esp2 = tk.Label(ventana, text="", font=("Arial", 12, "bold"), bd=2, bg="#222222")
esp2.pack()

# Crear el botón de carga de imagen
boton_cargar = tk.Button(ventana, text="Cargar imagen", command=cargar_imagen, bg="green", fg="white", cursor="hand2")
boton_cargar.pack(pady=10)

# Crear el botón de diagnóstico
boton_diagnostico = tk.Button(ventana, text="Diagnóstico", command=lambda: realizar_diagnostico(model), bg="green", fg="white", cursor="hand2")
boton_diagnostico.pack(pady=10)

# Crear el botón de cambio de 
boton_cambiar_puntero = tk.Button(ventana, text="Agregar Estoma", command=cambiar_puntero, bg="green", fg="white", cursor="hand2")
boton_cambiar_puntero.pack(pady=10)

# Crear el botón de descarga de la imagen cargada
boton_descargar_cargada = tk.Button(ventana, text="Descargar imagen", command=descargar_imagen_cargada4, bg="green", fg="white", cursor="hand2")
boton_descargar_cargada.pack(pady=10)

# Crear el Label para mostrar la cantidad de estomas
etiqueta_cantidad_estomas = tk.Label(ventana, text="Estomas detectados: 0", font=("Arial", 10, "bold"), bd=2, bg="#222222", fg="white")
etiqueta_cantidad_estomas.pack()

# Cargar la imagen para el ícono de la ventana
ruta_icono = "Marca mixta UA vertical - COLOR.ico"
ventana.iconbitmap(ruta_icono)

# Iniciar el bucle principal de la ventana
ventana.mainloop()