import matplotlib.pyplot as plt 
from matplotlib.patches import Circle
import numpy as np

def hemicircle(seat_counts: np.ndarray | int, colors: np.ndarray, ax: plt.Axes = None, 
               center_p: float = 0.5, arc_range = 180, n_rows: int | None = None):
    
    if isinstance(seat_counts, int):
        total_seats = seat_counts

        if total_seats < 0:
            raise Exception(f'Negative seat count: {seat_counts}')

        if len(colors) != total_seats:
            raise Exception(f'Length of `colors` ({len(colors)}) must match `seat_counts` ({seat_counts}).')

    else:
        total_seats = seat_counts.sum()

        neg_seat_counts = seat_counts[seat_counts < 0]
        if len(neg_seat_counts) > 0:
            neg_seat_counts = [str(n) for n in neg_seat_counts]
            raise Exception(f'Negative seat counts: {', '.join(neg_seat_counts)}')

    if total_seats == 0:
        raise Exception(f'Must be at least one seat!.')

    if center_p < 0:
        raise Exception(f'`center_p` must be positive, not {center_p}.')

    if center_p >= 1:
        raise Exception(f'`center_p` must not be less than 1; {center_p} entered.')

    if arc_range < 0:
        raise Exception(f'`arc_range` must be positive, not {arc_range}.')

    if arc_range > 360:
        raise Exception(f'`arc_range` must not be more than 360; {arc_range} entered.')

    if ax is None:
        fig, ax = plt.subplots()

    outer_r = 1.0
    inner_r = outer_r * center_p

    if n_rows is None:
        n_rows = int(np.sqrt(total_seats)) + 1

    if n_rows > total_seats:
        n_rows = total_seats
    
    r_delta_per_row = (outer_r - inner_r) / n_rows
    seat_r = r_delta_per_row / 3
    def gen_row_area(inner_r_n: float):
        for _ in range(n_rows):
            outer_r_n = inner_r_n + r_delta_per_row
            area = ((np.pi * np.square(outer_r_n)) - (np.pi * np.square(inner_r_n))) * (arc_range / 360)
            yield area
            inner_r_n = outer_r_n
    row_areas = np.array(list(gen_row_area(inner_r)))
    n_per_row = np.zeros(n_rows).astype(int)
    alloc_list = []

    while n_per_row.sum() < total_seats:
        q = row_areas / (n_per_row + 1)
        iup = [i for i in range(n_rows) if q[i] == q.max()][-1]
        alloc_list.append((iup, n_per_row[iup]))
        n_per_row[iup] += 1

    starting_theta = -(arc_range - 180) / 2
    def gen_row_coords(inner_r_n: float):
        for n_seats in n_per_row:
            seat_r_n = inner_r_n + (r_delta_per_row / 2)
            theta_delta = arc_range / (n_seats - 1)
            thetas = np.array([i * theta_delta + starting_theta for i in range(n_seats)])
            xs = np.cos(np.radians(thetas)) * seat_r_n
            ys = np.sin(np.radians(thetas)) * seat_r_n
            yield list(reversed(list(zip(xs, ys))))
            inner_r_n += r_delta_per_row
    coords = list(gen_row_coords(inner_r))
    coords = np.array([coords[row][n] for row, n in alloc_list])

    if isinstance(seat_counts, int):
        for coord, color in zip(coords, colors):
            seat = Circle(coord, radius=seat_r, color=color)
            ax.add_patch(seat)

    else:
        for n_seats, color in zip(seat_counts, colors):
            coords_n = coords[:n_seats]
            coords = coords[n_seats:]

            for x, y in coords_n:
                seat = Circle((x, y), radius=seat_r, color=color)
                ax.add_patch(seat)

    ax.set_xlim(-1, 1)
    ax.set_ylim(-0.5, 1.5)
    ax.set_aspect('equal')

    ax.set_axis_off()