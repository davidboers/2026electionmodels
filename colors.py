import numpy as np
import matplotlib.colors as mcolors
from matplotlib import colormaps as mcolormaps


def party_name(candidate_tag: str):
    return candidate_tag[-4:-1]


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
allred = gradient_pick(crimson, 1)
allblue = gradient_pick(royalblue, 1)
barelyred = gradient_pick(crimson, 0)
barelyblue = gradient_pick(royalblue, 0)

xs = [0, 0.25, 0.495, 0.5, 0.515, 0.75, 1]
markers = [allred, crimson, barelyred, (0.8, 0.8, 0.8), barelyblue, royalblue, allblue]

cdict = {
    'red': (
        [(x, color[0], color[0]) for x, color in zip(xs, markers)]
    ),
    'green': (
        [(x, color[1], color[1]) for x, color in zip(xs, markers)]
    ),
    'blue': (
        [(x, color[2], color[2]) for x, color in zip(xs, markers)]
    )
}

party_xs = [0, 0.5, 1]
dem_markers = [barelyblue, royalblue, allblue]
rep_markers = [barelyred, crimson, allred]

demcdict = {
    'red': (
        [(x, color[0], color[0]) for x, color in zip(party_xs, dem_markers)]
    ),
    'green': (
        [(x, color[1], color[1]) for x, color in zip(party_xs, dem_markers)]
    ),
    'blue': (
        [(x, color[2], color[2]) for x, color in zip(party_xs, dem_markers)]
    )
}

repcdict = {
    'red': (
        [(x, color[0], color[0]) for x, color in zip(party_xs, rep_markers)]
    ),
    'green': (
        [(x, color[1], color[1]) for x, color in zip(party_xs, rep_markers)]
    ),
    'blue': (
        [(x, color[2], color[2]) for x, color in zip(party_xs, rep_markers)]
    )
}

#mcolormaps.unregister('Bipartisan')
mcolormaps.register(mcolors.LinearSegmentedColormap('Bipartisan', cdict))
#mcolormaps.unregister('Democrats')
mcolormaps.register(mcolors.LinearSegmentedColormap('Democrats', demcdict))
#mcolormaps.unregister('Republicans')
mcolormaps.register(mcolors.LinearSegmentedColormap('Republicans', repcdict))