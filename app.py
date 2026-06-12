from flask import Flask, request, render_template
from flask import json as flask_json
from sintactico import analizar_sintactico
from traductor import traducir
from lexico import analizar_lexico, PLATOS, TOKENS

app = Flask(__name__)
app.json.sort_keys = False

def construir_menu():
    menu = {
        'entradas': [],
        'comidas':  [],
        'bebidas':  [],
        'postres':  []
    }
    for codigo, nombre in PLATOS.items():
        item = {'codigo': codigo, 'nombre': nombre, 'imagen': f"{codigo.lower()}.jpg"}
        if codigo.startswith('E'):
            menu['entradas'].append(item)
        elif codigo.startswith('C'):
            menu['comidas'].append(item)
        elif codigo.startswith('B'):
            menu['bebidas'].append(item)
        elif codigo.startswith('P'):
            menu['postres'].append(item)
    return menu

def construir_arbol(tokens):
    arbol = {
        "nombre": "COMANDA",
        "hijos": []
    }

    mesa_nodo = None
    items_nodo = {"nombre": "ITEMS", "hijos": []}
    item_actual = None

    for tipo, valor in tokens:
        if tipo == 'MESA':
            mesa_nodo = {"nombre": "MESA", "hijos": [{"nombre": valor, "hijos": []}]}

        elif tipo in ('ENTRADA', 'COMIDA', 'BEBIDA', 'POSTRE'):
            if item_actual:
                items_nodo["hijos"].append(item_actual)
            item_actual = {
                "nombre": "ITEM",
                "hijos": [{"nombre": f"{tipo}\n{valor}", "hijos": []}]
            }

        elif tipo == 'CANTIDAD' and item_actual:
            item_actual["hijos"][0]["nombre"] += f"\n{valor}"
            items_nodo["hijos"].append(item_actual)
            item_actual = None

        elif tipo == 'SEPARADOR' and valor == ',':
            if item_actual:
                items_nodo["hijos"].append(item_actual)
                item_actual = None

    if item_actual:
        items_nodo["hijos"].append(item_actual)

    if mesa_nodo:
        arbol["hijos"].append(mesa_nodo)
    arbol["hijos"].append(items_nodo)

    return arbol

def construir_regex():
    regex_info = []
    for tipo, patron in TOKENS:
        if tipo != 'DESCONOCIDO':
            regex_info.append({"tipo": tipo, "patron": patron})
    return regex_info

def respuesta(data):
    return app.response_class(
        response=flask_json.dumps(data, sort_keys=False, ensure_ascii=False),
        mimetype='application/json'
    )

@app.route('/')
def index():
    return render_template('index.html', menu=construir_menu())

@app.route('/compilar', methods=['POST'])
def compilar():
    datos = request.json
    instruccion = datos.get('instruccion', '').strip().upper()

    valido, mensajes = analizar_sintactico(instruccion)
    if not valido:
        return respuesta({"ok": False, "errores": mensajes})

    resultado = traducir(instruccion)
    tokens = analizar_lexico(instruccion)
    arbol = construir_arbol(tokens)
    regex = construir_regex()

    return respuesta({
        "ok": True,
        "instruccion": instruccion,
        "tokens": tokens,
        "regex": regex,
        "arbol": arbol,
        "json": resultado
    })

if __name__ == '__main__':
    app.run(debug=True)