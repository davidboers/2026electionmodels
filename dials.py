import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arrow, Wedge, Rectangle
import pandas as pd
import numpy as np

def swing_to_angle(swing: float, sidelen: float):
    return -(swing / sidelen * (np.pi / 2)) + (np.pi / 2)

def dial(wedges: np.ndarray, colors: np.ndarray, fulcrum: tuple[float, float] = (0.0, 0.0), 
         r: float = 1.0, ax: plt.Axes | None = None, autolim: bool = True, fu_r: float | None = None,
         fu_color = '#333333', swing: float | None = None):
    # Arg processing
    if ax is None:
        fig, ax = plt.subplots()

    if fu_r is None:
        fu_r = r * 0.05

    sidelen = int(wedges[0])
    wedges = pd.DataFrame(wedges, columns=['Start markers'])
    wedges['End markers'] = wedges['Start markers'].tolist()[1:] + [-sidelen]
    wedges['Color'] = colors
    if sidelen % 5 != 0:
        sidelen = 5 * (sidelen // 5) + 5
    total = sidelen * 2
    wedges['Proportion'] = np.abs(wedges['End markers'] - wedges['Start markers']) / total

    # Colored slices
    upto_part = 0
    for _, wedge in wedges.iterrows():
        theta1 = upto_part * 180
        theta2 = theta1 + (wedge['Proportion'] * 180)
        wd = Wedge(fulcrum, r=r, theta1=theta1, theta2=theta2, color=wedge['Color'])
        ax.add_patch(wd)
        upto_part += wedge['Proportion']

    # Markings
    mark_w = 0.005
    def draw(angle, height, s = None):
        (x, y) = fulcrum
        offset = (mark_w / 2) / (2 * np.pi * r) * (2 * np.pi)
        x1 = x + (np.cos(angle + offset) * r)
        y1 = y + (np.sin(angle + offset) * r)
        mark = Rectangle((x1, y1), width=mark_w, height=height, angle=np.degrees(angle) + 90,
                            color='black')
        ax.add_patch(mark)

        if s is not None:
            x2 = x + (np.cos(angle) * r * 1.1)
            y2 = y + (np.sin(angle) * r * 1.1)
            ax.text(x2, y2, s=s, horizontalalignment='center', verticalalignment='center')

    markh = 0.07
    (step, mark_n) = {
        5: (1, 1),
        10: (1, 2),
        15: (1, 3),
        20: (2, 4),
        25: (2, 4), # icky
        30: (2, 3),
        35: (2, 4),
        40: (4, 8),
    }[sidelen]
    for i in range(step, sidelen + step, step):
        height = markh if i % mark_n == 0 else markh / 2
        ang_p = (i / sidelen * (np.pi / 2))
        angle1 = (np.pi / 2) - ang_p
        angle2 = (np.pi / 2) + ang_p

        draw(angle1, height, i if i % mark_n == 0 else None)
        draw(angle2, height, i if i % mark_n == 0 else None)

    draw(np.pi / 2, markh, '0')

    # Middle and pointer
    mid = Wedge(fulcrum, r=r - markh, theta1=0, theta2=180, color='#f0f0f0')
    ax.add_patch(mid)

    if swing is not None:
        angle = swing_to_angle(swing, sidelen)

        fu = Circle(fulcrum, radius=fu_r, color=fu_color)
        ax.add_patch(fu)

        theta1 = -np.degrees(np.arctan(fu_r)) + np.degrees(angle) + 180
        theta2 = np.degrees(np.arctan(fu_r)) + np.degrees(angle) + 180
        pnt = Wedge((np.cos(angle) * r + fulcrum[0], 
                    np.sin(angle) * r + fulcrum[1]), 
                    r=r, theta1=theta1, theta2=theta2, color=fu_color)
        ax.add_patch(pnt)

    # End
    if autolim:
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect('equal')

def dial_from_swing_required(swing_req: float, swing: float | None = None, ax = None):
    x = swing_req
    if swing is not None:
        x = np.max(np.abs([swing_req, swing])) * np.sign(swing_req)
    b = 5 if np.abs(x) % 5 < 1.5 else 10
    sidelen = (np.abs(x) // b + 1) * b

    if swing_req > 0:
        # Rep on offense
        wedge_widths = [sidelen, swing_req, 0]
        colors = ['crimson', 'cadetblue', 'royalblue']

    else:
        # Dem on offense
        wedge_widths = [sidelen, 0, swing_req]
        colors = ['crimson', 'salmon', 'royalblue']

    dial(np.array(wedge_widths), colors=colors, swing=swing, ax=ax, autolim=False, r=0.5)