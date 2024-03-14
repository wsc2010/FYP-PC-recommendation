# Mr. Wong Shi Chin
# /genetic_algo.py
# Genetic Algorithm functions and population class
# 16/7/2022
# 20/7/2022

import copy
import random
import numpy as np

from algorithm.component import Build
from algorithm.component import Cpu
from algorithm.component import Gpu
from algorithm.component import Motherboard
from algorithm.component import Psu
from algorithm.component import Memory
from algorithm.component import Storage
from algorithm.component import Cooler
from algorithm.component import Case

from algorithm.component import createRandomBuilds
from algorithm.component import calcBuildFitness

# incompatibility_count = 0

def crossover(parentA, parentB, cpu_socket_chipset, budget):
    child = copy.deepcopy(parentA)
    incompatible = False
    # cpu
    if random.random() < 0.5: # 50% of crossover chance
        child.sel_cpu = parentB.sel_cpu
        if child.sel_mobo.chipset not in cpu_socket_chipset.loc[cpu_socket_chipset['series'] == child.sel_cpu.series]['chipset'].to_list():
            child.sel_mobo = parentB.sel_mobo
            if child.sel_mobo.socket not in child.sel_cooler.socket:
                child.sel_cooler = parentB.sel_cooler
            
    # mobo
    if random.random() < 0.5:
        if parentB.sel_mobo.chipset in cpu_socket_chipset.loc[cpu_socket_chipset['series'] == child.sel_cpu.series]['chipset'].to_list():
            child.sel_mobo = parentB.sel_mobo
            if child.sel_mobo.socket not in child.sel_cooler.socket:
                child.sel_cooler = parentB.sel_cooler
            
    # gpu
    if random.random() < 0.5:
        child.sel_gpu = parentB.sel_gpu
    
    # mem
    if random.random() < 0.5:
        if ((parentB.sel_mem.total_size <= child.sel_mobo.memory_max) &
            (parentB.sel_mem.modules_no <= child.sel_mobo.memory_slots) &
            (parentB.sel_mem.DDR == child.sel_mobo.memory_type)):
            child.sel_mem = parentB.sel_mem
            
    # storage
    if random.random() < 0.5:
        if ((parentB.sel_storage.pcie_gen <= child.sel_mobo.pcie_gen) | (np.isnan(parentB.sel_storage.pcie_gen))):
            child.sel_storage = parentB.sel_storage
            
    # cooler
    if random.random() < 0.5:
        if child.sel_mobo.socket in parentB.sel_cooler.socket:
            child.sel_cooler = parentB.sel_cooler
            
            
    # psu
    if random.random() < 0.5:
        if (child.sel_cpu.tdp + child.sel_gpu.tdp + 300) <= parentB.sel_psu.wattage:
            child.sel_psu = parentB.sel_psu
    
    # case
    if random.random() < 0.5:
        child.sel_case = parentB.sel_case
        if not child.checkCaseCompatability():
            child.sel_case = parentA.sel_case
            
            
    # final checks
    if (child.sel_cpu.tdp + child.sel_gpu.tdp + 300) > child.sel_psu.wattage:
        incompatible = True
    if not child.checkCaseCompatability():
        incompatible = True
    if child.totalCost() > budget:
        incompatible = True
        
    if incompatible:
        # global incompatibility_count
        # incompatibility_count += 1
        # copy parents at 50% chance
        if random.random() < 0.5:
            child = copy.deepcopy(parentA)
        else:
            child = copy.deepcopy(parentB)
    
    return child

