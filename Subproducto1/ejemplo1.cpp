#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// Definir una estructura para representar los tokens
struct Token {
    char nombre[20];
    char valor[20];
};

// Función para verificar si un carácter es un operador
int esOperador(char c) {
    return (c == '+' || c == '-' || c == '*' || c == '/');
}

// Función para analizar el código fuente
int analizarCodigoFuente(const char* codigo, struct Token resultados[], int maxResultados) {
    int i, j;
    int codigoLen = strlen(codigo);
    int numResultados = 0;

    for (i = 0; i < codigoLen; i++) {
        // Ignorar espacios en blanco
        if (isspace(codigo[i])) {
            continue;
        }

        // Verificar si es un dígito
        if (isdigit(codigo[i])) {
            for (j = i + 1; j < codigoLen; j++) {
                if (!isdigit(codigo[j])) {
                    break;
                }
            }
            int len = j - i;
            strncpy(resultados[numResultados].nombre, "ENTERO", sizeof(resultados[numResultados].nombre) - 1);
            strncpy(resultados[numResultados].valor, codigo + i, len);
            resultados[numResultados].nombre[sizeof(resultados[numResultados].nombre) - 1] = '\0';
            resultados[numResultados].valor[len] = '\0';
            numResultados++;
            i = j - 1; // Avanzar el índice
        }

        // Verificar si es un operador
        else if (esOperador(codigo[i])) {
            strncpy(resultados[numResultados].nombre, "OPERADOR", sizeof(resultados[numResultados].nombre) - 1);
            resultados[numResultados].nombre[sizeof(resultados[numResultados].nombre) - 1] = '\0';
            resultados[numResultados].valor[0] = codigo[i];
            resultados[numResultados].valor[1] = '\0';
            numResultados++;
        }

        // Error: Carácter no válido
        else {
            printf("Error: Carácter no válido en el código fuente.\n");
            break;
        }
    }
    return numResultados;
}

// Función auxiliar para imprimir los tokens
void imprimirTokens(struct Token tokens[], int numTokens) {
    int i;
    for (i = 0; i < numTokens; i++) {
        printf("Token: %s, Valor: %s\n", tokens[i].nombre, tokens[i].valor);
    }
}

// Código de ejemplo
int main() {
    const char* codigoFuente = "3 + 4 * 2 - 1 / 5";
    int maxTokens = 100;
    struct Token resultados[maxTokens];

    int numTokens = analizarCodigoFuente(codigoFuente, resultados, maxTokens);
    if (numTokens >= 0) {
        imprimirTokens(resultados, numTokens);
    }

   
}



