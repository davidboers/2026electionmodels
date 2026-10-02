import pandas as pd
import numpy as np

vote_methods = ['Election Day', 'Advance Voting', 'Absentee by Mail', 'Provisional']

def combin_statuses(s1: str, s2: str):
    if s1 == s2:
        return s1

    match (s1, s2):
        case ('Not Reported', 'Election Night Complete' | 'Fully Reported'): 
            return 'Partially Reported'

        case ('Partially Reported', _): 
            return 'Partially Reported'

        case ('Election Night Complete', 'Fully Reported'):
            return 'Election Night Complete'

        case ('Election Night Complete', _):
            return 'Partially Reported'

        case ('Fully Reported', 'Election Night Complete'):
            return 'Election Night Complete'

        case ('Fully Reported', _):
            return 'Partially Reported'

        case _:
            assert False


def prepare_export_df(df: pd.DataFrame, filter_unreported=True, use_advanced=False, ext_rs=False):
    df['results']['ballotItems'] = pd.DataFrame(df['results']['ballotItems'])
    lr = df['localResults']
    lr = pd.DataFrame(lr)
    lr['shortName'] = lr['name'].apply(lambda x: x.replace(' County', ''))
    #lr['Metro?'] = lr['shortName'].apply(lambda x: x in model.metro_counties)
    lr['ballotItems'] = lr['ballotItems'].apply(pd.DataFrame)
    if filter_unreported:
        for vote_group in vote_methods:
            field_name = str(vote_group)
            if use_advanced and vote_group == 'Advance Voting':
                vote_group = 'Advanced Voting'
            lr[field_name] = [pd.DataFrame.from_records(rs, index='groupName')['status'][vote_group] for rs in lr['reportingStatuses']]
        lr = lr.drop('reportingStatuses', axis=1)
    bis = df['results']['ballotItems']
    for vote_method in vote_methods:
        bis[vote_method] = np.repeat('Not Reporting', len(bis))
    if ext_rs:
        for countyname, county in lr.iterrows():
            reporting_statuses = lr[vote_methods]
            ballot_items = county['ballotItems']['name'].values
            
            for ballot_item in ballot_items:
                if ballot_item in bis['name'].values:
                    for vote_method in vote_methods:
                        bis.loc[bis['name'] == ballot_item, vote_method] = combin_statuses(bis.loc[bis['name'] == ballot_item, vote_method], reporting_statuses[vote_method])
    df['localResults'] = lr
    df['results']['ballotItems'] = bis
    return df
