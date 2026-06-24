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

def construir_agrupadores(tokens):
    agrupadores_dict = {}

    NOMBRES_TOKEN = {
        'MESA': 'MESA',
        'ENTRADA': 'ENTRADA',
        'COMIDA': 'COMIDA',
        'BEBIDA': 'BEBIDA',
        'POSTRE': 'POSTRE',
        'CANTIDAD': 'CANTIDAD',
        'SEPARADOR': 'SEPARADOR',
    }

    for tipo, valor in tokens:
        if tipo not in NOMBRES_TOKEN:
            continue
        if tipo not in agrupadores_dict:
            agrupadores_dict[tipo] = []
        if valor not in agrupadores_dict[tipo]:
            agrupadores_dict[tipo].append(valor)

    orden = ['MESA', 'ENTRADA', 'COMIDA', 'BEBIDA', 'POSTRE', 'CANTIDAD', 'SEPARADOR']
    agrupadores = []
    for tipo in orden:
        if tipo in agrupadores_dict:
            agrupadores.append({
                "token": tipo,
                "lexemas": ", ".join(agrupadores_dict[tipo])
            })

    return agrupadores

def construir_automata():
    return {
        "estados": ["q0", "q1", "q2", "q3", "q4", "q5(error)"],
        "transiciones": [
            {"desde": "q0", "hacia": "q1", "etiqueta": "MESA"},
            {"desde": "q1", "hacia": "q2", "etiqueta": "SEPARADOR"},
            {"desde": "q2", "hacia": "q3", "etiqueta": "ITEM"},
            {"desde": "q3", "hacia": "q4", "etiqueta": "CANTIDAD"},
            {"desde": "q4", "hacia": "q3", "etiqueta": "ITEM"},
            {"desde": "q0", "hacia": "q5", "etiqueta": "OTRO"},
            {"desde": "q1", "hacia": "q5", "etiqueta": "OTRO"},
            {"desde": "q2", "hacia": "q5", "etiqueta": "OTRO"},
            {"desde": "q3", "hacia": "q5", "etiqueta": "OTRO"},
        ]
    }
    
def construir_tabla_transiciones():
    simbolos = ["MESA", "SEPARADOR", "ITEM", "CANTIDAD"]
    estados = ["q0", "q1", "q2", "q3", "q4", "q5"]

    tabla_valida = {
        ("q0", "MESA"): "q1",
        ("q1", "SEPARADOR"): "q2",
        ("q2", "ITEM"): "q3",
        ("q3", "CANTIDAD"): "q4",
        ("q4", "ITEM"): "q3",
    }

    filas = []
    for estado in estados:
        fila = {"estado": estado}
        for simbolo in simbolos:
            fila[simbolo] = tabla_valida.get((estado, simbolo), "q5")
        filas.append(fila)

    return {"simbolos": simbolos, "filas": filas}

def construir_automatas_por_token():
    #TOKENS
    tokens_letra_digito = {
        'MESA':     'M',
        'ENTRADA':  'E',
        'COMIDA':   'C',
        'BEBIDA':   'B',
        'POSTRE':   'P',
        'CANTIDAD': 'X',
    }

    resultado = {}

    for token, letra in tokens_letra_digito.items():
        resultado[token] = {
            "regex": f"{letra}\\d+",
            "afnd": {
                "descripcion": "Autómata No Determinista (construcción directa desde la regex)",
                "estados": ["q0", "q1", "q2", "qf"],
                "transiciones": [
                    {"desde": "q0", "hacia": "q1", "etiqueta": letra},
                    {"desde": "q1", "hacia": "q2", "etiqueta": "dígito"},
                    {"desde": "q2", "hacia": "q2", "etiqueta": "dígito"},
                    {"desde": "q2", "hacia": "qf", "etiqueta": "ε"},
                ]
            },
            "afd": {
                "descripcion": "Autómata Determinista (equivalente simplificado)",
                "estados": ["q0", "q1", "q2"],
                "transiciones": [
                    {"desde": "q0", "hacia": "q1", "etiqueta": letra},
                    {"desde": "q1", "hacia": "q2", "etiqueta": "0-9"},
                    {"desde": "q2", "hacia": "q2", "etiqueta": "0-9"},
                ],
                "estado_aceptacion": "q2"
            }
        }

    #SEPARADOR
    resultado['SEPARADOR'] = {
        "regex": "[:,]",
        "afnd": {
            "descripcion": "Autómata No Determinista (construcción directa desde la regex)",
            "estados": ["q0", "q1", "qf"],
            "transiciones": [
                {"desde": "q0", "hacia": "q1", "etiqueta": ":"},
                {"desde": "q0", "hacia": "q1", "etiqueta": ","},
                {"desde": "q1", "hacia": "qf", "etiqueta": "ε"},
            ]
        },
        "afd": {
            "descripcion": "Autómata Determinista (equivalente simplificado)",
            "estados": ["q0", "q1"],
            "transiciones": [
                {"desde": "q0", "hacia": "q1", "etiqueta": ": o ,"},
            ],
            "estado_aceptacion": "q1"
        }
    }

    return resultado
    
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
        "agrupadores": construir_agrupadores(tokens),
        "automata": construir_automata(),
        "tabla_transiciones": construir_tabla_transiciones(),
        "arbol": arbol,
        "automatas_tokens": construir_automatas_por_token(),
        "json": resultado
    })

if __name__ == '__main__':
    app.run(debug=True)