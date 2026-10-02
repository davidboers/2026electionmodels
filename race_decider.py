from enum import Enum

import pandas as pd
import numpy as np


def vote_counts(tallies: pd.Series, proj_votes_remaining: int = 0, runoff: bool = True):
    victories = pd.DataFrame([['Possible', ''] for _ in tallies], index=tallies.index, columns=['Status', 'Notes'])
    alternatives = pd.DataFrame(np.repeat(['Possible', ''], 2), index=['Runoff', 'Recount'], columns=['Status', 'Notes'])

    if len(tallies) == 1:
        victories['Status'] = 'Final'
        victories['Notes'] = 'Only one candidate.'
        alternatives['Status'] = 'Impossible'
        alternatives['Notes'] = 'Only one candidate.'

    else:
        votes_counted = tallies.sum()
        projected_total = votes_counted + proj_votes_remaining
        projected_quota = (projected_total // 2) + 1

        if runoff:
            pass


    return victories.merge(alternatives)



def declare(tallies: pd.Series, runoff: bool = True):
    assert len(tallies) > 0

    # Recount source: O.C.G.A. § 21-2-495(c)

    leader = tallies.index[0]
    if len(tallies) == 1:
        return (leader, False)

    else:
        total_votes = tallies.sum()
        quota = (total_votes // 2) + 1
        recount_margin_limit = quota // 200 # Maximum vote margin allowing a recount (0.5%)

        tallies = tallies.sort_values()
        leader_v = tallies.index[0]
        runner_up_v = tallies[1]
        runner_up = tallies.index[1]

        if leader_v == runner_up_v:
            return ('Tie (Runoff)', True)

        if runoff:
            if leader_v >= quota:
                margin = leader_v - runner_up_v
                recount = margin <= recount_margin_limit
                return (leader, recount)

            else:
                if len(tallies) >= 3:
                    c3_v = tallies[2]
                    recount = runner_up_v - c3_v <= recount_margin_limit
                else:
                    recount = False
                return ('Runoff', recount)

        
