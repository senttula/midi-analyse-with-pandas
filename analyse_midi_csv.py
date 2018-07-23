import pandas as pd
from pandas.api.types import CategoricalDtype
from Args import args

tracks = pd.read_csv('tracks.csv', header=0)
tracks = tracks.loc[tracks['note count'] > 30]  # filter away tracks with low amount of notes

# instrument information has low amount of unique values
instument_categories = CategoricalDtype(categories=args.instruments, ordered=True)
tracks['instrument'] = tracks['instrument'].astype(instument_categories)
tracks['instrument family'] = tracks['instrument family'].astype('category')

print(tracks.groupby('instrument family').describe().to_string())

complexity = tracks['3 sequences']/tracks['note count']

dataframe_complexity = {
    'instrument': tracks['instrument'],
    'instrument family': tracks['instrument family'],
    'complexity': complexity
}

dataframe_complexity = pd.DataFrame(dataframe_complexity)

print(dataframe_complexity.groupby('instrument').describe().to_string())
