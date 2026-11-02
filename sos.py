import pandas as pd
import numpy as np

vote_methods = ['Election Day', 'Advance Voting', 'Absentee by Mail', 'Provisional']

def combin_statuses2(s1: str, s2: str):
    if s1 == s2:
        return s1

    if not s1:
        return s2

    if not s2:
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


def combin_statuses(statuses: list[str]):
    s1 = statuses[0]

    for si in statuses[1:]:
        s1 = combin_statuses2(si, s1)

    return s1


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
                        bis.loc[bis['name'] == ballot_item, vote_method] = combin_statuses2(bis.loc[bis['name'] == ballot_item, vote_method], reporting_statuses[vote_method])
    df['localResults'] = lr
    df['results']['ballotItems'] = bis
    return df


metro_counties = ['Fulton', 'Gwinnett', 'DeKalb', 'Cobb', 'Douglas', 'Fayette', 'Henry', 'Clayton', 'Rockdale', 'Newton', 'Cherokee', 'Forsyth', 'Hall']


def import_current(race_name: str, year = 2026, by_method: bool = False, all_precincts: bool = False):
    match year:
        case 2026:
            df = pd.read_json('./export-11032026GeneralAndSpecialElection.json', typ='series')
        case 2024:
            df = pd.read_json('./export-2024NovGen.json', typ='series')
        case 2022:
            df = pd.read_json('./export-2022NovGen.json', typ='series')
        case _:
            raise Exception('Year must be 2022, 2024, or 2026.')

    summ_results = pd.DataFrame.from_records(df['results']['ballotItems'], index='name')
    id_list = summ_results['id']
    race_id = id_list.rename(lambda n: n.split('/')[0])[race_name]

    lr = pd.DataFrame.from_records(df['localResults'], index='name')
    bis = lr['ballotItems'].map(pd.DataFrame.from_records)
    bis = bis[bis.map(lambda bis: race_id in bis['id'].values)]
    bis = bis.apply(lambda bis: bis.loc[bis[bis['id'] == race_id].first_valid_index()])
    bis = pd.DataFrame(bis['ballotOptions'], index=bis.index)

    ballotOptionsLists = bis['ballotOptions'].apply(lambda bos: pd.DataFrame.from_records(bos, index='name'))

    name_normalizer = lambda s: s.replace('(I)(Rep)', '(I) (Rep)').replace('(I)(Dem)', '(I) (Dem)')


    def transpose_row(county_name, bos: pd.Series):
        bos = ballotOptionsLists.loc[county_name]
        county_name_norm = county_name.replace(' County', '')
        if all_precincts or county_name_norm in metro_counties:
            precinct_lists = {cand: pd.DataFrame.from_records(bos['precinctResults'].loc[cand], index='name') for cand in bos.index}
            
            # TODO: reported?
            if by_method:
                votes = pd.DataFrame({cand: l['groupResults'] for cand, l in precinct_lists.items()})
                vote_counts = votes.map(lambda gr: pd.DataFrame.from_records(gr, index='groupName')['voteCount'])
                return np.concat([[{'County': county_name_norm, 'Precinct': precinct, 'Vote Method': method, 'Reported?': False} 
                                | {name_normalizer(cand): gr[cand][method] for cand in gr.index}
                                for method in vote_methods] 
                                for precinct, gr in vote_counts.iterrows()]).tolist()

            else:
                votes = pd.DataFrame({cand: l['voteCount'] for cand, l in precinct_lists.items()})
                votes['Reported?'] = list(precinct_lists.values())[0]['reportingStatus'].isin(['Election Night Complete', 'Fully Reported'])
                votes['County'] = county_name_norm
                return [{'Precinct': precinct} | entry.rename(name_normalizer).to_dict() for precinct, entry in votes.iterrows()]

        else:
            vote_counts = bos['groupResults'].apply(lambda gr: pd.DataFrame.from_records(gr, index='groupName')['voteCount'])
            if by_method:
                return [{'County': county_name_norm, 'Precinct': county_name_norm, 'Vote Method': method, 'Reported?': False} 
                        | vote_counts[method].rename(name_normalizer).to_dict() 
                        for method in vote_counts.columns]

            else:
                return [{'County': county_name_norm, 'Precinct': county_name_norm, 'Reported?': False} 
                        | vote_counts[vote_counts.columns].rename(name_normalizer).T.sum().to_dict()]
                


    votes = pd.DataFrame(np.concat([transpose_row(i, bos) for i, bos in ballotOptionsLists.items()]).tolist())
    index_cols = ['County', 'Precinct']
    if by_method:
        index_cols.append('Vote Method')
    votes = votes.set_index(index_cols)
    candidates = votes.columns.drop(['Reported?'])
    votes[candidates] = votes[candidates].fillna(0).astype(int)
    return votes, candidates