import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QFileDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)
        self.setWindowTitle("Analizador Léxico, Sintáctico y Semántico")

        # Conectar los botones con los métodos respectivos
        self.pushButton.clicked.connect(self.iniciar_analisis_lexico)
        self.pushButton_2.clicked.connect(self.iniciar_analisis_sintactico)
        self.pushButtonfile.clicked.connect(self.obtener_archivo)
        # Botón para análisis semántico
        self.pushButton_3.clicked.connect(self.iniciar_analisis_semantico)

        # Configurar la tabla para el análisis léxico
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Lexema", "Token", "#"])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)

    def obtener_archivo(self):
        options = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir archivo de texto", "", "Text Files (*.txt)", options=options)
        
        if archivo:
            with open(archivo, 'r') as file:
                content = file.read()
                self.plainTextEdit_2.appendPlainText(content)

    def iniciar_analisis_lexico(self):
        texto = self.plainTextEdit_2.toPlainText()

        palabras_reservadas = ["int", "float", "void", "if", "while", "return", "else"]
        operadores = ['+', '-', '*', '/', '<', '<=', '>', '>=', '==', '!=', '&&', '||']
        delimitadores = ['(', ')', '{', '}', ';', ',']
        
        resultados = []
        i = 0
        while i < len(texto):
            c = texto[i]

            if c.isspace():
                i += 1
                continue

            if c.isalpha():
                inicio = i
                while i < len(texto) and (texto[i].isalnum() or texto[i] == '_'):
                    i += 1
                token = texto[inicio:i]
                if token in palabras_reservadas:
                    resultados.append([token, "Palabra reservada", 4])
                else:
                    resultados.append([token, "Identificador", 0])
                continue

            elif c.isdigit():
                inicio = i
                tiene_punto = False
                while i < len(texto) and (texto[i].isdigit() or (texto[i] == '.' and not tiene_punto)):
                    if texto[i] == '.':
                        tiene_punto = True
                    i += 1
                token = texto[inicio:i]
                if tiene_punto:
                    resultados.append([token, "Número real", 2])
                else:
                    resultados.append([token, "Número entero", 1])
                continue

            elif c in operadores:
                if i + 1 < len(texto) and texto[i:i+2] in operadores:
                    resultados.append([texto[i:i+2], "Operador", 7])
                    i += 2
                else:
                    resultados.append([c, "Operador", 7])
                    i += 1
                continue

            elif c in delimitadores:
                resultados.append([c, "Delimitador", 12])
                i += 1
                continue

            else:
                resultados.append([c, "Error léxico", 6])
                i += 1

        self.tableWidget.setRowCount(0)
        for fila in resultados:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            for columna, item in enumerate(fila):
                self.tableWidget.setItem(row_position, columna, QTableWidgetItem(str(item)))

    def iniciar_analisis_sintactico(self):
        texto = self.plainTextEdit_2.toPlainText().splitlines()
        errores = []
        variables_declaradas = {}
        variables_reportadas = set()  # Para evitar repetir el error de variable no declarada
        function_declaration = False  # Bandera para detectar declaración de funciones
        function_opened = False  # Bandera para detectar si la función ya tiene una llave abierta

        for num_linea, linea in enumerate(texto, start=1):
            linea = linea.strip()

            # Verificar si la línea es una declaración de función
            if linea.startswith("int main()"):
                function_declaration = True  # Marcar que se ha encontrado la declaración de la función
                continue

            # Verificar la apertura de llave después de una declaración de función
            if function_declaration:
                if linea.startswith("{"):
                    function_opened = True  # Se ha encontrado la llave
                    function_declaration = False  # Restablecer la bandera de declaración
                    continue  # Saltar a la siguiente línea

                # Si no hay una llave después de la declaración de función
                errores.append(f"Error en la línea {num_linea}: falta '{{' después de 'int main()'.")
                function_declaration = False  # Restablecer la bandera

            # Ignorar líneas vacías
            if not linea:
                continue

            # Verificar si la línea es una declaración de variable
            if linea.startswith(("int", "float", "void")):
                if not linea.endswith(";"):
                    errores.append(f"Error en la línea {num_linea}: falta ';' al final de la declaración.")
                else:
                    # Extraer la variable y su tipo
                    tokens = linea.split()
                    if len(tokens) >= 2:
                        tipo = tokens[0]
                        variable = tokens[1].replace(";", "")
                        variables_declaradas[variable] = tipo  # Guardar el tipo de la variable

            # Verificar asignaciones y si terminan con ';'
            elif "=" in linea:
                if not linea.endswith(";"):
                    errores.append(f"Error en la línea {num_linea}: falta ';' al final de la asignación.")
                
                # Verificar si las variables usadas en la asignación están declaradas
                tokens = linea.replace(";", "").split()
                for token in tokens:
                    if token.isidentifier() and token not in variables_declaradas and token not in variables_reportadas:
                        errores.append(f"Error en la línea {num_linea}: variable '{token}' no está declarada.")
                        variables_reportadas.add(token)  # Evitar repetir el mismo error

                # Verificar tipos en las asignaciones
                variable, valor = linea.replace(";", "").split("=")
                variable = variable.strip()
                valor = valor.strip()

                if variable in variables_declaradas:
                    tipo = variables_declaradas[variable]
                    if tipo == "int" and "." in valor:
                        errores.append(f"Error en la línea {num_linea}: no se puede asignar un valor de punto flotante a una variable de tipo 'int'.")

            # Verificar si las variables están declaradas antes de usarlas
            else:
                tokens = linea.replace(";", "").split()
                for token in tokens:
                    if token.isidentifier() and token not in variables_declaradas and token not in ["if", "else"] and token not in variables_reportadas:
                        errores.append(f"Error en la línea {num_linea}: variable '{token}' no está declarada.")
                        variables_reportadas.add(token)  # Evitar repetir el mismo error

            # Verificar bloques if
            if "if" in linea:
                # Asegurarse de que la línea de 'if' termine con '{' o que la siguiente línea inicie con '{'
                if not linea.strip().endswith("{"):
                    siguiente_linea = texto[num_linea].strip() if num_linea < len(texto) else ""
                    if not siguiente_linea.startswith("{"):
                        errores.append(f"Error en la línea {num_linea}: falta '{{' al final del bloque 'if'.")

        # Mostrar los errores en el QPlainTextEdit_3
        self.plainTextEdit_3.clear()
        if errores:
            for error in errores:
                self.plainTextEdit_3.appendPlainText(error)
        else:
            self.plainTextEdit_3.appendPlainText("Análisis sintáctico completado: no se encontraron errores.")
    
    def iniciar_analisis_semantico(self):
        texto = self.plainTextEdit_2.toPlainText().splitlines()
        errores = []
        variables_declaradas = {}

        # Palabras reservadas y símbolos a ignorar
        palabras_reservadas = {"int", "float", "if", "else", "return"}
        simbolos_ignorar = {"{", "}", "(", ")", "<", ">", "+", "-", "*", "/", "=", ";"}

        for num_linea, linea in enumerate(texto, start=1):
            # Eliminar caracteres de puntuación que podrían interferir con la detección de variables
            tokens = linea.replace(";", "").replace("(", "").replace(")", "").split()

            # Verificar si es una declaración de variable
            if len(tokens) >= 2 and tokens[0] in ["int", "float"]:
                tipo = tokens[0]
                variable = tokens[1].strip().lower()  # Convertimos el nombre de la variable a minúsculas
                variables_declaradas[variable] = tipo

            # Verificar asignación de variable o uso en expresiones
            if "=" in linea:
                partes = linea.split("=")
                variable = partes[0].strip().lower()
                valor = partes[1].strip().replace(";", "")

                # Verificar que la variable esté declarada antes de su uso
                if variable not in variables_declaradas:
                    errores.append(f"Error en la línea {num_linea}: variable '{variable}' no está declarada.")
                else:
                    tipo_variable = variables_declaradas[variable]
                    # Comprobación de tipo (por ejemplo, valor flotante en una variable 'int')
                    if tipo_variable == "int" and any(c in valor for c in ".eE"):
                        errores.append(f"Error en la línea {num_linea}: tipo incompatible, asignación de flotante a 'int'.")

            # Verificar uso de variables no declaradas en expresiones
            for token in tokens:
                  # Convertimos el token a minúsculas
                # Ignorar palabras reservadas, números y operadores comunes
                if (token not in variables_declaradas and 
                    token not in palabras_reservadas and
                    token not in simbolos_ignorar and
                    not token.isdigit()):
                    
                    errores.append(f"Error en la línea {num_linea}: identificador '{token}' no está definido.")
                    # Evitar duplicados, procesar solo una vez cada token en su contexto

        # Mostrar errores en la interfaz
        self.plainTextEdit_4.clear()
        if errores:
            for error in errores:
                self.plainTextEdit_4.appendPlainText(error)
        else:
            self.plainTextEdit_4.appendPlainText("Análisis semántico completado: no se encontraron errores.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
