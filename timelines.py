
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

import pandas as pd
import numpy as np

poll_closing = pd.Timestamp('2026-11-03 19:00')

def build_template_timeline(do_other: bool = False):
    parties = ['Dem', 'Rep']
    if do_other:
        parties.append('Oth')
    columns = [[f'{pty} Counted', f'{pty} Projected', f'{pty} Min. 1', f'{pty} Max. 1', f'{pty} Min. 2', f'{pty} Max. 2'] for pty in parties]
    columns = np.concat(columns).tolist() + ['Projected Progress']
    return pd.DataFrame(columns=columns)


def display(timeline: pd.DataFrame, new_entry, ax: plt.Axes, timeline_filename: None | str = None):
    timeline.loc[pd.Timestamp('now')] = new_entry
    
    timeline = timeline.drop_duplicates()

    # Write before filtering for show
    if timeline_filename is not None:
        timeline.to_csv(timeline_filename, index_label='Timestamp')

    timeline.index = pd.to_datetime(timeline.index, errors='coerce')
    timeline = timeline.loc[timeline.index >= poll_closing]

    range1_alpha = 0.15
    range2_alpha = 0.2
    for pty, color in zip(['Rep', 'Dem'], ['crimson', 'royalblue']):
        ax.fill_between(timeline.index, timeline[f'{pty} Min. 1'], timeline[f'{pty} Max. 1'], color=color, alpha=range1_alpha)
        if f'{pty} Min. 2' in timeline.columns:
            ax.fill_between(timeline.index, timeline[f'{pty} Min. 2'], timeline[f'{pty} Max. 2'], color=color, alpha=range2_alpha)
        ax.plot(timeline.index, timeline[f'{pty} Counted'], color=color)
        ax.plot(timeline.index, timeline[f'{pty} Projected'], color=color, linestyle='--')
    ax.plot(timeline.index, timeline['Projected Progress'], 'g--')
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1))

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))

    ax.legend(handles=[
        mlines.Line2D([], [], color='black', label='Counted'),
        mpatches.Patch(color='black', label='Range', alpha=range1_alpha),
        mlines.Line2D([], [], color='black', label='Projected', linestyle='--'),
        #mpatches.Patch(color='black', label='Projection error', alpha=range2_alpha),
        mlines.Line2D([], [], color='green', label='% Counted', linestyle='--'),
    ])


def show_awaiting_results(ax: plt.Axes):
    ax.set_axis_off()
    ax.text(0.5, 0.5, 'Awaiting results', ha='center', fontsize=24, alpha=0.5)
    