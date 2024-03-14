# Mr. Wong Shi Chin
# /utils.py
# utility functions
# 16/7/2022
# 20/7/2022

import random

#v is the number of votes for the movie;
#m is the minimum votes required to be listed in the chart;
#R is the average rating of the movie;
#C is the mean vote across the whole report.
def calc_weighted(row, m, C):
    v = row['rating_count']
    R = row['rating']
    # Calculation based on the IMDB formula
    return (v/(v+m) * R) + (m/(m+v) * C)


def weighted_rating(df):
    C = df['rating'].mean()
    m = df['rating_count'].quantile(0.25) # items with votes more than 20% of the items in list
    
    df2 = df.copy().loc[df['rating_count'] >= m]
    df2['weighted_rating'] = df2.apply(calc_weighted, axis=1, args=(m, C))
    return df2


def budget_range(col):
    Q1 = col.quantile(0.25)
    Q3 = col.quantile(0.75)
    median = col.quantile(0.5)
    upper_limit = Q3 + 1.5*(Q3-Q1)
    lower_limit = Q1 - 1.5*(Q3-Q1)
    budget_range = {
        "Q1" : Q1,
        "Q3" : Q3,
        "median" : median,
        "upper_limit" : upper_limit,
        "lower_limit" : lower_limit
    }
    return budget_range

# Filter out items based on price
def get_candidates(df, budget_range, budget, no_lower=False):
    headroom = 0 # in percent e.g. 0.1
    budget2 = budget * (1-headroom)
    if no_lower:
        # Remove items that cost too much
        candidates_df = df.copy().loc[(df['price_usd'] < (budget_range['upper_limit'] * budget2))]
    else:
        # Remove items that cost too much and too less
        candidates_df = df.copy().loc[(df['price_usd'] > (budget_range['lower_limit'] * budget2)) & (df['price_usd'] < (budget_range['upper_limit'] * budget2))]
    return candidates_df

# Rescale relative performance based on highest in column
def recalc_perf(column):
    reference = column.max()
    new_perf = column.apply(lambda x: round((x/reference)*100, 2))
    return new_perf

# Not used
# Randomly spreads the rating to simulate average ratings with decimal
def spread_value(rating):
    if rating == 0:
        rating += random.randrange(0, 4, 1) / 10
    elif rating == 5:
        rating += random.randrange(-5, 0, 1) / 10
    else:
        rating += random.randrange(-5, 4, 1) / 10
    return rating

# Format build component names for displaying
def update_build_naming(build):
    gpu_name = f"{build.sel_gpu.name} {build.sel_gpu.chipset} {build.sel_gpu.chipset} {build.sel_gpu.memory}"
    build.sel_gpu.full_name = gpu_name

    mem_name = f"{build.sel_mem.name} {build.sel_mem.modules_no}x{build.sel_mem.module_size}GB {build.sel_mem.DDR}-{build.sel_mem.speed}"
    build.sel_mem.full_name = mem_name

    storage_prefix = 'TB' if build.sel_storage.capacity >= 1000 else 'GB'
    storage_size = (build.sel_storage.capacity/1000) if build.sel_storage.capacity >= 1000 else build.sel_storage.capacity
    storage_name = f"{build.sel_storage.name} {storage_size} {storage_prefix} {build.sel_storage.storage_type}"
    build.sel_storage.full_name = storage_name

    psu_name = f"{build.sel_psu.name} {build.sel_psu.wattage}W"
    build.sel_psu.full_name = psu_name
