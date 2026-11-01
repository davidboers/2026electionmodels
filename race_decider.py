from enum import Enum

import pandas as pd
import numpy as np


def remaining_votes_summary(current_tallies: pd.Series, projected_remaining: pd.Series):
    total_votes = current_tallies.sum()
    margin_v = current_tallies.max() - np.partition(current_tallies, -2)[-2]
    quota = total_votes // 2 + 1
    non_leading_candidates_v = total_votes - current_tallies.max()

    if current_tallies.max() >= quota:
        threshold_field_name = 'Votes required to force runoff'
        threshold_field_value = current_tallies.max() - non_leading_candidates_v

    else:
        threshold_field_name = 'Votes required to avoid runoff'
        threshold_field_value = non_leading_candidates_v - current_tallies.max() + 1 

    # Recount source: O.C.G.A. § 21-2-495(c)
    recount_margin_limit = total_votes // 200 # Maximum vote margin allowing a recount (0.5%)

    if margin_v <= recount_margin_limit and total_votes > 0:
        print(f'Margin between two highest-performing candidates ({margin_v:,}) is within the range to force a recount '
            f'({recount_margin_limit:,}; 0.5% of the total votes).')

    return pd.DataFrame(pd.Series({
        'Votes required to swap places in count': margin_v + 1,
        threshold_field_name: threshold_field_value,
        'Estimated votes remaining': projected_remaining.sum()
    }).astype(int)).style.format('{:,}')
