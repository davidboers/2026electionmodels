from enum import Enum

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import utils


metro_counties = ['Gwinnett', 'Fulton']


def project(df: pd.DataFrame, prev_cands, new_cands, swing_map):
    prev_reg_totals = df[prev_cands].sum()

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

    # Project vote
    growth_ratio = new_reg_results_f['Votes'].sum() / prev_reg_results_f['Votes'].sum()
    proj_reg_vote_total = prev_reg_totals.sum() * growth_ratio
    reg_proj['Votes'] = (reg_proj['Share'] / 100 * proj_reg_vote_total).round()
    return reg_proj[['Votes', 'Share', 'Swing']]


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


# Summary

def summarize(df: pd.DataFrame, prev_cands, new_cands, swing_map: dict[str, str], race_stem, runoff=True):
    assert(len(prev_cands) > 1)
    assert(len(new_cands) > 1)

    def big_sum(cand_tally: pd.DataFrame):
        vts = cand_tally['Votes'].tolist()
        maj = vts[0] - vts[1]
        print(f'Majority: {maj:,}')
        shrs = cand_tally['Share'].tolist()
        marg = shrs[0] - shrs[1]
        print(f'Margin: {marg:.2f}')
        return shrs

    def display_res_table(res: pd.DataFrame):
        res = pd.DataFrame(res)
        res['Votes'] = res['Votes'].apply(utils.format_votes)
        res['Share'] = res['Share'].round(utils.STD_ROUND)
        if 'Max' in res:
            res['Max'] = res['Max'].apply(utils.format_votes)
        print(res)

    df['Prev. Total'] = df[prev_cands].sum(axis=1)
    df['Curr. Total'] = df[new_cands].sum(axis=1)
    df['Reported?'] = df['Reporting Status'].apply(lambda x: x in ['Election Night Complete', 'Fully Reported'])
    df = df.drop(['Reporting Status'], axis=1)

    # region Overall results as counted
    print('Previous results:')
    prev_res = df[prev_cands].sum()
    prev_res = pd.DataFrame(prev_res, columns=['Votes'])
    prev_res = prev_res.sort_values(by='Votes', ascending=False)
    prev_res['Share'] = (prev_res['Votes'] / prev_res['Votes'].sum() * 100)
    display_res_table(prev_res)
    shrs = big_sum(prev_res)
    swing_req = 50 - shrs[1] if runoff else (shrs[0] - shrs[1]) / 2
    print(f'Swing required: {swing_req:.2f}')

    print('Current results:')
    curr_res = df[new_cands].sum()
    curr_res = pd.DataFrame(curr_res, columns=['Votes'])
    curr_res = curr_res.sort_values(by='Votes', ascending=False)
    curr_res['Share'] = (curr_res['Votes'] / curr_res['Votes'].sum() * 100)
    r = ranges(df, prev_cands, new_cands, runoff=runoff)
    curr_res['Max'] = r['Max']
    curr_res['Status'] = r['Status']
    display_res_table(curr_res)
    shrs = big_sum(curr_res)
    #endregion

    # region Regional results
    print('Regional Results')
    stwd_proj = pd.Series(0, index=new_cands)
    # This comparison helps demonstrate the reporting bias for a particular candidate.
    # The 'Current' swing uses the full region's previous results as a benchmark for the
    # swing calculation, whereas 'Projection' only calculates the swing amongst fully
    # reported counties (segmented by vote method). 
    grouped = df.groupby('Bloc').sum()
    col = pd.MultiIndex.from_tuples([y for x in [[(c, 'Share'), (c, 'Swing')] for c in new_cands] for y in x])
    ind = pd.MultiIndex.from_tuples([y for x in [[(reg, 'Current'), (reg, 'Projection')] for reg in grouped.index] for y in x], names=('Region', 'Model'))
    regional_table = pd.DataFrame(columns=col, index=ind)
    for cand in prev_cands:
        grouped[cand] = grouped[cand] / grouped['Prev. Total'] * 100
    for cand in new_cands:
        grouped[cand] = grouped[cand] / grouped['Curr. Total'] * 100
        grouped[f'{cand} (Swing)'] = grouped[cand]
    for from_c, to_c in swing_map.items():
        grouped[f'{to_c} (Swing)'] = grouped[to_c] - grouped[from_c]
    for cand in new_cands:
        for region in grouped.index:
            regional_table.loc[(region, 'Current'), (cand, 'Share')] = \
                grouped.loc[region, cand].round(utils.STD_ROUND)
            regional_table.loc[(region, 'Current'), (cand, 'Swing')] = \
                utils.format_delta(grouped.loc[region, f'{cand} (Swing)'].round(utils.STD_ROUND))
    regions = grouped.index
    for region in regions:
        region_df = df[df['Bloc'] == region]
        region_df = region_df.reset_index(level='Vote Method')
        by_vote_method = {method: project(region_df[region_df['Vote Method'] == method], prev_cands, new_cands, swing_map)['Votes']
                          for method in region_df['Vote Method'].unique()}
        p = pd.DataFrame(pd.DataFrame(by_vote_method).T.sum(), columns=['Votes'])
        p['Share'] = p['Votes'] / p['Votes'].sum() * 100
        prev_shares = pd.Series([0.0 for _ in new_cands], index=new_cands)
        for from_c, to_c in swing_map.items():
            prev_shares[to_c] = grouped.loc[region, from_c] 
        p['Swing'] = p['Share'] - prev_shares
        stwd_proj += p['Votes']

        projection = pd.concat([
            p.loc[new_cands, 'Share'].round(utils.STD_ROUND),
            p.loc[new_cands, 'Swing'].round(utils.STD_ROUND).map(utils.format_delta),
        ], axis=1, keys=['Share', 'Swing']).stack()
        projection.index = pd.MultiIndex.from_product(
            [new_cands, ['Share', 'Swing']], names=regional_table.columns.names
        )
        regional_table.loc[(region, 'Projection'), projection.index] = projection
    print(regional_table)
    # endregion

    # region Regional progress
    reg_progress = pd.DataFrame(index=grouped.index, columns=['Reporting'])
    reg_progress['Reporting'] = [len(df[(df['Bloc'] == region) & df['Reported?']]) for region in reg_progress.index]
    reg_progress['Total'] = [len(df[df['Bloc'] == region]) for region in reg_progress.index]
    reg_progress['Votes'] = grouped['Prev. Total']
    reg_progress['Votes (Filtered)'] = [df[(df['Bloc'] == region) & df['Reported?']]['Prev. Total'].sum() 
                                        for region in reg_progress.index]
    reg_progress['Vote Coverage (%)'] = (reg_progress['Votes (Filtered)'] / reg_progress['Votes'] * 100).round(utils.STD_ROUND)
    reg_progress = reg_progress.drop(['Votes', 'Votes (Filtered)'], axis=1)
    print(reg_progress)
    # endregion

    # region Elaborate projection
    stwd_proj = pd.DataFrame(stwd_proj, index=stwd_proj.index, columns=['Votes'])
    stwd_proj['Share'] = stwd_proj['Votes'] / stwd_proj['Votes'].sum() * 100
    # endregion

    # region Swing histograms and maps
    df_shares = pd.DataFrame(df)
    def subtotal_counties(field: pd.Series):
        assert(isinstance(field, pd.Series))
        match field.name:
            case 'Bloc': return field.values[0]
            case 'Reported?': return field.all()
            case _: return field.sum()
    subtotals = df_shares.groupby(level='County').agg(subtotal_counties)
    subtotals.index = pd.MultiIndex.from_tuples(
        [(county, 'All') for county in subtotals.index],
        names=df_shares.index.names,
    )
    df_shares = pd.concat([df_shares, subtotals])
    counties = df.index.get_level_values('County').unique()
    #def mk_swing_df(df_shares: pd.DataFrame):
    df_swings = pd.DataFrame(index=df_shares.index)
    for from_c, to_c in swing_map.items():
        df_shares[from_c] = df_shares[from_c] / df_shares['Prev. Total'] * 100
        df_shares[to_c] = df_shares[to_c] / df_shares['Curr. Total'] * 100
        df_swings[to_c] = df_shares[to_c] - df_shares[from_c]
    #plt.figure()
    #df_swings = mk_swing_df(df_shares)
    df_swings['Reported?'] = df_shares['Reported?']
    swing_columns = list(swing_map.values())[:2]
    df_swings_by_county = df_swings.reset_index(level=1)
    df_swings_by_county = df_swings_by_county[df_swings_by_county['Vote Method'] == 'All']
    df_swings_by_county = df_swings_by_county.drop(['Vote Method'], axis=1)
    max_county_swing = df_swings_by_county[swing_columns].map(np.abs).max().max()
    max_county_swing = int(np.ceil(max_county_swing))
    range = (-max_county_swing, max_county_swing)
    bins = max_county_swing * 2
    fig, axes = plt.subplots(1, len(swing_columns), squeeze=False)
    for column, ax in zip(swing_columns, axes[0]):
        ax.hist(
            [
                df_swings_by_county.loc[
                    ~df_swings_by_county['Reported?'], column
                ].dropna(),
                df_swings_by_county.loc[
                    df_swings_by_county['Reported?'], column
                ].dropna(),
            ],
            bins=bins,
            range=range,
            stacked=True,
            color=['lightblue', 'darkblue'],
            label=['Unreported', 'Reported'],
        )
        ax.set_title(column)
    axes[0][0].legend()
    plt.savefig(f'./plots/county_swing_{race_stem}.png')
    #plt.figure()
    # Must be inverted to align with color scheme
    df_swings['TPS'] = -(df_swings[new_cands[0]] - df_swings[new_cands[1]]) / 2
    counties_geo = utils.import_county_map()
    counties_geo = counties_geo.join(df_swings.reset_index('Vote Method').pivot(columns='Vote Method', values='TPS'))
    ax = counties_geo.plot(column='All', cmap='RdBu', legend=True,
        norm=mcolors.CenteredNorm(), missing_kwds={
            'color': 'lightgray',
            'edgecolor': 'red',
            'hatch': '///',
            'label': 'Missing values'
        })
    counties_geo['Region'] = {county: df['Bloc'][(county, 'Election Day')] for county in counties}
    regions_gis = counties_geo.dissolve(by='Region')
    regions_gis.plot(ax=ax, edgecolor='black', color='none')
    ax.set_title(f'Two-party swing - {race_stem}')
    ax.set_axis_off()
    plt.savefig(f'./plots/county_tps_swing_{race_stem}.png')
    #endregion

    # region Swings
    def guaranteed_swing():
        gwdf = pd.DataFrame(df)
        gwdf = gwdf[gwdf['Reported?']]
        gwdf = gwdf[list(new_cands) + list(prev_cands) + ['Prev. Total', 'Curr. Total']]
        gwdf = gwdf.sum()
        out = pd.Series()
        for from_c, to_c in swing_map.items():
            out[to_c] = ((gwdf[to_c] / gwdf['Curr. Total']) - (gwdf[from_c] / gwdf['Prev. Total'])) * 100
        return out

    print('Swings:')
    print(f'2-Party Swing: {(shrs[0] - shrs[1]) / 2}')
    swings = pd.DataFrame(index=curr_res.index)
    for from_c, to_c in swing_map.items():
        swings.loc[to_c, 'Prev. Cand.'] = from_c
        swings.loc[to_c, 'Prev. Share'] = prev_res.loc[from_c, 'Share']
    # Swing from (complete) previous results and as-counted shares.
    swings['Current'] = curr_res['Share'] - swings['Prev. Share']
    # Projected swings from a statewide swing model.
    #swings['Proj. Statewide'] = project(df, swing_map)['Swing']
    # Current guaranteed swing (unreported counties assumed to not have changed)
    # (This is the same as projected statewide swing unless we segment by vote type)
    swings['In Reporting'] = guaranteed_swing()
    # Statewide swing projected by regional swing model.
    swings['Proj. Regional'] = stwd_proj.loc[:, 'Share'] - swings['Prev. Share']
    #
    swings = swings.drop(['Prev. Cand.', 'Prev. Share'], axis=1)
    swings = swings.round(utils.STD_ROUND).map(utils.format_delta)
    print(swings)
    #endregion

    return stwd_proj