def mutation(child, candidates, cpu_socket_chipset, budget, rate):
    cpu_candidates, gpu_candidates, mobo_candidates, mem_candidates, storage_candidates, psu_candidates, cooler_candidates, case_candidates = candidates
    mutated_child = copy.deepcopy(child)
    
    # cpu
    if random.random() < rate:
        cpu_df = cpu_candidates.sample().iloc[0]
        mutated_child.sel_cpu = Cpu(cpu_df['name'], cpu_df['rating'], cpu_df['rating_count'], cpu_df['price_usd'], cpu_df['weighted_rating'],
                  cpu_df['core_count'], cpu_df['core_clock'], cpu_df['boost_clock'], cpu_df['tdp'], cpu_df['integrated_graphics'],
                  cpu_df['smt'], cpu_df['series'], cpu_df['manufacturer'], cpu_df['avg_gaming'], cpu_df['avg_workload'])
        
    # mobo
    cpu_chipsets = cpu_socket_chipset.loc[cpu_socket_chipset['series'] == mutated_child.sel_cpu.series]['chipset'].to_list()
    # if motherboard not compatible or mutation
    if ((mutated_child.sel_mobo.chipset not in cpu_chipsets) | (random.random() < rate)):
        mobo_df = mobo_candidates.loc[mobo_candidates['chipset'].apply(lambda x: x in cpu_chipsets)].sample().iloc[0]
        mutated_child.sel_mobo = Motherboard(mobo_df['name'], mobo_df['rating'], mobo_df['rating_count'], mobo_df['price_usd'], mobo_df['weighted_rating'],
                    mobo_df['socket_/_cpu'], mobo_df['form_factor'], mobo_df['memory_max'], mobo_df['memory_slots'], mobo_df['color'], 
                    mobo_df['chipset'], mobo_df['memory_type'], mobo_df['PCIE_Gen'])

     
    # gpu
    if random.random() < rate:
        gpu_df = gpu_candidates.sample().iloc[0]
        mutated_child.sel_gpu = Gpu(gpu_df['name'], gpu_df['rating'], gpu_df['rating_count'], gpu_df['price_usd'], gpu_df['weighted_rating'],
                  gpu_df['chipset'], gpu_df['memory'], gpu_df['color'],
                  gpu_df['length'], gpu_df['manufacturer'],gpu_df['tdp'], gpu_df['relative_performance'])
    
    # mem
    # if mem not compatible or mutation
    if (((mutated_child.sel_mem.total_size > mutated_child.sel_mobo.memory_max) |
         (mutated_child.sel_mem.modules_no > mutated_child.sel_mobo.memory_slots) |
         (mutated_child.sel_mem.DDR != mutated_child.sel_mobo.memory_type)) |
        (random.random() < rate)):
        mem_df = mem_candidates.loc[(mem_candidates['total_size'] <= mutated_child.sel_mobo.memory_max) &
                                    (mem_candidates['modules_no'] <= mutated_child.sel_mobo.memory_slots) &
                                    (mem_candidates['DDR'] == mutated_child.sel_mobo.memory_type)].sample().iloc[0]
        mutated_child.sel_mem = Memory(mem_df['name'], mem_df['rating'], mem_df['rating_count'], mem_df['price_usd'], mem_df['weighted_rating'],
                     mem_df['speed'], mem_df['modules'], mem_df['DDR'], mem_df['modules_no'], mem_df['cas_latency'],
                     mem_df['total_size'], mem_df['performance'])
   
        
    # storage
    # if storage not compatible or mutation
    if (((mutated_child.sel_storage.pcie_gen > mutated_child.sel_mobo.pcie_gen) &
        (not np.isnan(mutated_child.sel_storage.pcie_gen))) |
        (random.random() < rate)):
        storage_df = storage_candidates.loc[(storage_candidates['PCIE_Gen'] <= mutated_child.sel_mobo.pcie_gen) |
                                            (storage_candidates['PCIE_Gen'].isna())].sample().iloc[0]
        mutated_child.sel_storage = Storage(storage_df['name'], storage_df['rating'], storage_df['rating_count'], storage_df['price_usd'], storage_df['weighted_rating'],
                          storage_df['capacity'], storage_df['type'], storage_df['cache'], storage_df['form_factor'], storage_df['interface'],
                          storage_df['read_speed'], storage_df['write_speed'], storage_df['PCIE_Gen'], storage_df['avg_perf'])
        
        
    # cooler
    # if cooler not compatible or mutation
    if ((mutated_child.sel_mobo.socket not in mutated_child.sel_cooler.socket) |
        (random.random() < rate)):
        cooler_df = cooler_candidates.loc[cooler_candidates['socket'].apply(lambda x: mutated_child.sel_mobo.socket in x)].sample().iloc[0]
        mutated_child.sel_cooler = Cooler(cooler_df['name'], cooler_df['rating'], cooler_df['rating_count'], cooler_df['price_usd'], cooler_df['weighted_rating'],
                        cooler_df['fan_rpm'], cooler_df['noise_level'], cooler_df['color'], cooler_df['radiator_size'], cooler_df['type'],
                        cooler_df['heat_sink_height'], cooler_df['socket'], cooler_df['perf_tier'])

        
    # psu
    # if psu not compatible or mutation
    if ((mutated_child.sel_cpu.tdp + mutated_child.sel_gpu.tdp + 300) > mutated_child.sel_psu.wattage |
        (random.random() < rate)):
        psu_df = psu_candidates.loc[psu_candidates['wattage'] >= (mutated_child.sel_cpu.tdp + mutated_child.sel_gpu.tdp + 300)].sample().iloc[0]
        mutated_child.sel_psu = Psu(psu_df['name'], psu_df['rating'], psu_df['rating_count'], psu_df['price_usd'], psu_df['weighted_rating'],
                  psu_df['form_factor'], psu_df['efficiency_rating'], psu_df['wattage'], psu_df['modular'], psu_df['color'])
        
        
    # case
    if ((not mutated_child.checkCaseCompatability()) | (random.random() < rate)):
        if mutated_child.sel_cooler.cooler_type == 'Water':
            rad = mutated_child.sel_cooler.radiator 
            case_df = case_candidates.loc[(case_candidates['gpu_clearance'] >= mutated_child.sel_gpu.length) &
                        (case_candidates['mobo_support'].apply(lambda x: mutated_child.sel_mobo.form_factor in x)) &
                        (case_candidates['psu_support'].apply(lambda x: mutated_child.sel_psu.form_factor in x)) &
                        ((case_candidates['140rad_support'].apply(lambda x: rad in x)) | (case_candidates['120rad_support'].apply(lambda x: rad in x)))].sample().iloc[0]
        else:
            case_df = case_candidates.loc[(case_candidates['gpu_clearance'] >= mutated_child.sel_gpu.length) &
                        (case_candidates['mobo_support'].apply(lambda x: mutated_child.sel_mobo.form_factor in x)) &
                        (case_candidates['psu_support'].apply(lambda x: mutated_child.sel_psu.form_factor in x)) &
                        (case_candidates['cpu_cooler_clearance'] >= mutated_child.sel_cooler.heat_sink_height)].sample().iloc[0]


        mutated_child.sel_case = Case(case_df['name'], case_df['rating'], case_df['rating_count'], case_df['price_usd'], case_df['weighted_rating'],
                    case_df['type'], case_df['color'], case_df['side_panel_window'], case_df['cpu_cooler_clearance'], case_df['gpu_clearance'],
                    case_df['140rad_support'], case_df['120rad_support'], case_df['mobo_support'], case_df['psu_support'])
        
    
    # if overpriced then no mutation
    if mutated_child.totalCost() > budget:
        mutated_child = copy.deepcopy(child)
    
    return mutated_child

