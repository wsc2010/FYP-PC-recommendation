# Mr. Wong Shi Chin
# /component.py
# Component Classes
# 16/7/2022
# 20/7/2022

class Build:
    def __init__(self, sel_cpu, sel_gpu, sel_mobo, sel_psu, sel_mem, sel_storage, sel_cooler, sel_case):
        self.sel_cpu = sel_cpu
        self.sel_gpu = sel_gpu
        self.sel_mobo = sel_mobo
        self.sel_psu = sel_psu
        self.sel_mem = sel_mem
        self.sel_storage = sel_storage
        self.sel_cooler = sel_cooler
        self.sel_case = sel_case
        
    def totalCost(self):
        totalCost = round(self.sel_cpu.price_usd + self.sel_gpu.price_usd + self.sel_mobo.price_usd + 
                          self.sel_psu.price_usd + self.sel_mem.price_usd + self.sel_storage.price_usd + 
                          self.sel_cooler.price_usd + self.sel_case.price_usd, 2)
        return totalCost
    
    def checkCaseCompatability(self):
        compatible = True
        if self.sel_gpu.length > self.sel_case.gpu_clearance:
            compatible = False
        if self.sel_mobo.form_factor not in self.sel_case.mobo_supp:
            compatible = False
        if self.sel_psu.form_factor not in self.sel_case.psu_supp:
            compatible = False
            
        if self.sel_cooler.cooler_type == "Water":
            if not ((self.sel_cooler.radiator in self.sel_case.rad_supp140) | (self.sel_cooler.radiator in self.sel_case.rad_supp120)):
                compatible = False
        else:
            if self.sel_cooler.heat_sink_height > self.sel_case.cooler_clearance:
                compatible = False
            
        return compatible


class Component:
    def __init__(self, name, rating, rating_count, price_usd, weighted_rating):
        self.name = name
        self.rating = rating
        self.rating_count = rating_count
        self.price_usd = price_usd
        self.weighted_rating = weighted_rating


class Cpu(Component):
    def __init__(self, name, rating, rating_count, price_usd, weighted_rating, 
                 core_count, core_clock, boost_clock, tdp, int_graphics, smt, series, manufacturer, avg_gaming, avg_workload):
        super().__init__(name, rating, rating_count, price_usd, weighted_rating)
        self.core_count = core_count
        self.core_clock = core_clock
        self.boost_clock = boost_clock
        self.tdp = tdp
        self.int_graphics = int_graphics
        self.smt = smt
        self.series = series
        self.manufacturer = manufacturer
        self.avg_gaming = avg_gaming
        self.avg_workload = avg_workload

class Gpu(Component):
    def __init__(self, name, rating, rating_count, price_usd, weighted_rating,
                 chipset, memory, color, length, manufacturer, tdp, rel_perf):
        super().__init__(name, rating, rating_count, price_usd, weighted_rating)
        self.chipset = chipset
        self.memory = memory
        self.color = color
        self.length = length
        self.manufacturer = manufacturer
        self.tdp = tdp
        self.rel_perf = rel_perf
    
class Motherboard(Component):
    def __init__(self, name, rating, rating_count, price_usd, weighted_rating,
                 socket, form_factor, memory_max, memory_slots, color, chipset, memory_type, pcie_gen):
        super().__init__(name, rating, rating_count, price_usd, weighted_rating)
        self.socket = socket
        self.form_factor = form_factor
        self.memory_max = memory_max
        self.memory_slots = memory_slots
        self.color = color
        self.chipset = chipset
        self.memory_type = memory_type
        self.pcie_gen = pcie_gen

class Psu(Component):
    def __init__(self, name, rating, rating_count, price_usd, weighted_rating,
                 form_factor, efficiency_rating, wattage, modular, color):
        super().__init__(name, rating, rating_count, price_usd, weighted_rating)
        self.form_factor = form_factor
        self.efficiency_rating = efficiency_rating
        self.wattage = wattage
        self.modular = modular
        self.color = color

