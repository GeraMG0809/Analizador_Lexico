import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)
        self.setWindowTitle("Analizador Léxico")

        # Conectar el botón "Traducir" con el método iniciar_analisis
        self.pushButton.clicked.connect(self.iniciar_analisis)

        # Configurar el QTableWidget
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Lexema", "Token", "#"])

        # Ajustar las columnas para que se expandan con el tamaño de la tabla
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)

    def iniciar_analisis(self):
        # Obtener el texto del QPlainTextEdit_2 para analizar
        texto = self.plainTextEdit_2.toPlainText()

        # Listas de palabras reservadas, operadores, etc.
        palabras_reservadas = ["int", "float", "void", "if", "while", "return", "else"]
        operadores_suma = ['+', '-']
        operadores_mult = ['*', '/']
        operadores_relacional = ['<', '<=', '>', '>=']
        operadores_or = ['||']
        operadores_and = ['&&']
        operadores_igualdad = ['==', '!=']
        operadores_not = ['!']
        delimitadores = ['(', ')', '{', '}', ';', ',']
        
        resultados = []

        # Recorrer el texto carácter por carácter
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

            elif c in ['<', '>', '=', '!']:
                if i + 1 < len(texto) and texto[i+1] == '=':
                    token = c + texto[i+1]
                    if token in operadores_relacional or token in operadores_igualdad:
                        resultados.append([token, "Operador relacional/igualdad", 7])
                    i += 2
                else:
                    resultados.append([c, "Operador", 2])
                    i += 1
                continue

            elif c == '|':
                if i + 1 < len(texto) and texto[i+1] == '|':
                    resultados.append([c + texto[i+1], "Operador lógico OR", 8])
                    i += 2
                else:
                    resultados.append([c, "Error léxico", 6])
                    i += 1
                continue
            elif c == '&':
                if i + 1 < len(texto) and texto[i+1] == '&':
                    resultados.append([c + texto[i+1], "Operador lógico AND", 9])
                    i += 2
                else:
                    resultados.append([c, "Error léxico", 6])
                    i += 1
                continue

            elif c in delimitadores:
                resultados.append([c, "Delimitador", 12])
                i += 1
                continue

            else:
                resultados.append([c, "Error léxico", 6])
                i += 1

        # Mostrar resultados en el QTableWidget
        self.tableWidget.setRowCount(0)
        for fila in resultados:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            for columna, item in enumerate(fila):
                self.tableWidget.setItem(row_position, columna, QTableWidgetItem(str(item)))

        # Limpieza del QPlainTextEdit después de analizar
        self.plainTextEdit_2.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
