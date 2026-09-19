import pandas as pd

vote_methods = ['Election Day', 'Advance Voting', 'Absentee by Mail', 'Provisional']


def prepare_export_df(df: pd.DataFrame, filter_unreported=True, use_advanced=False):
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
        lr.drop('reportingStatuses', axis=1)
    df['localResults'] = lr
    return df
