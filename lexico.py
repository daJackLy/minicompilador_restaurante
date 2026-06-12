import re

PLATOS = {
    # ENTRADAS
    'E01': 'Ceviche',
    'E02': 'Causa Rellena',
    'E03': 'Tiradito',
    'E04': 'Leche de Tigre',
    'E05': 'Papa a la Huancaina',
    'E06': 'Ocopa Arequipeña',
    'E07': 'Choritos a la Chalaca',
    'E08': 'Solterito de Queso',
    'E09': 'Anticuchos',
    'E10': 'Chicharron de Calamar',

    # COMIDAS
    'C01': 'Lomo Saltado',
    'C02': 'Pollo a la Brasa',
    'C03': 'Aji de Gallina',
    'C04': 'Seco de Res',
    'C05': 'Carapulcra',
    'C06': 'Arroz con Leche',
    'C07': 'Arroz con Pollo',
    'C08': 'Estofado de Pollo',
    'C09': 'Tacu Tacu',
    'C10': 'Chicharron de Cerdo',
    'C11': 'Sudado de Pescado',
    'C12': 'Jalea Mixta',
    'C13': 'Cabrito con Frijoles',
    'C14': 'Pepian de Pollo',
    'C15': 'Tallarines Verdes',
    'C16': 'Tallarines Rojos',
    'C17': 'Cau Cau',
    'C18': 'Sopa a la Criolla',
    'C19': 'Parihuela',
    'C20': 'Chupe de Camarones',

    # BEBIDAS
    'B01': 'Inca Kola',
    'B02': 'Agua',
    'B03': 'Chicha Morada',
    'B04': 'Chicha de Jora',
    'B05': 'Maracuya Sour',
    'B06': 'Pisco Sour',
    'B07': 'Emoliente',
    'B08': 'Refresco de Camu Camu',
    'B09': 'Refresco de Tamarindo',
    'B10': 'Limonada',
    'B11': 'Cerveza',
    'B12': 'Cafe Pasado',

    # POSTRES
    'P01': 'Arroz con Leche',
    'P02': 'Mazamorra Morada',
    'P03': 'Picarones',
    'P04': 'Suspiro Limeño',
    'P05': 'Crema Volteada',
    'P06': 'Turrón de Doña Pepa',
    'P07': 'Helado de Lucuma',
    'P08': 'Ranfañote',
    'P09': 'Cachanga',
    'P10': 'Buñuelos',
}

TOKENS = [
    ('MESA',       r'M\d+'),
    ('ENTRADA',    r'E\d+'),
    ('COMIDA',     r'C\d+'),
    ('BEBIDA',     r'B\d+'),
    ('POSTRE',     r'P\d+'),
    ('CANTIDAD',   r'X\d+'),
    ('SEPARADOR',  r'[:,]'),
    ('DESCONOCIDO',r'\S+'),
]

def analizar_lexico(instruccion):
    tokens_encontrados = []
    texto = instruccion.strip().upper()

    while texto:
        texto = texto.lstrip()
        match = None

        for tipo, patron in TOKENS:
            regex = re.compile(patron)
            match = regex.match(texto)
            if match:
                valor = match.group(0)
                tokens_encontrados.append((tipo, valor))
                texto = texto[len(valor):]
                break

        if not match:
            break

    return tokens_encontrados