import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import model


def reg_df_m(region_name, df: pd.DataFrame):
    reg_df = df[df['Bloc'] == region_name]
    reg_df = reg_df.drop(columns=['Bloc'])
    return reg_df


if __name__ == '__main__':
    df = pd.read_csv('./2024testdatapres.csv', index_col='County')
    regnames = set(df['Bloc'].tolist())
    regions = {region_name: reg_df_m(region_name, df)
                for region_name in regnames}
    
    graph = pd.DataFrame(columns=['n. counties', 'Coverage', 'Gallagher Index'])
    region = 'South'
    correct = regions[region][model.swing_map.values()].sum()
    correct = pd.DataFrame(correct, columns=['Votes'])
    correct['Share'] = correct['Votes'] / correct['Votes'].sum()
    sample_n = 3
    
    def project_c(reg_df):
        new_p = reg_df[model.swing_map.values()]
        new_data = new_p.sample(sample_n)

        proj = pd.DataFrame(model.project(reg_df[model.swing_map.keys()], new_data, model.swing_map)['Votes'])
        proj['Proj. Share'] = proj['Votes'] / proj['Votes'].sum()
        proj['Act. Share'] = correct['Share']
        proj['Error'] = (proj['Proj. Share'] - correct['Share']).round(4)
        
        total_error = np.sqrt(((proj['Act. Share'] * 100) - (proj['Proj. Share'] * 100)).pow(2).sum() / 2).round(2)
        graph.loc[len(graph)] = [
            # Sampled
            len(new_data.index.tolist()),
            # Coverage
            new_data.sum().sum() / new_p.sum().sum(),
            # Gallagher index
            total_error,
        ]

    for _ in range(10000):
        project_c(regions[region])

    graph.plot.scatter(x='Coverage', y='Gallagher Index', title=f'n. counties = {sample_n}')
    plt.savefig(f'./plots/pres_south.png')