# Entrypoint

if __name__ == '__main__':
    regions = pd.read_csv('regions.csv', index_col='County')

    pres_swing_map = {'Trump 2020': 'Trump 2024', 'Biden 2020': 'Harris 2024', 'Others 2020': 'Others 2024'}

    races = ['Governor', 'Lieutenant Governor', 
             'Secretary of State', 'Attorney General', 'Commissioner of Agriculture',
             'Commissioner of Insurance', 'Commissioner of Labor', 'State School Superintendent'
             ]

    projections = []

    for race_name in races:
        filename = race_name.lower().replace(' ', '_')
        prev_year = 2018
        curr_year = 2022
        prev = pd.read_csv(f'./data/{prev_year}_{filename}.csv', index_col=['County', 'Vote Method'])
        curr = pd.read_csv(f'./data/{curr_year}_{filename}.csv', index_col=['County', 'Vote Method'])
        prev = prev.rename({cand: f'{cand} ({prev_year})' for cand in prev.columns}, axis=1)
        curr = curr.rename({cand: f'{cand} ({curr_year})' for cand in curr.columns}, axis=1)

        def compile_party_map(df: pd.DataFrame):
            def extract_party(name):
                for party in ['rep', 'dem', 'lib']:
                    if f'({party})' in name.lower():
                        return party
                return 'oth'
            return {extract_party(cand): cand for cand in df.columns}

        prev_party_map = compile_party_map(prev)
        curr_party_map = compile_party_map(curr)
        swing_map = {}
        for party in ['rep', 'dem', 'lib']:
            try:
                prev_cand = prev_party_map[party]
                curr_cand = curr_party_map[party]
            except KeyError:
                continue
            swing_map[prev_cand] = curr_cand

        prev_cands = prev.columns
        curr_cands = curr.columns

        s_counties = ['Bacon', 'Burke', 'Tift', 'Troup', 'Towns', 'Murray', 'Oglethorpe', 'Telfair', 'Monroe', 'Rabun', 
                    'Chattooga', 'Glynn', 'Banks', 'McDuffie', 'Chattahoochee', 'Stephens', 'Barrow', 'Sumter', 'Johnson',
                    #'Gwinnett', 'DeKalb', 'Newton', 'Rockdale', 'Forsyth', 'Hall', 'Cobb', 'Clayton', 'Henry', 'Fulton',
                    'Cherokee', 'Fayette', 'Douglas',
                    'Harris', 'Polk', 'Dade', 'Lee', 'Quitman', 'Evans', 'Clinch', 'Greene', 'Twiggs', 'Macon', 'Schley',
                    'Chatham', 'Muscogee', 'Clarke', 'Richmond', 'Coweta', 'Appling'
                    ]
        curr = curr.loc[utils.make_tuple_matrix(s_counties, ['Election Day', 'Advance Voting', 'Absentee by Mail']), :]
        curr['Reporting Status'] = 'Election Night Complete'

        df = prev.join(curr)
        df.loc[:, 'Bloc'] = regions['Region']
        
        print(race_name)
        proj = summarize(df, prev_cands, curr_cands, swing_map, filename)
        projections.append(proj)

    projections: pd.DataFrame = pd.concat(projections)

    #Write only if we have loaded in correct 2022 results
    #projections.to_csv('./tuningdata/correct2022results.csv')

    correct = pd.read_csv('./tuningdata/correct2022results.csv', index_col='Candidate')

    print('Error:')
    projections['Error (Votes)'] = projections['Votes'] - correct['Votes']
    projections['Error (Share)'] = projections['Share'] - correct['Share']
    print(projections)
        
