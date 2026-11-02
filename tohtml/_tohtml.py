import json
import markdown



def notebook_to_html(path_from, path_to):
    with open(path_from, 'r') as file:
        notebook = json.load(file)
    cells = [mk_cell(cell) for cell in notebook['cells']]
    with open('./styles/main.css', 'r') as file:
        css = file.readlines()
        css = '\n'.join(['<style>', ''.join(css), '</style>'])
    html = '\n'.join(cells)
    with open(path_to, 'w') as out:
        out.write(css)
        out.write(html)


def mk_cell(cell):
    cell_type = cell['cell_type']

    match cell_type:
        case 'markdown':
            return mk_cell_markdown(cell)

        case 'code':
            return mk_cell_code(cell)

        case _:
            raise Exception(f'Unknown cell type {cell_type}.')


def mk_cell_markdown(cell):
    source = ''.join(cell['source'])
    return markdown.markdown(source)


def mk_cell_code(cell):
    return ''.join([mk_cell_output(output) for output in cell['outputs']])


def mk_cell_output(output):
    if 'data' not in output:
        if 'text' in output:
            ''.join([f'<p>{para}</p>' for para in output['text']])

        else:
            print(output.keys())

        return ''
    
    data = output['data']
    if 'text/html' in data:
        return ''.join(data['text/html'])

    elif 'image/png' in data:
        code = data['image/png']
        return f'<img src="data:image/png;base64,{code}" />'

    elif 'text/plain' in data:
        return ''.join([f'<p>{para.strip('\'')}</p>' for para in data['text/plain']])

    else:
        raise Exception(f'Try one of these: {list(data.keys())}')

