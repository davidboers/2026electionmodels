import geopandas
import numpy as np
import pandas as pd


INSTAGRAM_SQUARE_RATIO = (960, 960, 'px')        # 1:1
INSTAGRAM_PORTRAIT_RATIO = (960, 1200, 'px')     # 4:5
INSTAGRAM_LANDSCAPE_RATIO = (960, 540, 'px')     # 16:9
INSTAGRAM_REELS_RATIO = (540, 960, 'px')         # 9:16


STD_ROUND = 2


reporting_group_sets = [
    'Reporting Group (2018-2022)',
    'Reporting Group (2018-2026)',
    'Reporting Group (2021-2026)',
    'Reporting Group (2022-2026)',
    'Reporting Group (2025-2026)',
]


def mk_timestamp():
    return pd.Timestamp('now', tz='US/Eastern')


def mk_formatted_timestamp():
    return mk_timestamp().strftime('As of %A, %d %B %Y at %I:%M %p Eastern Time').replace(' 0', ' ')

def sort_and_share(res):
    res = res.sort_values(by='Votes', ascending=False)
    res['Votes'] = res['Votes'].astype(int)
    if res['Votes'].sum() == 0:
        res['Share'] = 0
    else:
        res['Share'] = (res['Votes'] / res['Votes'].sum() * 100)
    return res

def format_votes(x):
    return f'{x:,}'

def format_delta(x):
    if isinstance(x, str):
        return x
    return f'+{x}' if x > 0 else f'{x}'



def point_formatter(p, decimals: bool = True):
    """ 
    >>> point_formatter(3)          # R+3
    >>> point_formatter(-3)         # D+3
    >>> point_formatter(('D', -1))  # D-1
    >>> point_formatter(('R', 10))  # R+10
    >>> point_formatter(('I', 1))   # I+1
    >>> point_formatter(0)          # =0
    >>> point_formatter(('D', 0))   # D+0
    """
    
    if isinstance(p, tuple):
        (party, points) = p
        party = party[:1].upper()
        p = points

    else:
        if p == 0:
            return '=0'

        # Assume negative is Dem and positive is Rep
        party = 'D' if p < 0 else 'R'
        p = np.abs(p)

    if decimals:
        return f'{party}{p:+.1f}'

    else:
        return f'{party}{int(p):+}'

def points_format(p, field: str):
    if isinstance(p, tuple):
        (party, points) = p
        party = party[:1].upper()

    else:
        party = 'D' if p < 0 else 'R'
        points = np.abs(p)

    if points <= 0:
        color = 'gray'

    elif party == 'D':
        color = 'royalblue'

    elif party == 'R':
        color = 'crimson'

    else:
        color = 'gray'

    return f'{field}: {color}; '

def points_format_block(p):
    return points_format(p, 'background-color')

def points_format_font(p):
    return points_format(p, 'color')



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