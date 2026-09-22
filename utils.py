import geopandas


STD_ROUND = 2

def format_votes(x):
    return f'{x:,}'

def format_delta(x):
    if isinstance(x, str):
        return x
    return f'+{x}' if x > 0 else f'{x}'

def make_tuple_matrix(a: list, b: list):
    return [t for row in [[(i, j) for j in b] for i in a] for t in row]


# County GIS maps

def import_county_map():
    counties = geopandas.read_file('./gis/GA-COUNTIES.json')
    def sanitize_name(name: str):
        match name:
            case 'DEKALB': return 'DeKalb'
            case 'MCDUFFIE': return 'McDuffie'
            case 'MCINTOSH': return 'McIntosh'
        return name.title()
    counties['name'] = counties['name'].apply(sanitize_name)
    counties = counties.set_index('name')
    return counties