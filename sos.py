import pandas as pd

import model

vote_methods = ['Election Day', 'Advance Voting', 'Absentee by Mail', 'Provisional']


def prepare_export_df(df: pd.DataFrame, filter_unreported=True, use_advanced=False):
    df['results']['ballotItems'] = pd.DataFrame(df['results']['ballotItems'])
    lr = df['localResults']
    lr = pd.DataFrame(lr)
    lr['shortName'] = lr['name'].apply(lambda x: x.replace(' County', ''))
    lr['Metro?'] = lr['shortName'].apply(lambda x: x in model.metro_counties)
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


    #for_vote_group(df, 'Election Day')
    #for_vote_group(df, 'Absentee by Mail')
    #for_vote_group(df, 'Early in Person')
    #for_vote_group(df, 'Provisional')


def for_vote_group(df: pd.DataFrame, vote_group):
    # Filter counties that are ENC
    lr = df['localResults']
    lr = lr[lr['Metro?'] | (lr[vote_group] == 'Fully Reported') | (lr[vote_group] == 'Election Night Complete')]

    # Split non-Metro counties
    nmc = lr[lr['Metro?'] == False]

    def prepareBallotOptionNMC(bo):
        bo = pd.DataFrame.from_records(bo)
        bo = bo.drop(['precinctResults'], axis=1)
        bo['voteCount'] = [pd.DataFrame.from_records(gr, index='groupName')['voteCount'][vote_group] 
                           for gr in bo['groupResults']]
        bo = bo.drop(['groupResults'], axis=1)
        return bo

    def prepareBallotItemNMC(entry):
        bi = pd.DataFrame.from_records(entry)
        bi = bi.drop(['precinctsParticipating', 'precinctsReporting'], axis=1)
        bi['ballotOptions'] = [prepareBallotOptionNMC(bo)
                               for bo in bi['ballotOptions']]
        return bi

    nmc['ballotItems'] = [prepareBallotItemNMC(entry) for entry in nmc['ballotItems']]

    df['localResults'] = lr
    return df

