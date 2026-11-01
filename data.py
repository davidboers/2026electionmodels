import pandas as pd

import sos
import utils
import colors


statewide_races_2022 = [
    'Governor',
    'Lieutenant Governor',
    'Secretary of State',
    'Attorney General',
    'Commissioner of Agriculture',
    'Commissioner of Insurance',
    'State School Superintendent',
    'Commissioner of Labor',
]


def compile(file, races, year, metro_prec_data=pd.DataFrame(columns=['County']), write=False):
    df = pd.read_json(file, typ='series')
    df = sos.prepare_export_df(df, filter_unreported=False)

    counties = df['localResults']['shortName'].tolist()
    index = pd.MultiIndex.from_product([counties, sos.vote_methods], names=['County', 'Vote Method'])
    out_files = {
        race: {
            'County': pd.DataFrame(index=index),
            'Metro': pd.DataFrame()
        } 
        for race in races
    }

    for county in counties:
        ballotItems = df['localResults'].set_index('shortName')['ballotItems'][county]
        for race, out_data in out_files.items():
            if county == 'Baldwin' and race == 'PSC - District 3':
                # Weird bug with Baldwin County's 2025 results
                race = 'PSC - District 3 - Rep'
            try:
                ballotOptions = pd.DataFrame(ballotItems.set_index('name')['ballotOptions'][race])
            except KeyError:
                print(county)
                print(ballotItems.set_index('name')['ballotOptions'])
                raise
            ballotOptions = ballotOptions.set_index('name')
            def gr_df(x):
                groupResults = pd.DataFrame(x)
                groupResults['groupName'] = groupResults['groupName']\
                    .apply(lambda x: x.replace(' Votes', ''))\
                    .apply(lambda x: 'Advance Voting' if 'Advance' in x else x)
                groupResults = groupResults.set_index('groupName')
                return groupResults
            ballotOptions['groupResults'] = ballotOptions['groupResults'].apply(gr_df)
            for method in sos.vote_methods:
                obfuscated = False
                for candidate in ballotOptions.index:
                    candidate1 = candidate.replace('(I)(Rep)', '(I) (Rep)')
                    count = \
                        ballotOptions.loc[candidate, 'groupResults'].loc[method, 'voteCount']
                    if count is None:
                        obfuscated = True
                        count = 0
                    out_data['County'].loc[(county, method), candidate1] = count
                if obfuscated:
                    print(f'{county} County {method} results for {race} appear to be obfuscated')

            # Handle metro-ATL precincts
            if county in metro_prec_data['County'].unique():
                precincts = metro_prec_data[metro_prec_data['County'] == county]
                out_data['Metro'] = ballotOptions['precinctResults']

    if write:
        for race, out_data in out_files.items():
            filename = race.lower().replace(' ', '_')
            filename = f'{year}_{filename}.csv'
            out_data = out_data.map(int)
            out_data.to_csv(f'./data/{filename}')

    return out_files
            

def import_chamber_data(race: str, pres2024: pd.DataFrame):
    curr, candidates = sos.import_current(race, year=2024, by_method=False, all_precincts=True)
    is_substitute = False
    if len(candidates) == 1:
        # Use 2024 results instead
        is_substitute = True
        mask = curr.index
        curr = pres2024.loc[mask]
        candidates = curr.columns
    curr = curr[candidates]
    nonmetro = curr.loc[~curr.index.get_level_values('County').isin(sos.metro_counties)]
    nonmetro = nonmetro.groupby('County').sum()
    nonmetro['Precinct'] = nonmetro.index
    nonmetro = nonmetro.reset_index().set_index(['County', 'Precinct'])
    curr = pd.concat([
        curr.loc[curr.index.get_level_values('County').isin(sos.metro_counties)],
        nonmetro
    ])
    curr = curr.rename(columns={cand: colors.party_name(cand) for cand in candidates})
    curr['Race'] = race
    curr['is_sub'] = is_substitute
    curr = curr.reset_index().set_index(['Race', 'County', 'Precinct'])
    return curr
            

if __name__ == '__main__':
    # Do not delete (need for git repo)
    #compile('export-2025Special.json', ['PSC - District 3'], '2025', True)
    #compile('export-2022NovGen.json', statewide_races_2022, '2022', True)
    #compile('export-2021JanFedRun.json', ['US Senate (Perdue)'], '2021', True)
    #compile('export-2018NovGen.json', ['Public Service Commission, District 5 - Western'], '2018', True)

    # For tuning
    #statewide_races_2018 = [office.replace(' of ', ' Of ') for office in statewide_races_2022]
    #compile('export-2018NovGen.json', statewide_races_2018, '2018', True)


    pres2024, pres2024_candidates = sos.import_current('President of the US', year=2024, by_method=False, all_precincts=True)
    pres2024 = pres2024[pres2024_candidates[:2]]

    state_senate_2024 = []
    for district_number in range(1, 57):
        race = f'State Senate - District {district_number}'
        curr = import_chamber_data(race, pres2024)
        state_senate_2024.append(curr)
    pd.concat(state_senate_2024).fillna(0).astype(int).to_csv('./data/state_senate_2024.csv')

    state_house_2024 = []
    for district_number in range(1, 181):
        race = f'State House of Representatives - District {district_number}'
        curr = import_chamber_data(race, pres2024)
        state_house_2024.append(curr)
    pd.concat(state_house_2024).fillna(0).astype(int).to_csv('./data/state_house_2024.csv')