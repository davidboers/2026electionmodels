from enum import Enum

import pandas as pd


def project(df: pd.DataFrame, prev_cands, new_cands, swing_map):
    prev_reg_totals = df[prev_cands].sum()
    curr_reg_totals = df[new_cands].sum()

    # Calculate swing
    filtered = df[df['Reported?']]
    if len(filtered) == 0:
        out = pd.DataFrame([0 for _ in new_cands], index=new_cands, columns=['Votes'])
        for from_c, to_c in swing_map.items():
            out.loc[to_c, 'Votes'] = prev_reg_totals[from_c]
        out['Share'] = out['Votes'] / out['Votes'].sum() * 100
        out['Swing'] = 0
        return out
    prev_reg_results_f = pd.DataFrame(filtered[prev_cands].sum(), columns=['Votes'])
    new_reg_results_f = pd.DataFrame(filtered[new_cands].sum(), columns=['Votes'])
    prev_reg_results_f['Share'] = prev_reg_results_f['Votes'] / prev_reg_results_f['Votes'].sum() * 100
    new_reg_results_f['Share'] = new_reg_results_f['Votes'] / new_reg_results_f['Votes'].sum() * 100

    # Project vote share
    def get_prev_results(cand: str):
        try:
            prev_cand = list(prev_cands)[list(new_cands).index(cand)]
            return (prev_reg_results_f['Share'][prev_cand], prev_reg_totals[prev_cand])

        except IndexError:
            # New candidate (without previous benchmark)
            return 0, 0

    reg_proj = pd.DataFrame(new_reg_results_f['Share'].values, index=new_reg_results_f.index, columns=['New Share (Filtered)'])
    reg_proj[['Previous Share (Filtered)', 'Previous Votes']] = [get_prev_results(cand) for cand in reg_proj.index]
    reg_proj['Swing'] = reg_proj['New Share (Filtered)'] - reg_proj['Previous Share (Filtered)']
    reg_proj['Share'] = reg_proj['Previous Votes'] / reg_proj['Previous Votes'].sum() * 100 + reg_proj['Swing']

    # Growth ratio
    prev_vote_total = prev_reg_results_f['Votes'].sum()
    growth_ratio = new_reg_results_f['Votes'].sum() / prev_vote_total if prev_vote_total != 0 else 0
    proj_reg_vote_total = prev_reg_totals.sum() * growth_ratio

    # Project vote
    reg_proj['Votes'] = (reg_proj['Share'] / 100 * proj_reg_vote_total).round()
    reg_proj['Current'] = new_reg_results_f['Votes']
    return reg_proj[['Previous Votes', 'Current', 'Votes']]\
        .rename(columns={'Previous Votes': 'Previous', 'Votes': 'Projection'})\
        .fillna(0)\
        .astype(int)


def is_subset(lhs: list, rhs: list):
    """Also returns true if lhs and rhs are equal"""

    return all([i in rhs for i in lhs])


# Ranges

class Status(Enum):
    AWAITING_MORE_RESULTS = 0,
    CANNOT_MAKE_RUNOFF = 1,
    AVOIDS_RUNOFF = 2,
    CANNOT_WIN_PLURALITY = 3,
    CANNOT_AVOID_RUNOFF = 4,

def ranges(df, prev_cands, new_cands, weak: bool = False, runoff=True):
    
    rf = 'Reported?'
    tf = 'Prev. Total'

    if len(df[df[rf]].index) == 0:
        raise Exception('None reporting')

    if weak:
        # In reporting counties/precincts
        # This method, using "vote growth ratios" is very imprecise and this
        # could be improved by inserting registered voter data in each county
        # when that data is available. We could then use the reporting
        # counties/precincts to estimate voter turnout rates in the unreported
        # counties/precincts. The downside is that using turnout as a baseline
        # makes it impossible to break down the calculation by vote method.
        average_prev_to_now_ratio = df[df[rf]].apply(lambda x: x[new_cands].sum() / x[prev_cands].sum(), axis=1).mean()
        df.loc[df[rf] == False, tf] = df[tf] * average_prev_to_now_ratio

    # Ensure all unreported vote totals are set to zero
    df.loc[df[rf] == False, new_cands] = 0

    out = pd.DataFrame(df[new_cands].sum(), index=new_cands,
                       columns=['Min'])
    votes_in_doubt = df[df[rf] == False][tf].sum()
    out['Max'] = out['Min'] + votes_in_doubt
    out['Status'] = Status.AWAITING_MORE_RESULTS

    out.loc[out['Max'] < out['Min'].max(), 'Status'] = Status.CANNOT_WIN_PLURALITY

    if runoff:
        runoff_threshold = sorted(out['Min'].tolist(), reverse=True)[1]
        out.loc[out['Max'] < runoff_threshold, 'Status'] = Status.CANNOT_MAKE_RUNOFF

        maj_threshold = int((out['Min'].sum() + votes_in_doubt) / 2) + 1
        out.loc[out['Min'] >= maj_threshold, 'Status'] = Status.AVOIDS_RUNOFF
        out.loc[(out['Min'] == out['Min'].max()) &
                (out['Max'] < maj_threshold), 'Status'] = Status.CANNOT_AVOID_RUNOFF

    return out

