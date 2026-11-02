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
    print(f'Running {temporary_notebook}')
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

# TODO: historical data for legislative races with special elections/recounts


def mk_legislative_pages():
    # Template district number
    proceed = True
    notebook_template = './other_temp.ipynb'
    senate_districts = [1, 6, 7, 9, 10, 14, 15, 16, 19, 21, 23, 24, 26, 27, 29, 30, 31, 32,
                        36, 37, 38, 39, 40, 41, 42, 44, 45, 47, 48, 49, 50, 51, 53, 55, 56]
    for dist_num in senate_districts:
        temporary_notebook = f'./tempnb_sd_{dist_num}.ipynb'
        final_page = f'./html/sd_{dist_num}.html'
        template_subs = {
            '# Template district number': f'district_number = {dist_num}',
            '# Template chamber': 'chamber = \'Senate\''
        }
        proceed = proceed and mk_notebook_page(temporary_notebook, final_page, notebook_template, template_subs)
    print(f'{len(senate_districts)} Senate Districts completed')

    house_districts = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                       23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 36, 40, 44, 45, 46, 47, 48, #35, 42   # 39 write-in only
                       49, 50, 51, 53, 54, 57, 58, 59, 64, 65, 67, 70, 71, 73, 79, 80, 81, 82, # 61
                       83, 87, 88, 90, 95, 97, 99, 100, 101, 103, 105, 107, 108, 110, 111, 112, # 85
                       113, 114, 115, 116, 118, 119, 120, 121, 123, 124, 125, 126, 127, 128, 130, 131, #134, 137 write-in only
                       138, 139, 140, 141, 142, 145, 147, 148, 149, 150, 151, 152, 154, 155, 157, 161,
                       164, 166, 167, 168, 173, 174, 175, 176, 178] # 180 write-in only
    for dist_num in house_districts:
        temporary_notebook = f'./tempnb_hd_{dist_num}.ipynb'
        final_page = f'./html/hd_{dist_num}.html'
        template_subs = {
            '# Template district number': f'district_number = {dist_num}',
            '# Template chamber': 'chamber = \'House\''
        }
        proceed = proceed and mk_notebook_page(temporary_notebook, final_page, notebook_template, template_subs)
    print(f'{len(house_districts)} House Districts completed')

    return proceed




def run_notebook(notebook_path) -> subprocess.CompletedProcess:
    args = ['jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', notebook_path]
    try:
        import nbformat
        from nbclient import NotebookClient

        with open(notebook_path, 'r', encoding='utf-8') as file:
            notebook = nbformat.read(file, as_version=4)

        NotebookClient(notebook).execute()

        with open(notebook_path, 'w', encoding='utf-8') as file:
            nbformat.write(notebook, file)

        return subprocess.CompletedProcess(args, 0)
    except Exception as exc:
        return subprocess.CompletedProcess(args, 1, stderr=str(exc))


def main():
    for func in [mk_statewide_pages, mk_congressional_pages, mk_legislative_pages]:
        if not func():
            print('Stopping.')
            break


if __name__ == '__main__':
    main()