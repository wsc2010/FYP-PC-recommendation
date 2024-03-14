# Mr. Wong Shi Chin
# /pc_recommendation.py
# Main function for running the genetic algorithm
# 16/7/2022
# 20/7/2022

import pandas as pd
import numpy as np
import random
import copy
import os
from pathlib import Path
from ast import literal_eval

from algorithm.utils import weighted_rating
from algorithm.utils import budget_range
from algorithm.utils import get_candidates
from algorithm.utils import recalc_perf
from algorithm.utils import spread_value
from algorithm.utils import update_build_naming

from algorithm.genetic_algo import Population
from algorithm.component import createRandomBuilds

def generate_recommendation(budget = 1500, use_case = 'general', pop_size = 1000, generations = 50, mutation_rate = 0.01, top3 = False, get_random = False):

    if budget < 1200:
        return False


    # gaming - emphasize cpu on gaming, add multiplier to gpu
    # general - default, avg cpu perf
    # machine learning - default to nvidia gpu + multiplier, multiplier to mem
    # content creation (rendering, modeling, photo video editing) - default to nvidia, CPU work perf, mem multiplier

    script_dir = Path(__file__).parent


    cpu = pd.read_csv((script_dir / 'data/cpu_perf_recalc.csv').resolve())
    gpu = pd.read_csv((script_dir /  'data/gpu.csv').resolve())
    mem = pd.read_csv((script_dir /  'data/mem.csv').resolve())
    mobo = pd.read_csv((script_dir /  'data/mobo.csv').resolve())
    psu = pd.read_csv((script_dir /  'data/psu.csv').resolve())
    storage = pd.read_csv((script_dir /  'data/storage.csv').resolve())
    case = pd.read_csv((script_dir /  'data/case.csv').resolve(), converters={"140rad_support": literal_eval, "120rad_support": literal_eval, 
                                                                                "mobo_support": literal_eval, "psu_support": literal_eval})
    cooler = pd.read_csv((script_dir /  'data/cooler.csv').resolve(), converters={"socket": literal_eval})


    cpu_socket_chipset = pd.read_csv((script_dir / 'data/cpu_chipset_socket.csv').resolve())
    gpu_perf = pd.read_csv((script_dir / 'data/gpu_perf_recalc.csv').resolve())


    build_budget_allocation = pd.read_csv((script_dir / 'data/build_budget_allocation.csv').resolve())


    cpu['1080p_rel_perf'] = recalc_perf(cpu['1080p_rel_perf'])
    cpu['1440p_rel_perf'] = recalc_perf(cpu['1440p_rel_perf'])
    cpu['single_thread_rel_perf'] = recalc_perf(cpu['single_thread_rel_perf'])
    cpu['multi_thread_rel_perf'] = recalc_perf(cpu['multi_thread_rel_perf'])

    cpu['avg_gaming'] = (cpu['1080p_rel_perf'] + cpu['1440p_rel_perf']) / 2
    cpu['avg_workload'] = (cpu['single_thread_rel_perf'] + cpu['multi_thread_rel_perf']) / 2

    gpu_perf['relative_performance'] = recalc_perf(gpu_perf['relative_performance'])

    gpu = gpu.join(gpu_perf.set_index('chipset'), on='chipset')
    if (use_case == 'machine learning') | (use_case == 'content creation'): # Nvidia gpu only
        gpu = gpu.loc[gpu['manufacturer'] != 'AMD']


    mem['total_size'] = mem['modules'] * mem['modules_no']
    mem['performance'] = mem['speed'] / mem['cas_latency']

    storage = storage.loc[storage['read_speed'].notna()]
    storage['avg_perf'] = (storage['read_speed'] + storage['write_speed']) / 2

    build_budget_allocation['total'] = (build_budget_allocation['cpu'] + build_budget_allocation['gpu'] + 
                                        build_budget_allocation['mobo'] + build_budget_allocation['mem'] + build_budget_allocation['psu'] + 
                                        build_budget_allocation['storage'] + build_budget_allocation['cooler'] + build_budget_allocation['case'])

    build_budget_allocation['cpu_perc'] = build_budget_allocation['cpu'] / build_budget_allocation['total']
    build_budget_allocation['gpu_perc'] = build_budget_allocation['gpu'] / build_budget_allocation['total']
    build_budget_allocation['mobo_perc'] = build_budget_allocation['mobo'] / build_budget_allocation['total']
    build_budget_allocation['mem_perc'] = build_budget_allocation['mem'] / build_budget_allocation['total']
    build_budget_allocation['psu_perc'] = build_budget_allocation['psu'] / build_budget_allocation['total']
    build_budget_allocation['storage_perc'] = build_budget_allocation['storage'] / build_budget_allocation['total']
    build_budget_allocation['cooler_perc'] = build_budget_allocation['cooler'] / build_budget_allocation['total']
    build_budget_allocation['case_perc'] = build_budget_allocation['case'] / build_budget_allocation['total']

    cpu_perc_ranges = budget_range(build_budget_allocation['cpu_perc'])
    gpu_perc_ranges = budget_range(build_budget_allocation['gpu_perc'])
    mobo_perc_ranges = budget_range(build_budget_allocation['mobo_perc'])
    mem_perc_ranges = budget_range(build_budget_allocation['mem_perc'])
    psu_perc_ranges = budget_range(build_budget_allocation['psu_perc'])
    storage_perc_ranges = budget_range(build_budget_allocation['storage_perc'])
    cooler_perc_ranges = budget_range(build_budget_allocation['cooler_perc'])
    case_perc_ranges = budget_range(build_budget_allocation['case_perc'])

    cpu_candidates = get_candidates(weighted_rating(cpu), cpu_perc_ranges, budget, True)
    gpu_candidates = get_candidates(weighted_rating(gpu), gpu_perc_ranges, budget, True)
    mobo_candidates = get_candidates(weighted_rating(mobo), mobo_perc_ranges, budget, True)
    mem_candidates = get_candidates(weighted_rating(mem), mem_perc_ranges, budget, True)
    psu_candidates = get_candidates(weighted_rating(psu), psu_perc_ranges, budget, True)
    storage_candidates = get_candidates(weighted_rating(storage), storage_perc_ranges, budget, True)
    cooler_candidates = get_candidates(weighted_rating(cooler), cooler_perc_ranges, budget, True)
    case_candidates = get_candidates(weighted_rating(case), case_perc_ranges, budget, True)

    # check if candidates are empty or less than 10 items
    for i in [cpu_candidates, gpu_candidates, mobo_candidates, mem_candidates, psu_candidates, storage_candidates, cooler_candidates, case_candidates]:
        if len(i) < 10:
            return False

    candidates = cpu_candidates, gpu_candidates, mobo_candidates, mem_candidates, storage_candidates, psu_candidates, cooler_candidates, case_candidates
    perc_ranges = cpu_perc_ranges, gpu_perc_ranges, mobo_perc_ranges, mem_perc_ranges, storage_perc_ranges, psu_perc_ranges, cooler_perc_ranges, case_perc_ranges


    if get_random:
        return createRandomBuilds(candidates, cpu_socket_chipset, random.randint(1500, 10000))

    # Initilize population
    pop = Population(mutation_rate, pop_size, candidates, cpu_socket_chipset, budget, perc_ranges, use_case) 
    # old_pop = copy.deepcopy(pop)

    # Evolve
    for i in range(generations):
        pop.calcFitness()
        print(pop.getMaxFitnessBuild().fitness)
        pop.generate()


    pop.calcFitness()
    # calcBuildFitness(pop.getMaxFitnessBuild(), True)
    if top3:
        first = pop.getMaxFitnessBuild()
        pop.population.remove(first)
        second = pop.getMaxFitnessBuild()
        pop.population.remove(second)
        third = pop.getMaxFitnessBuild()

        sel_builds = first, second, third
        return sel_builds


    return pop.getMaxFitnessBuild()

# best_build = generate_recommendation(pop_size=100, generations=20)
# bdict = build_to_dict(best_build)
# print(bdict)