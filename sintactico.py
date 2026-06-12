from lexico import analizar_lexico

def analizar_sintactico(instruccion):
    tokens = analizar_lexico(instruccion)
    tipos = [tipo for tipo, valor in tokens]
    errores = []

    if not tipos or tipos[0] != 'MESA':
        return False, ["ERROR: La instrucción debe empezar con el código de mesa (M1-M20)."]

    if len(tipos) < 2 or tipos[1] != 'SEPARADOR':
        return False, ["ERROR: Falta el separador ':' después de la mesa."]

    if len(tipos) < 3:
        return False, ["ERROR: La mesa no tiene ningún ítem pedido."]

    ITEMS_VALIDOS = {'ENTRADA', 'COMIDA', 'BEBIDA', 'POSTRE'}

    i = 2
    while i < len(tipos):
        if tipos[i] not in ITEMS_VALIDOS:
            errores.append(f"ERROR: Se esperaba un ítem válido, se encontró '{tipos[i]}'.")
            i += 1
            continue

        i += 1

        if i < len(tipos) and tipos[i] == 'CANTIDAD':
            i += 1

        if i < len(tipos):
            if tipos[i] == 'SEPARADOR':
                i += 1  # saltar la coma
            elif tipos[i] in ITEMS_VALIDOS:
                errores.append(f"ERROR: Falta ',' entre ítems.")
            else:
                errores.append(f"ERROR: Token inesperado '{tipos[i]}'.")
                i += 1

    if errores:
        return False, errores

    return True, ["OK: Estructura sintáctica correcta."]