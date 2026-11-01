import subprocess
import os

import tohtml


def from_template(path_from, path_to, template_subs: dict):
    with open(path_from, 'r') as file:
        content = file.read()

        for placeholder, repl in template_subs.items():
            content = content.replace(placeholder, repl)

        with open(path_to, 'w') as out:
            out.write(content)


def mk_notebook_page(temporary_notebook, final_page, notebook_template, template_subs):
    from_template(notebook_template, temporary_notebook, template_subs)
    r = run_notebook(temporary_notebook) 
    proceed = True 
    if r.returncode != 0:
        print(f'Error for {temporary_notebook}: ', end='')
        print(r.stderr) 
        proceed = False

    else:
        tohtml.notebook_to_html(temporary_notebook, final_page)

    if os.path.exists(temporary_notebook):
        os.remove(temporary_notebook)

    return proceed


statewide_races = [
    # 'US Senate',
    'Governor', 'Lieutenant Governor', 'Secretary of State', 'Attorney General', 'Commissioner of Insurance', 
    'Commissioner of Agriculture', 'Commissioner of Labor', 'State School Superintendent', 
    #'PSC - District 3', 'PSC - District 5',
]


def mk_statewide_pages():
    proceed = True
    notebook_template = './statewide_temp.ipynb'
    for race_name in statewide_races:
        rn_norm = race_name.lower().replace(' ', '_')
        temporary_notebook = f'./tempnb_{rn_norm}.ipynb'
        final_page = f'./html/{rn_norm}.html'
        template_subs = {
            '# Template variables': f'race_name = \'{race_name}\''
        }
        proceed = proceed and mk_notebook_page(temporary_notebook, final_page, notebook_template, template_subs)

    return proceed


def mk_congressional_pages():
    proceed = True
    notebook_template = './congressional.ipynb'
    for dist_num in range(1, 14 + 1):
        temporary_notebook = f'./tempnb_district_{dist_num}.ipynb'
        final_page = f'./html/district_{dist_num}.html'
        template_subs = {
            '# Template district number': f'dist_num = {dist_num}'
        }
        proceed = proceed and mk_notebook_page(temporary_notebook, final_page, notebook_template, template_subs)

    return proceed


def run_notebook(notebook_path) -> subprocess.CompletedProcess:
    return subprocess.run(['jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', notebook_path])


def main():
    for func in [mk_statewide_pages, mk_congressional_pages]:
        if not func():
            print('Stopping.')
            break


if __name__ == '__main__':
    main()