import os
from graphviz import Graph

# Especificar la ruta completa al ejecutable dot
graph = Graph()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from graphviz import Digraph
from lexico import AnalizadorLexico
from sintactico import AnalizadorSintactico

class InterfazApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Código")
        self.archivo_actual = None
        self.crear_menu()
        self.crear_areas()

    def crear_menu(self):
        menubar = tk.Menu(self.root)

        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Nuevo", command=self.nuevo_archivo)
        archivo_menu.add_command(label="Abrir", command=self.abrir_archivo)
        archivo_menu.add_command(label="Guardar", command=self.guardar_archivo)
        archivo_menu.add_command(label="Guardar Como", command=self.guardar_como_archivo)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.salir)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        traducir_menu = tk.Menu(menubar, tearoff=0)
        traducir_menu.add_command(label="Traducir", command=self.traducir_archivo)
        menubar.add_cascade(label="Traducir", menu=traducir_menu)

        herramientas_menu = tk.Menu(menubar, tearoff=0)
        herramientas_menu.add_command(label="Tokens", command=self.mostrar_tokens)
        herramientas_menu.add_command(label="Errores", command=self.mostrar_errores)
        menubar.add_cascade(label="Herramientas", menu=herramientas_menu)

        self.root.config(menu=menubar)

    def crear_areas(self):
        self.codigo_texto = tk.Text(self.root, wrap="word")
        self.codigo_texto.pack(fill="both", expand=True)

    def nuevo_archivo(self):
        if self.codigo_texto.get("1.0", "end-1c"):
            respuesta = messagebox.askyesnocancel("Nuevo Archivo", "¿Desea guardar los cambios antes de crear un nuevo archivo?")
            if respuesta:
                self.guardar_archivo()
            elif respuesta is None:
                return
        self.codigo_texto.delete("1.0", "end")
        self.archivo_actual = None

    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if archivo:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
            self.codigo_texto.delete("1.0", "end")
            self.codigo_texto.insert("1.0", contenido)
            self.analizar_lexico(contenido)
            self.analizar_sintactico(contenido)

    def guardar_archivo(self):
        if self.archivo_actual:
            with open(self.archivo_actual, "w") as f:
                f.write(self.codigo_texto.get("1.0", "end-1c"))
        else:
            self.guardar_como_archivo()

    def guardar_como_archivo(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            with open(archivo, "w") as f:
                f.write(self.codigo_texto.get("1.0", "end-1c"))
            self.archivo_actual = archivo

    def salir(self):
        self.root.quit()

    def analizar_lexico(self, contenido):
        analizador = AnalizadorLexico()
        lineas = contenido.split("\n")
        tokens_validos = []
        errores_lexicos = []

        for num_linea, linea in enumerate(lineas, start=1):
            tokens = analizador.analizar_linea(linea)
            for token in tokens:
                if token.tipo != "ERROR_LEXICO":
                    tokens_validos.append((num_linea, token))
                else:
                    errores_lexicos.append((num_linea, token))

        '''for num_linea, token in tokens_validos:
            print(f"Línea {num_linea}: {token.tipo}, {token.valor}")

        for num_linea, token in errores_lexicos:
            print(f"Línea {num_linea}: ERROR LÉXICO, {token.valor}")'''

    def analizar_sintactico(self, contenido):
        analizador_lexico = AnalizadorLexico()
        analizador_sintactico = AnalizadorSintactico()

        tokens_por_linea = analizador_lexico.analizar_contenido(contenido)
        estructuras_validas = []

        for num_linea, tokens in enumerate(tokens_por_linea, start=1):
            if analizador_sintactico.analizar_linea(tokens):
                estructuras_validas.append(num_linea)

        '''for num_linea, tokens in enumerate(tokens_por_linea, start=1):
            if num_linea in estructuras_validas:
                print(f"Línea {num_linea}: SINTACTICO, ESTRUCTURA VALIDA")
            else:
                print(f"Línea {num_linea}: ERROR_SINTACTICO, ESTRUCTURA NO VALIDA")'''

    def traducir_archivo(self):
        contenido = self.codigo_texto.get("1.0", "end-1c")

        analizador_lexico = AnalizadorLexico()
        tokens_por_linea = analizador_lexico.analizar_contenido(contenido)

        traduccion = self.traducir_contenido(tokens_por_linea)

        ventana_traduccion = tk.Toplevel(self.root)
        ventana_traduccion.title("Traducción a MongoDB")

        cuadro_traduccion = tk.Text(ventana_traduccion, wrap="word")
        cuadro_traduccion.pack(fill="both", expand=True)
        
        traduccion = self.traducir_contenido(tokens_por_linea)
        if traduccion:
            cuadro_traduccion.insert(tk.END, traduccion)
        else:
            cuadro_traduccion.insert(tk.END, "No se pudo traducir el contenido.")

        # Mostrar la ventana
        ventana_traduccion.mainloop()

    def traducir_contenido(self, tokens_por_linea):
        traduccion = ""
        for tokens in tokens_por_linea:
                if len(tokens) == 0:
                    continue
                primer_token = tokens[0]
                if primer_token.tipo == "PALABRA_RESERVADA":
                    if primer_token.valor == "CrearBD":
                        traduccion += f"use('{tokens[1].valor}');\n"
                    elif primer_token.valor == "EliminarBD":
                        traduccion += "db.dropDatabase();\n"
                    elif primer_token.valor == "CrearColeccion":
                        traduccion += f"db.createCollection('{tokens[1].valor}');\n"
                    elif primer_token.valor == "EliminarColeccion":
                        traduccion += f"db.{tokens[1].valor}.drop();\n"
                    elif primer_token.valor == "BuscarTodo":
                        traduccion += f"db.{tokens[1].valor}.find();\n"
                    pass  # Devolver la traducción completa
        if traduccion:
                return traduccion
        else:
                return None

    def mostrar_tokens(self, tokens=None):
        contenido = self.codigo_texto.get("1.0", "end-1c")

        analizador_lexico = AnalizadorLexico()
        tokens_por_linea = analizador_lexico.analizar_contenido(contenido)

        tokens_validos = []
        tokens_no_validos = []
        for num_linea, tokens in enumerate(tokens_por_linea, start=1):
            for token in tokens:
                if token.tipo != "ERROR_LEXICO":
                    tokens_validos.append((num_linea, token))
                else:
                    tokens_no_validos.append((num_linea, token))

        html = self.generar_html(tokens_validos, tokens_no_validos)
        nombre_archivo_html = os.path.join(os.getcwd(), "tokens.html")

        with open(nombre_archivo_html, "w") as f:
            f.write(html)

        messagebox.showinfo("Tokens", f"Se ha generado el archivo HTML: {nombre_archivo_html}")

    def generar_html(self, tokens_validos, tokens_no_validos):
        html = "<html><head><style>table { border-collapse: collapse; } th, td { border: 1px solid black; padding: 8px; }</style></head><body>"
        html += "<h2>Tokens Válidos</h2>"
        html += "<table><tr><th>Línea</th><th>Tipo</th><th>Valor</th></tr>"
        for num_linea, token in tokens_validos:
            html += f"<tr><td>{num_linea}</td><td>{token.tipo}</td><td>{token.valor}</td></tr>"
        html += "</table>"
        html += "<h2>Tokens No Válidos</h2>"
        html += "<table><tr><th>Línea</th><th>Error</th><th>Valor</th></tr>"
        for num_linea, token in tokens_no_validos:
            html += f"<tr><td>{num_linea}</td><td>{token.tipo}</td><td>{token.valor}</td></tr>"
        html += "</table></body></html>"
        return html

    def mostrar_errores(self):
        contenido = self.codigo_texto.get("1.0", "end-1c")

        analizador_lexico = AnalizadorLexico()
        errores_lexicos = self.obtener_errores_lexicos(analizador_lexico, contenido)

        html = self.generar_html_errores(errores_lexicos)
        nombre_archivo_html = os.path.join(os.getcwd(), "errores.html")

        with open(nombre_archivo_html, "w") as f:
            f.write(html)

        messagebox.showinfo("Errores", f"Se ha generado el archivo HTML de errores: {nombre_archivo_html}")

    def obtener_errores_lexicos(self, analizador_lexico, contenido):
        errores_lexicos = []
        lineas = contenido.split("\n")
        for num_linea, linea in enumerate(lineas, start=1):
            errores = analizador_lexico.analizar_linea(linea)
            for error in errores:
                if error.tipo == "ERROR_LEXICO":
                    errores_lexicos.append((num_linea, error.valor))
        return errores_lexicos
    
    def generar_html_errores(self, errores):
        html = "<html><head><style>table { border-collapse: collapse; } th, td { border: 1px solid black; padding: 8px; }</style></head><body>"
        html += "<h2>Errores Léxicos</h2>"
        html += "<table><tr><th>Línea</th><th>Error</th><th>Valor</th></tr>"
        for num_linea, error in errores:
            html += f"<tr><td>{num_linea}</td><td>Error Léxico</td><td>{error}</td></tr>"
        html += "</table></body></html>"
        return html

if __name__ == "__main__":
    root = tk.Tk()  # Crea la raíz 
    app = InterfazApp(root)
    root.mainloop()     

