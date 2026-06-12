from lexico import analizar_lexico, PLATOS
from collections import OrderedDict

def traducir(instruccion):
    tokens = analizar_lexico(instruccion)

    resultado = OrderedDict([
        ("mesa",     None),
        ("entradas", []),
        ("comidas",  []),
        ("bebidas",  []),
        ("postres",  [])
    ])

    i = 0
    while i < len(tokens):
        tipo, valor = tokens[i]

        if tipo == 'MESA':
            resultado["mesa"] = int(valor[1:])

        elif tipo in ('ENTRADA', 'COMIDA', 'BEBIDA', 'POSTRE'):
            nombre = PLATOS.get(valor, f"Desconocido({valor})")

            # Ver si el siguiente token es CANTIDAD
            cantidad = 1
            if i + 1 < len(tokens) and tokens[i+1][0] == 'CANTIDAD':
                cantidad = int(tokens[i+1][1][1:])  # X3 → 3
                i += 1

            item = {"nombre": nombre, "cantidad": cantidad}

            if tipo == 'ENTRADA':
                resultado["entradas"].append(item)
            elif tipo == 'COMIDA':
                resultado["comidas"].append(item)
            elif tipo == 'BEBIDA':
                resultado["bebidas"].append(item)
            elif tipo == 'POSTRE':
                resultado["postres"].append(item)

        i += 1

    return resultado