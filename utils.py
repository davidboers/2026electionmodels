import geopandas


INSTAGRAM_SQUARE_RATIO = (1080, 1080, 'px')      # 1:1
INSTAGRAM_PORTRAIT_RATIO = (1080, 1350, 'px')    # 4:5
INSTAGRAM_LANDSCAPE_RATIO = (1080, 607.5, 'px')  # 16:9
INSTAGRAM_REELS_RATIO = (1080, 1920, 'px')       # 9:16


STD_ROUND = 2


reporting_group_sets = [
    'Reporting Group (2018-2022)',
    'Reporting Group (2018-2026)',
    'Reporting Group (2021-2026)',
    'Reporting Group (2022-2026)',
    'Reporting Group (2025-2026)',
]


def format_votes(x):
    return f'{x:,}'

def format_delta(x):
    if isinstance(x, str):
        return x
    return f'+{x}' if x > 0 else f'{x}'


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