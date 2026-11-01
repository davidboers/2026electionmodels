import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arrow, Wedge, Rectangle
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np

import utils

def swing_to_angle(swing: float, sidelen: float):
    return -(swing / sidelen * (np.pi / 2)) + (np.pi / 2)

def dial(proportions: np.ndarray, colors: np.ndarray, 
         normalize: bool = True,
         fulcrum: tuple[float, float] = (0.0, 0.0), 
         major_ticks = np.arange(-50.0, 50.0, 5.) / 100, # Every fifth
         minor_ticks = np.arange(-50.0, 50.0, 1.) / 100, # Every tick
         primary_tick_formatter: mticker.Formatter = mticker.FuncFormatter(lambda x, _: f'{x:.1f}'),
         secondary_tick_formatter: mticker.Formatter | None = None,
         r: float = 1.0, ax: plt.Axes | None = None, autolim: bool = True, fu_r: float | None = None,
         fu_color = '#333333', point_to: float | None = None):
    # Arg processing
    if ax is None:
        fig, ax = plt.subplots()

    if fu_r is None:
        fu_r = r * 0.05

    if normalize:
        proportions = proportions / proportions.sum()

    rot = np.pi / 2.0

    # Colored slices
    wedges = pd.DataFrame(proportions, columns=['Proportion'])
    wedges['Color'] = colors
    wedges['ProportionCS'] = wedges['Proportion'].cumsum()
    wedges['theta2'] = wedges['ProportionCS'] * 360
    wedges['theta1'] = wedges['theta2'] - (wedges['Proportion'] * 360)
    for _, wedge in wedges.iterrows():
        wd = Wedge(fulcrum, r=r, theta1=wedge['theta1'] + np.degrees(rot), theta2=wedge['theta2'] + np.degrees(rot), color=wedge['Color'])
        ax.add_patch(wd)

    # Ticks
    mark_w = 0.005
    def draw(angle, height):
        (x, y) = fulcrum
        offset = (mark_w / 2) / r
        x1 = x + (np.cos(angle - offset) * r)
        y1 = y + (np.sin(angle - offset) * r)
        mark = Rectangle((x1, y1), width=mark_w, height=height, angle=np.degrees(angle) + 90,
                            color='black')
        ax.add_patch(mark)

    major_tick_height = r * 0.1
    for i in major_ticks:
        angle = i * 2 * np.pi + rot

        draw(angle, major_tick_height)

        outer_r = r * 1.1
        inner_r = r * 0.7

        txt_rot = np.degrees(angle)
        if txt_rot > 90 and txt_rot < 270: # If upside down
            txt_rot = txt_rot + 180

        s2 = primary_tick_formatter(i, angle)
        x2 = fulcrum[0] + (np.cos(angle) * outer_r)
        y2 = fulcrum[1] + (np.sin(angle) * outer_r)
        ax.text(x2, y2, s=s2, horizontalalignment='center', verticalalignment='center', 
                clip_on=True, rotation=txt_rot, fontsize='small')

        if secondary_tick_formatter is not None:
            s3 = secondary_tick_formatter(i, angle)
            x3 = fulcrum[0] + (np.cos(angle) * inner_r)
            y3 = fulcrum[1] + (np.sin(angle) * inner_r)
            ax.text(x3, y3, s=s3, horizontalalignment='center', verticalalignment='center', 
                    clip_on=True, rotation=txt_rot, fontsize='x-small')
        

    minor_tick_height = major_tick_height / 2
    for i in minor_ticks:
        if i in major_ticks:
            continue
        angle = i * 2 * np.pi

        draw(angle, minor_tick_height)

    # Middle and pointer
    mid = Wedge(fulcrum, r=r - major_tick_height * 2, theta1=0, theta2=360, color='#f0f0f0')
    ax.add_patch(mid)

    if point_to is not None:
        angle = point_to * 2 * np.pi + rot

        fu = Circle(fulcrum, radius=fu_r, color=fu_color)
        ax.add_patch(fu)

        theta1 = -np.degrees(np.arctan(fu_r / r)) + np.degrees(angle) + 180
        theta2 = np.degrees(np.arctan(fu_r / r)) + np.degrees(angle) + 180
        pnt = Wedge((np.cos(angle) * r + fulcrum[0], 
                    np.sin(angle) * r + fulcrum[1]), 
                    r=r, theta1=theta1, theta2=theta2, color=fu_color)
        ax.add_patch(pnt)

    # End
    if autolim:
        ax.set_aspect('equal')
        ax.set_xlim(-1.6, 1.6)
        ax.set_ylim(-.1, 1.6)


def dial_from_swing_required(swing_req: float, swing: float | None = None, ax = None, pty: None | str = None, gray_center: bool = False):
    is_rep = swing_req > 0 if pty is None else pty == 'Rep'

    if is_rep:
        # Rep on offense
        wedge_widths = [50.0 - np.abs(swing_req), np.abs(swing_req), 50.0]
        colors = ['gray' if gray_center else 'cadetblue', 'crimson', 'royalblue']

    else:
        # Dem on offense
        wedge_widths = [np.abs(swing_req), 50.0,  50.0 - np.abs(swing_req)]
        colors = ['gray' if gray_center else 'salmon', 'royalblue', 'crimson']

    if pty is None or is_rep:
        swing = -swing

    side_len = 50.0# if np.abs(swing_req) < 25.0 else 100.0 
    major_ticks = np.arange(-side_len, side_len, 5.0) / 100
    minor_ticks = np.arange(-side_len, side_len, 1.0) / 100
    adj_swing = np.round(swing_req / 5) * 5

    def ff_swing(x, _):
        swing_pt = x * 100.0
        points = -swing_pt if pty is None else (pty, swing_pt)
        return utils.point_formatter(points, decimals=False)

    def ff_margin(x, _):
        swing_pt = (x * 100.0 + np.abs(swing_req)) * 2
        points = swing_pt if pty is None else -swing_pt
        return utils.point_formatter(points, decimals=False)

    dial(np.array(wedge_widths), colors=colors, point_to=swing / 100, ax=ax, autolim=True,
         r=1.25,
         major_ticks=major_ticks,
         minor_ticks=minor_ticks,
         primary_tick_formatter=mticker.FuncFormatter(ff_swing),
         secondary_tick_formatter=mticker.FuncFormatter(ff_margin))

    