class Memory(Component):
    def __init__(self, name, rating, rating_count, price_usd, weighted_rating,
                 speed, module_size, DDR, modules_no, cas_latency, total_size, perf):
        super().__init__(name, rating, rating_count, price_usd, weighted_rating)
        self.speed = speed
        self.module_size = module_size
        self.DDR = DDR
        self.modules_no = modules_no
        self.cas_latency = cas_latency
        self.total_size = total_size
        self.perf = perf

class Storage(Component):
    def __init__(self, name, rating, rating_count, price_usd, weighted_rating,
                 capacity, storage_type, cache, form_factor, interface, read_speed, write_speed, pcie_gen, avg_perf):
        super().__init__(name, rating, rating_count, price_usd, weighted_rating)
        self.capacity = capacity
        self.storage_type = storage_type
        self.cache = cache
        self.form_factor = form_factor
        self.interface = interface
        self.read_speed = read_speed
        self.write_speed = write_speed
        self.pcie_gen = pcie_gen
        self.avg_perf = avg_perf

class Cooler(Component):
    def __init__(self, name, rating, rating_count, price_usd, weighted_rating,
                 fan_rpm, noise_level, color, radiator, cooler_type, heat_sink_height, socket, perf_tier):
        super().__init__(name, rating, rating_count, price_usd, weighted_rating)
        self.fan_rpm = fan_rpm
        self.noise_level = noise_level
        self.color = color
        self.radiator = radiator
        self.cooler_type = cooler_type
        self.heat_sink_height = heat_sink_height
        self.socket = socket
        self.perf_tier = perf_tier
        
class Case(Component):
    def __init__(self, name, rating, rating_count, price_usd, weighted_rating,
                 case_type, color, side_panel, cooler_clearance, gpu_clearance, rad_supp140, rad_supp120, mobo_supp, psu_supp):
        super().__init__(name, rating, rating_count, price_usd, weighted_rating)
        self.case_type = case_type
        self.color = color
        self.side_panel = side_panel
        self.cooler_clearance = cooler_clearance
        self.gpu_clearance = gpu_clearance
        self.rad_supp140 = rad_supp140
        self.rad_supp120 = rad_supp120
        self.mobo_supp = mobo_supp
        self.psu_supp = psu_supp

