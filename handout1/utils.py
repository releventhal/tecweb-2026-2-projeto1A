import json
from pathlib import Path

def extract_route(request):
    primeira_linha = request.split('\n')[0]
    rota = primeira_linha.split(' ')[1]
    return rota[1:]

def read_file(path):
    with open(path, "rb") as file:
        return file.read()

def load_data(filename):
    path = Path("data") / filename

    with open(path, "r") as file:
        return json.load(file)

def load_template(filename):
    path = Path("templates") / filename

    with open(path, "r", encoding="UTF-8") as file:
        return file.read()


def add_note(note):
    notes = load_data('notes.json')
    notes.append(note)

    path = Path('data') / 'notes.json'

    with open(path, 'w') as file:
        json.dump(notes, file)

def build_response(body='', code=200, reason='OK', headers=''):
    response = f'HTTP/1.1 {code} {reason}\r\n'

    if headers:
        response += headers + '\r\n'

    response += '\r\n'
    response += body

    return response.encode('utf-8')