class Population:
    def __init__(self, mutation_rate, pop_size, candidates, cpu_socket_chipset, budget, perc_ranges, use_case):
        self.candidates = candidates
        self.cpu_socket_chipset = cpu_socket_chipset
        self.budget = budget
        self.perc_ranges = perc_ranges
        self.mutation_rate = mutation_rate
        self.pop_size = pop_size
        self.use_case = use_case
        self.population = [createRandomBuilds(self.candidates, self.cpu_socket_chipset, self.budget) for _ in range(self.pop_size)]
    
    def calcFitness(self):
        for i in self.population:
            i.fitness = calcBuildFitness(i, self.perc_ranges, self.use_case)
    
    def calcFitnessSum(self):
        # self.calcFitness()
        fitness_sum = 0
        for i in self.population:
            fitness_sum += i.fitness
        return fitness_sum
    
    def getMaxFitnessBuild(self):
        maxFitnessBuild = self.population[0]
        for i in self.population:
            if i.fitness > maxFitnessBuild.fitness:
                maxFitnessBuild = i
        return maxFitnessBuild

    # Normalize the fitness to 0-1
    def normalize(self):
        fitness_sum = self.calcFitnessSum()
        for i in self.population:
            i.norm = i.fitness / fitness_sum
    
    #Roulette Wheel Selection
    def selectOne(self):
        randomNum = random.random()
        for i in self.population:
            randomNum = randomNum - i.norm
            if randomNum <= 0:
                return i

    # Select parents and create offspring
    def selection(self):
        parentA = copy.deepcopy(self.selectOne())
        parentB = copy.deepcopy(self.selectOne())
        
        if random.random() < (self.mutation_rate / 10): # 10% of mutation rate chance perform full mutation
            child = createRandomBuilds(self.candidates, self.cpu_socket_chipset, self.budget)
        else:
            child = crossover(parentA, parentB, self.cpu_socket_chipset, self.budget)
            child = mutation(child, self.candidates, self.cpu_socket_chipset, self.budget, self.mutation_rate)
                
        return child

    # generate next population
    def generate(self): 
        self.normalize()
        new_population = [self.selection() for _ in range(self.pop_size - 1)]
        new_population.append(copy.deepcopy(self.getMaxFitnessBuild())) # bring over the previous best
        self.population = new_population