def createRandomBuilds(candidates, cpu_socket_chipset, budget):
    cpu_candidates, gpu_candidates, mobo_candidates, mem_candidates, storage_candidates, psu_candidates, cooler_candidates, case_candidates = candidates
    overpriced = True
    
    while overpriced:
        cpu_df = cpu_candidates.sample().iloc[0]
        cpu = Cpu(cpu_df['name'], cpu_df['rating'], cpu_df['rating_count'], cpu_df['price_usd'], cpu_df['weighted_rating'],
                  cpu_df['core_count'], cpu_df['core_clock'], cpu_df['boost_clock'], cpu_df['tdp'], cpu_df['integrated_graphics'],
                  cpu_df['smt'], cpu_df['series'], cpu_df['manufacturer'], cpu_df['avg_gaming'], cpu_df['avg_workload'])

        gpu_df = gpu_candidates.sample().iloc[0]
        gpu = Gpu(gpu_df['name'], gpu_df['rating'], gpu_df['rating_count'], gpu_df['price_usd'], gpu_df['weighted_rating'],
                  gpu_df['chipset'], gpu_df['memory'], gpu_df['color'],
                  gpu_df['length'], gpu_df['manufacturer'],gpu_df['tdp'], gpu_df['relative_performance'])


        cpu_chipsets = cpu_socket_chipset.loc[cpu_socket_chipset['series'] == cpu.series]['chipset'].to_list()

        mobo_df = mobo_candidates.loc[mobo_candidates['chipset'].apply(lambda x: x in cpu_chipsets)]
        if len(mobo_df) < 1:
            continue
        mobo_df = mobo_df.sample().iloc[0]
        mobo = Motherboard(mobo_df['name'], mobo_df['rating'], mobo_df['rating_count'], mobo_df['price_usd'], mobo_df['weighted_rating'],
                    mobo_df['socket_/_cpu'], mobo_df['form_factor'], mobo_df['memory_max'], mobo_df['memory_slots'], mobo_df['color'], 
                    mobo_df['chipset'], mobo_df['memory_type'], mobo_df['PCIE_Gen'])


        mem_df = mem_candidates.loc[(mem_candidates['total_size'] <= mobo.memory_max) &
                                    (mem_candidates['modules_no'] <= mobo.memory_slots) &
                                    (mem_candidates['DDR'] == mobo.memory_type)]
        if len(mem_df) < 1:
            continue
        mem_df = mem_df.sample().iloc[0]
        mem = Memory(mem_df['name'], mem_df['rating'], mem_df['rating_count'], mem_df['price_usd'], mem_df['weighted_rating'],
                     mem_df['speed'], mem_df['modules'], mem_df['DDR'], mem_df['modules_no'], mem_df['cas_latency'],
                     mem_df['total_size'], mem_df['performance'])


        storage_df = storage_candidates.loc[(storage_candidates['PCIE_Gen'] <= mobo.pcie_gen) |
                                            (storage_candidates['PCIE_Gen'].isna())]
        if len(storage_df) < 1:
            continue
        storage_df = storage_df.sample().iloc[0]
        storage = Storage(storage_df['name'], storage_df['rating'], storage_df['rating_count'], storage_df['price_usd'], storage_df['weighted_rating'],
                          storage_df['capacity'], storage_df['type'], storage_df['cache'], storage_df['form_factor'], storage_df['interface'],
                          storage_df['read_speed'], storage_df['write_speed'], storage_df['PCIE_Gen'], storage_df['avg_perf'])


        required_power = cpu.tdp + gpu.tdp + 300 # 300W headroom for power

        psu_df = psu_candidates.loc[psu_candidates['wattage'] >= required_power]
        if len(psu_df) < 1:
            continue
        psu_df = psu_df.sample().iloc[0]
        psu = Psu(psu_df['name'], psu_df['rating'], psu_df['rating_count'], psu_df['price_usd'], psu_df['weighted_rating'],
                  psu_df['form_factor'], psu_df['efficiency_rating'], psu_df['wattage'], psu_df['modular'], psu_df['color'])


        cooler_df = cooler_candidates.loc[cooler_candidates['socket'].apply(lambda x: mobo.socket in x)]
        if len(cooler_df) < 1:
            continue
        cooler_df = cooler_df.sample().iloc[0]
        cooler = Cooler(cooler_df['name'], cooler_df['rating'], cooler_df['rating_count'], cooler_df['price_usd'], cooler_df['weighted_rating'],
                        cooler_df['fan_rpm'], cooler_df['noise_level'], cooler_df['color'], cooler_df['radiator_size'], cooler_df['type'],
                        cooler_df['heat_sink_height'], cooler_df['socket'], cooler_df['perf_tier'])


        if cooler.cooler_type == 'Water':
            rad = cooler.radiator 
            case_df = case_candidates.loc[(case_candidates['gpu_clearance'] >= gpu.length) &
                        (case_candidates['mobo_support'].apply(lambda x: mobo.form_factor in x)) &
                        (case_candidates['psu_support'].apply(lambda x: psu.form_factor in x)) &
                        ((case_candidates['140rad_support'].apply(lambda x: rad in x)) | (case_candidates['120rad_support'].apply(lambda x: rad in x)))]
        else:
            case_df = case_candidates.loc[(case_candidates['gpu_clearance'] >= gpu.length) &
                        (case_candidates['mobo_support'].apply(lambda x: mobo.form_factor in x)) &
                        (case_candidates['psu_support'].apply(lambda x: psu.form_factor in x)) &
                        (case_candidates['cpu_cooler_clearance'] >= cooler.heat_sink_height)]
            
        if len(case_df) < 1:
            continue
        case_df = case_df.sample().iloc[0]

        case = Case(case_df['name'], case_df['rating'], case_df['rating_count'], case_df['price_usd'], case_df['weighted_rating'],
                    case_df['type'], case_df['color'], case_df['side_panel_window'], case_df['cpu_cooler_clearance'], case_df['gpu_clearance'],
                    case_df['140rad_support'], case_df['120rad_support'], case_df['mobo_support'], case_df['psu_support'])

        build = Build(cpu, gpu, mobo, psu, mem, storage, cooler, case)
        overpriced = False if build.totalCost() <= budget else True
    
    return build


