
import pandas as pd


def project(swing: pd.Series, previous_shares: pd.DataFrame, proj_totals: pd.Series, counted_votes_cc: pd.DataFrame):
    """
    swing: swing for each candidate
    previous_shares: previous shares (percent * 100) for each candidate in each cell, but only unreported cells
    proj_totals: projected number of votes in each cell
    counted_votes_cc: Counted votes in reported cells
    """


    if int(swing.sum()) != 0:
        raise Exception('Swing not symetrical!')
    
    previous_shares += swing
    previous_shares = previous_shares.clip(0, 100)

    proj_votes = (previous_shares / 100).mul(proj_totals, axis=0).sum()
    return (proj_votes.add(counted_votes_cc, fill_value=0)
            .astype(int))