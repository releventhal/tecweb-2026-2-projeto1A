from utils import load_template, build_response
from database import Database, Note
from urllib.parse import unquote_plus
from html import escape

db = Database('banco')

def index(request):
    error = ''
    form_title = ''
    form_details = ''

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
            chave, valor = chave_valor.split('=', 1)
            params[chave] = unquote_plus(valor)

        form_title = params.get('titulo', '').strip()
        form_details = params.get('detalhes', '').strip()

        if not form_title or not form_details:
            error = '''
            <div class="form-error">
            Preencha o título e o conteúdo da anotação.
            </div>
            '''
        else:
            note = Note(
                title=form_title,
                content=form_details
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
            title=escape(note.title or ''),
            details=escape(note.content or ''),
            favorite_class='favorite-active' if note.favorite else '',
            favorite_icon='&#9733;' if note.favorite else '&#9734;',
            favorite_label='Remover dos favoritos'
            if note.favorite
            else 'Adicionar aos favoritos'
        )
        for note in db.get_all()
    ]
    notes = '\n'.join(notes_li)

    body = load_template('index.html').format(
        notes=notes,
        error=error,
        form_title=escape(form_title, quote=True),
        form_details=escape(form_details)
    )

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
        return not_found()

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

def not_found():
    body = load_template('404.html')

    return build_response(
        body=body,
        code=404,
        reason='Not Found',
        headers='Content-Type: text/html; charset=utf-8'
    )

def favorite_note(note_id):
    note = db.get(note_id)

    if note is None:
        return not_found()

    db.toggle_favorite(note_id)

    return build_response(
        code=303,
        reason='See Other',
        headers='Location: /'
    )