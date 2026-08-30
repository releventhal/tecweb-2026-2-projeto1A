from utils import load_template, build_response
from database import Database, Note
from urllib.parse import unquote_plus
from html import escape

db = Database('banco')

def index(request):

    # A string de request sempre começa com o tipo da requisição (ex: GET, POST)
    if request.startswith('POST'):
        request = request.replace('\r', '')  # Remove caracteres indesejados
        # Cabeçalho e corpo estão sempre separados por duas quebras de linha
        partes = request.split('\n\n')
        corpo = partes[1]
        params = {}
        # Preencha o dicionário params com as informações do corpo da requisição
        # O dicionário conterá dois valores, o título e a descrição.
        # Posteriormente pode ser interessante criar uma função que recebe a
        # requisição e devolve os parâmetros para desacoplar esta lógica.
        # Dica: use o método split da string e a função unquote_plus
        for chave_valor in corpo.split('&'):
            chave, valor = chave_valor.split('=')
            params[chave] = unquote_plus(valor)

        note = Note(
            title=params['titulo'],
            content=params['detalhes']
        )

        db.add(note)

        return build_response(
        code=303,
        reason='See Other',
        headers='Location: /'
        )



    # Cria uma lista de <li>'s para cada anotação
    # Se tiver curiosidade: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    note_template = load_template('components/note.html')
    notes_li = [
        note_template.format(
            id=note.id,
            title=note.title,
            details=note.content
        )
    for note in db.get_all()
    ]
    notes = '\n'.join(notes_li)

    body = load_template('index.html').format(notes=notes)
    return build_response(
        body=body,
        headers='Content-Type: text/html; charset=utf-8'
    )

def delete_note(request, note_id):
    note = db.get(note_id)

    if note is None:
        return build_response(
            body='Anotação não encontrada',
            code=404,
            reason='Not Found',
            headers='Content-Type: text/plain; charset=utf-8'
        )

    if request.startswith('POST'):
        db.delete(note_id)

        return build_response(
            code=303,
            reason='See Other',
            headers='Location: /'
        )

    body = load_template('delete.html').format(
        id=note.id,
        title=escape(note.title or '', quote=True)
    )

    return build_response(
        body=body,
        headers='Content-Type: text/html; charset=utf-8'
    )

def edit(request, note_id):
    note = db.get(note_id)

    if note is None:
        return build_response(
            body='Anotação não encontrada',
            code=404,
            reason='Not Found',
            headers='Content-Type: text/plain; charset=utf-8'
        )

    if request.startswith('POST'):
        request = request.replace('\r', '')
        partes = request.split('\n\n')
        corpo = partes[1]

        params = {}

        for chave_valor in corpo.split('&'):
            chave, valor = chave_valor.split('=', 1)
            params[chave] = unquote_plus(valor)

        updated_note = Note(
            id=note.id,
            title=params['titulo'],
            content=params['detalhes']
        )

        db.update(updated_note)

        return build_response(
            code=303,
            reason='See Other',
            headers='Location: /'
        )

    body = load_template('edit.html').format(
        id=note.id,
        title=escape(note.title or '', quote=True),
        details=escape(note.content or '')
    )

    return build_response(
        body=body,
        headers='Content-Type: text/html; charset=utf-8'
    )