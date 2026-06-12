from flask import Flask, request, render_template
from flask import json as flask_json
from sintactico import analizar_sintactico
from traductor import traducir
from lexico import analizar_lexico, PLATOS

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

    return respuesta({
        "ok": True,
        "instruccion": instruccion,
        "tokens": tokens,
        "json": resultado
    })

if __name__ == '__main__':
    app.run(debug=True)