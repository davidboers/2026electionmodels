import numpy as np
import matplotlib.colors as mcolors
from matplotlib import colormaps as mcolormaps


def party_name(candidate_tag: str):
    for tag in ['Rep', 'Dem', 'Wrt', 'Lib', 'Grn']:
        if f'({tag})'.lower() in candidate_tag.lower():
            return tag
    return 'Ind'


strong_party_colors = {
    'Rep': 'crimson',
    'Dem': 'royalblue',
    'Lib': 'orange',
    'Runoff': 'gray'
}

light_party_colors = {
    'Rep': 'salmon',
    'Dem': 'cadetblue',
    'Lib': 'orange',
    'Runoff': 'lightgray'
}


def color_for_cand(color_map: dict, cand):
    party = party_name(cand)
    try:
        return color_map[party]

    except KeyError:
        return 'gray'


def mk_listed_colormap(candidates, color_scheme, convert_to_party = True):
    return mcolors.ListedColormap([
        color_for_cand(color_scheme, cand) if convert_to_party else cand
        for cand in candidates
        ]
    )


# Gradients


def gradient_pick(color: np.ndarray, ratio):
    color = color * 255.0

    ratio = 1 - ratio

    # Only use 70% of the spectrum to prevent fully white or black
    ratio = 0.7 * (ratio - 0.5) + 0.5

    if ratio >= 0.5:
        rev_color = 255 - color
        color = 2 * (ratio - 0.5) * rev_color + color

    else: 
        color = 2 * ratio * color

    color = color / 255

    [r, g, b] = color
    return (r, g, b)


crimson = np.array([0.863, 0.078, 0.235])
royalblue = np.array([0.255, 0.412, 0.882])


nullcolor = '#fff5f5'

democrats = mcolors.LinearSegmentedColormap.from_list('Democrats', [nullcolor, 'royalblue'])
republicans = mcolors.LinearSegmentedColormap.from_list('Republicans', [nullcolor, 'crimson'])
others = mcolors.LinearSegmentedColormap.from_list('Others', [nullcolor, 'gold'])


referendum = mcolors.LinearSegmentedColormap.from_list('referendum', ['crimson', 'green'])