def calcBuildFitness(build, perc_ranges, use_case, print_indiv_scores = False):
    cpu_perc_ranges, gpu_perc_ranges, mobo_perc_ranges, mem_perc_ranges, storage_perc_ranges, psu_perc_ranges, cooler_perc_ranges, case_perc_ranges = perc_ranges
    totalCost = build.totalCost()
    mem_multiplier = 1
    gpu_multiplier = 1

    if use_case == 'gaming':
        cpu_score = (cpu_perc_ranges['median'] * (1 - abs(build.sel_cpu.price_usd / totalCost - cpu_perc_ranges['median'])) *
                        build.sel_cpu.weighted_rating * build.sel_cpu.avg_gaming)
    elif use_case == 'general':
        cpu_score = (cpu_perc_ranges['median'] * (1 - abs(build.sel_cpu.price_usd / totalCost - cpu_perc_ranges['median'])) *
                        build.sel_cpu.weighted_rating * (build.sel_cpu.avg_gaming + build.sel_cpu.avg_workload)/2)
    else: # machine learning and content creation
        mem_multiplier = 1.5
        cpu_score = (cpu_perc_ranges['median'] * (1 - abs(build.sel_cpu.price_usd / totalCost - cpu_perc_ranges['median'])) *
                        build.sel_cpu.weighted_rating * build.sel_cpu.avg_workload)

    if use_case == 'machine learning':
        gpu_multiplier = 1.15
    gpu_score = (gpu_perc_ranges['median'] * (1 - abs(build.sel_gpu.price_usd / totalCost - gpu_perc_ranges['median'])) *
                 build.sel_gpu.weighted_rating * build.sel_gpu.rel_perf) * gpu_multiplier
    
    mobo_score = (mobo_perc_ranges['median'] * (1 - abs(build.sel_mobo.price_usd / totalCost - mobo_perc_ranges['median'])) *
                  build.sel_mobo.weighted_rating * 10)
    
    mem_score = (mem_perc_ranges['median'] * (1 - abs(build.sel_mem.price_usd / totalCost - mem_perc_ranges['median'])) *
                 build.sel_mem.weighted_rating * (build.sel_mem.perf/200) + (build.sel_mem.total_size / 4)) * mem_multiplier
    
    storage_score = (storage_perc_ranges['median'] * (1 - abs(build.sel_storage.price_usd / totalCost - storage_perc_ranges['median'])) *
                     build.sel_storage.weighted_rating * (build.sel_storage.capacity / 1000) * (build.sel_storage.avg_perf / 1000))
    
    psu_score = (psu_perc_ranges['median'] * (1 - abs(build.sel_psu.price_usd / totalCost - psu_perc_ranges['median'])) *
                 build.sel_psu.weighted_rating * 10)
    
    cooler_score = (cooler_perc_ranges['median'] * (1 - abs(build.sel_cooler.price_usd / totalCost - cooler_perc_ranges['median'])) *
                    build.sel_cooler.weighted_rating * (build.sel_cpu.tdp / build.sel_cooler.perf_tier / 2))
    
    case_score = (case_perc_ranges['median'] * (1 - abs(build.sel_case.price_usd / totalCost - case_perc_ranges['median'])) *
                  build.sel_case.weighted_rating * 10)
                  
    if print_indiv_scores:
        print("cpu %4.5f" % (cpu_score))
        print("gpu %4.5f" % (gpu_score))
        print("mobo %4.5f" % (mobo_score))
        print("mem %4.5f" % (mem_score))
        print("storage %4.5f" % (storage_score))
        print("psu %4.5f" % (psu_score))
        print("cooler %4.5f" % (cooler_score))
        print("case %4.5f" % (case_score))
    
    fitness_val = cpu_score + gpu_score + mobo_score + storage_score + psu_score + cooler_score + case_score
    return fitness_val