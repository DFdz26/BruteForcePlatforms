import math
import time
import matplotlib.pyplot as plt
import tools_BF
import numpy
import random

NOVELTY_HISTORY_FOLDER = "noveltyHistory"
NOVELTY_HISTORY_FILE = "noveltyHistory.pickle"


class NoveltySearchBF:
    def __init__(self, config=None, verbose=False):
        tools_BF.check_create_folder(NOVELTY_HISTORY_FOLDER, verbose=verbose)
        used_config = {
            "decimalResolution": 2,
            "selectedFields": ["avg BPM animal", "avg BPM human", "delta BPM", "class"],
            "maxValueFields": [255.0, 255.0, 255.0, 4],
            "minValueFields": [90.0, 90.0, 0.0, 0],
            "allowAutogamy": False,
            "crossoverProbability": 0.8,
            "mutationProbability": 0.1,
            "elitism": 0.1,
        }
        self.nextSelected = None

        if not(config is None):
            for k in config.key:
                used_config[k] = config[k]

        self.implementation = {
            "mean": self.__chose_mean_genome__,
            "min": self.__chose_min_genome__,
            "max": self.__chose_max_genome__,
            "random": self.__chose_random_genome__,
            "specific": self.__chose_specific_genome__,
        }

        self.excelLoader = tools_BF.ExcelLoader()
        self.config = used_config
        self.countGenerated = 0
        self.currentGeneration = 0
        self.maxValues = used_config["maxValueFields"]
        self.store_data = []

        dic = self.excelLoader.loadExcel(0, used_config["selectedFields"], verbose=True)

        nRows = self.__check_dic_sizes__(dic)

        self.population = []

        for entrance in dic.keys():
            type_aux = type(dic[entrance][0])

            for i in range(nRows):
                if len(self.population) <= i:
                    self.population.append({
                        "novelty": random.randint(0, 7),
                        "genome_id": i,
                        "genotype": [],
                        "generation": 0
                    })

                value = dic[entrance][i]

                if type_aux == numpy.float64:
                    value = float(value)
                elif type_aux == numpy.int64:
                    value = int(value)

                self.population[i]["genotype"].append(value)

        self.population, self.sumGen = self.__get_novelty__(self.population, nRows,
                                                            len(used_config["selectedFields"]), self.maxValues)
        self.nPopulation = nRows
        self.nGenotypes = len(used_config["selectedFields"])
        self.countGenerated = self.nPopulation

        self.currentGeneration += 1

    def printStoreData(self, selected):
        x = list(range(self.currentGeneration))

        items = [[], [], [], [], []]
        print(items)
        print(self.store_data)
        print(self.store_data[2][3])
        for i in range(len(self.store_data)):
            for j in range(len(self.store_data[i])):
                items[j].append(self.store_data[i][j])
        print("_-------")
        print(items)
        # plotting the points
        for i in range(len(items)):
            plt.plot(x, items[i])

            # naming the x axis
            plt.xlabel('x - axis')
            # naming the y axis
            plt.ylabel('y - axis')

            # giving a title to my graph
            plt.title(f'{i} item')

            # function to show the plot
            plt.show()

    def step(self):
        # print(self.population)
        sorted_values = self.__sort_values_by_parameter__(self.population, "novelty")
        adj_values = self.__adjusted_dic__(sorted_values)
        try:
            children = self.__get_children__(adj_values)
        except Exception as E:
            print(self.population)
            print("-------")
            print(sorted_values)
            adj_values = self.__adjusted_dic__(sorted_values)
            raise ValueError(E)
        children, self.sumGen = self.__get_novelty__(children, self.nPopulation * 2, len(self.config["selectedFields"]),
                                                 self.maxValues, self.sumGen, self.countGenerated)

        # self.sumGen = list(map(lambda x, y: x + y, self.sumGen, sum_aux))
        self.countGenerated += self.nPopulation * 2
        self.__generate_next_population__(children, sorted_values)
        self.currentGeneration += 1

    def __get_children__(self, sorted_adj_values):
        children = []

        for i in range(self.nPopulation):

            # Select random parents. The probability of choosing a genome to be a parent is directly proportional
            # to the novelty punctuation.
            randomChoice_1_population_index = random.choice(sorted_adj_values)

            # index_randomChoice_1 = sorted_adj_values.index(randomChoice_1_population_index)
            # sorted_adj_values.pop(index_randomChoice_1)
            # sorted_adj_values.remove(randomChoice_1_population_index)
            randomChoice_2_population_index = random.choice(sorted_adj_values)

            if not self.config["allowAutogamy"]:
                while randomChoice_2_population_index == randomChoice_1_population_index:
                    randomChoice_2_population_index = random.choice(sorted_adj_values)

            # sorted_adj_values.remove(randomChoice_2_population_index)
            # index_randomChoice_2 = sorted_adj_values.index(randomChoice_2_population_index)
            # sorted_adj_values.pop(index_randomChoice_2)
            parent1 = self.population[randomChoice_1_population_index]
            parent2 = self.population[randomChoice_2_population_index]
            offspring_12, offspring_21 = self.__crossover__(parent1, parent2)

            children.append(offspring_12)
            children.append(offspring_21)

        return children

    def __crossover__(self, parent1, parent2):
        offspring_1 = self.__init_offspring__(self.currentGeneration, 0)
        offspring_2 = self.__init_offspring__(self.currentGeneration, 0)

        for i in range(len(parent1["genotype"])):
            val1 = parent1["genotype"][i]
            val2 = parent2["genotype"][i]
            maxValue = self.config["maxValueFields"][i]
            minValue = self.config["minValueFields"][i]
            type1 = type(val1)
            type2 = type(val2)

            if type2 != type1:
                raise ValueError("Types are different")

            if type1 == int:
                aux_1, aux_2 = self.__int_crossover__(val1, val2, minValue, maxValue)

                aux_1 = self.__int_mutation__(aux_1, maxValue)
                aux_2 = self.__int_mutation__(aux_2, maxValue)

                aux_1 = self.__check_between_values__(aux_1, maxValue, minValue)
                aux_2 = self.__check_between_values__(aux_2, maxValue, minValue)
            elif type1 == float:
                aux_1, aux_2 = self.__float_crossover__(val1, val2, minValue, maxValue)

                aux_1 = self.__float_mutation__(aux_1, maxValue)
                aux_2 = self.__float_mutation__(aux_2, maxValue)

                aux_1 = self.__check_between_values__(aux_1, maxValue, minValue)
                aux_2 = self.__check_between_values__(aux_2, maxValue, minValue)
            else:
                raise ValueError(f"Unrecognized type, not crossover is available for this data type {type1}")

            offspring_1["genotype"].append(aux_1)
            offspring_2["genotype"].append(aux_2)

        return offspring_1, offspring_2

    def __float_mutation__(self, value, maxValue):
        decimalResolution = self.config["decimalResolution"]
        multDecimal = int(math.pow(10, decimalResolution))

        int_value = int(value)
        float_part = int(round((value - int_value), decimalResolution) * multDecimal)

        int_maxValue = int(maxValue)

        int_value = self.__int_mutation__(int_value, int_maxValue)
        float_part = self.__int_mutation__(float_part, multDecimal - 1) % multDecimal

        return int_value + (float_part / multDecimal)

    def __int_mutation__(self, value, maxValue):
        maxValue_bin = bin(maxValue).strip("0b")
        aux_minMutation = 1.0 - self.config["mutationProbability"]
        value_bin = bin(value).strip("0b")

        if len(value_bin) != len(maxValue_bin):
            aux_0 = '0' * (len(maxValue_bin) - len(value_bin))
            value_bin = aux_0 + value_bin

        for i in range(len(maxValue_bin)):
            randNum = random.random()

            if randNum > aux_minMutation:
                value_bin = self.__switch_bit__(value_bin, i)

        return int(value_bin, 2)

    def __generate_next_population__(self, children, sorted_pop):
        previous_pop = self.population
        new_pop = []
        size_previous_pop = self.nPopulation
        elitism = self.config["elitism"]
        if elitism:
            nElit = int(elitism * size_previous_pop)

            for i in range(nElit):
                max_novel = max(sorted_pop)
                sel = sorted_pop[max_novel].pop(0)

                if not(len(sorted_pop[max_novel])):
                    sorted_pop.pop(max_novel)

                new_pop.append(self.population[sel])

        if len(new_pop) != size_previous_pop:
            chosen = []
            sorted_children = self.__sort_values_by_parameter__(children, "novelty")
            adj_children = self.__adjusted_dic__(sorted_children)

            while len(new_pop) != size_previous_pop:
                randChoice = random.choice(adj_children)

                if not(randChoice in chosen):
                    chosen.append(randChoice)
                    new_pop.append(children[randChoice])

        self.population = new_pop

    def transform_genome_into_usable_data(self, aux_data, sequence=None, store_next_genome=False, step=False,
                                          selectMax=False):
        if self.nextSelected is None or selectMax:
            selected_genome = self.selectGenome(method="max")
        else:
            print(self.nextSelected)
            selected_genome = self.selectGenome(method="specific", chosen=int(self.nextSelected))

        # Delta position in the genome
        print(selected_genome)
        delta = selected_genome[2]
        trans_data = None

        if store_next_genome:
            self.nextSelected = delta % self.nPopulation

        if sequence is None:
            # In this case, the selected genome will be used for selecting the sequence using the class position

            # Class position in the genome
            sequence = int(1 + selected_genome[3])

            if not (sequence in aux_data):
                aux_value = list(aux_data)

                if len(aux_value) > 1:
                    aux_seq = sequence % len(aux_value)
                    sequence = aux_value[aux_seq]
                else:
                    sequence = aux_value[0]
        elif sequence == 2:

            # In case of being in the second sequence:
            # Delta value selects whether to go “left to right” or “right to left”
            # Proposed: This will depend on the parity of the delta value
            # trans_data will boolean. True -> go from right lo left.
            # trans_data will boolean. False -> go from left lo right.

            trans_data = (delta % 2) == 0

        elif sequence == 5:

            # In case of being in the fifth sequence:
            # Delta value selects whether to add or remove one robot.
            # Proposed: In case that the first digit is 0, one robot will be removed
            # In case of being 1, one robot will be added

            trans_data = delta & 0x1

        else:
            # In case of being in the first sequence:
            # Starting robot = “delta” (sum of the binary digits) mod “total number of robots.
            # aux_data will contain the number of available robots in that iteration
            # trans_data will be the next robot to choose

            # In case of being in the third sequence:
            # Delta value selects which floor to start on.
            # aux_data will contain the number of available floors.
            # trans_data will be the next floor to choose

            # In case of being in the fourth sequence:
            # Delta value selects which is the second movement to do.
            # aux_data will contain the number of the available movements.
            # trans_data will be the second available movement

            trans_data = delta % aux_data

        if step:
            self.step()

        return sequence, delta, trans_data

    def transform_delta_value_delay(self, max_delay, min_delay, store_next=False, step=False, selectMax=False):
        if self.nextSelected is None or selectMax:
            selected_genome = self.selectGenome(method="max")
        else:
            selected_genome = self.selectGenome(method="specific", chosen=int(self.nextSelected))

        delta = selected_genome[2]

        if store_next:
            self.nextSelected = delta % self.nPopulation

        min_delta = self.config["maxValueFields"][2]
        max_delta = self.config["minValueFields"][2]

        delay = (delta - min_delta) * (max_delay - min_delay) / (max_delta - min_delta) + min_delay
        print("delay", delay)

        if step:
            self.step()

        return delay

    @staticmethod
    def __switch_bit__(value, pos):
        aux = list(value)
        if aux[pos]:
            aux[pos] = '0'
        else:
            aux[pos] = '1'

        return ''.join(aux)

    @staticmethod
    def __init_offspring__(generation, off_id):
        offs = {
            "novelty": 0,
            "genome_id": off_id,
            "genotype": [],
            "generation": generation
        }

        return offs

    def __float_crossover__(self, parent1, parent2, minValue, maxValue):

        decimalResolution = self.config["decimalResolution"]
        mult_decimal = int(math.pow(10, decimalResolution))
        intPart_1 = int(parent1)
        intPart_2 = int(parent2)

        floatPart_1 = int(round(parent1 - intPart_1, decimalResolution) * math.pow(10, decimalResolution))
        floatPart_2 = int(round(parent2 - intPart_2, decimalResolution) * math.pow(10, decimalResolution))

        intCrossOver12, intCrossOver21 = self.__int_crossover__(intPart_1, intPart_2, int(minValue), int(maxValue))
        floatCrossOver12, floatCrossOver21 = self.__int_crossover__(floatPart_1, floatPart_2, 0, mult_decimal - 1)

        floatCrossOver12 &= mult_decimal
        floatCrossOver21 &= mult_decimal

        firstCrossover = intCrossOver12 + (floatCrossOver12 / mult_decimal)
        secondCrossover = intCrossOver21 + (floatCrossOver21 / mult_decimal)

        return firstCrossover, secondCrossover

    @staticmethod
    def __int_crossover__(parent1, parent2, minValue, maxValue):

        mask = random.randint(minValue, maxValue)
        mask_n = ~mask & maxValue

        firstCrossover = (parent1 | mask) & (parent2 | mask_n)
        secondCrossover = (parent2 | mask) & (parent1 | mask_n)

        return firstCrossover, secondCrossover

    @staticmethod
    def __sort_values_by_parameter__(values, parameter):
        aux_dic = {}
        res_dic = {}

        for i in range(len(values)):
            if not (values[i][parameter] in aux_dic):
                aux_dic[values[i][parameter]] = []

            aux_dic[values[i][parameter]].append(i)

        key_sorted = sorted(aux_dic)

        for k in key_sorted:
            res_dic[k] = aux_dic[k]

        return res_dic

    @staticmethod
    def __adjusted_dic__(res_dic):
        i = 1
        res = []

        # This might not be the most effective solution

        for rd in res_dic:
            for r in res_dic[rd]:
                for _ in range(i):
                    res.append(r)

            i += 1

        return res

    # @staticmethod
    def __get_novelty__(self, pop, size_gens, size_genotype, maxValues, previous_sum=None, previous_len=None):
        global o
        sum_genotype = [0] * size_genotype
        mean_genotype = [0] * size_genotype
        div = size_gens
        counts = [0, 0, 0, 0, 0]

        if o == 20:
            print("hey")
        else:
            o += 1

        for p in pop:
            sum_genotype = list(map(lambda x, y, z: x + (y/z), sum_genotype, p["genotype"], maxValues))
            counts[p["genotype"][3]] += 1

        if not (previous_sum is None) and True:
            sum_genotype_aux = list(map(lambda x, y: x + y, sum_genotype, previous_sum))
            div += previous_len
            print(f"div: {div}")
        else:
            sum_genotype_aux = sum_genotype

        for i in range(size_genotype):
            mean_genotype[i] = sum_genotype_aux[i] / div

        print(f"mean_genotype: {mean_genotype}, real: {list(map(lambda x, y: x * y, mean_genotype, maxValues))}")
        print(f"counts: {counts}")
        self.store_data.append(counts)

        for k in range(len(pop)):
            nov = 0
            for i in range(size_genotype):
                nov += ((pop[k]["genotype"][i] / maxValues[i]) - mean_genotype[i]) ** 2

            pop[k]['novelty'] = round(math.sqrt(nov), 3)

        return pop, sum_genotype_aux

    def selectGenome(self, method="random", chosen=None):
        if not(method in self.implementation):
            raise ValueError(f"The chosen method is not implemented, select one of the following methods: "
                             f"{self.implementation.keys()}")

        if method != "specific":
            selected = self.implementation[method]()
        elif chosen is None or chosen > len(self.population):
            raise ValueError(f"Please select a individual from 0 to {len(self.population) - 1}")
        else:
            selected = self.implementation[method](chosen)

        return selected

    @staticmethod
    def __check_dic_sizes__(dic):
        prev_size = -1

        for i in dic.keys():
            size = len(dic[i])

            if prev_size != -1 and prev_size != size:
                raise ValueError("The sizes of the loaded excel doesn't match, check the excel format please.")

            prev_size = size

        return prev_size

    @staticmethod
    def __check_between_values__(value, maxValue, minValue):
        if value > maxValue:
            value = maxValue
        elif value < minValue:
            value = minValue

        return value

    def __chose_specific_genome__(self, chosen):
        return self.population[chosen]["genotype"]

    def __chose_min_genome__(self):
        worst_novelty = 9999
        worst_genome = []

        for one in self.population:
            if one["novelty"] < worst_novelty:
                worst_novelty = one["novelty"]
                worst_genome = one["genotype"]

        return worst_genome

    def __chose_max_genome__(self):
        best_novelty = 0
        best_genome = []

        for one in self.population:
            if one["novelty"] > best_novelty:
                best_novelty = one["novelty"]
                best_genome = one["genotype"]

        return best_genome

    def __chose_random_genome__(self):
        one = random.choice(self.population)

        return one["genotype"]

    def __chose_mean_genome__(self):
        mean = [0, 0, 0, 0]
        length_population = [len(self.population)] * 4

        for one in self.population:
            mean = list(map(lambda x, y: x + y, one["genotype"], mean))

        mean = list(map(lambda x, y: x/y, mean, length_population))

        return mean
    #
    #
    # @staticmethod
    # def __mutation__():
    #     pass

o = 0
if __name__ == "__main__":
    test_noveltySearch = NoveltySearchBF()
    i = 0
    # sorted_values = {0.096: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 48, 49, 50, 51, 52, 53, 54, 55, 57, 58, 59, 60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74], 0.097: [56], 0.156: [7, 29, 62], 0.191: [47], 0.564: [5, 6], 0.614: [4], 0.623: [3], 0.649: [2], 0.707: [1], 0.79: [0]}
    # adj_values = test_noveltySearch.__adjusted_dic__(sorted_values)
    # children = test_noveltySearch.__get_children__(adj_values)
    while i < 1000:
        print(test_noveltySearch.population)
        print(len(test_noveltySearch.population))
        test_noveltySearch.step()
        # time.sleep(1)
        i += 1

    test_noveltySearch.printStoreData(3)
    # print(test_noveltySearch.population)
    # n = test_noveltySearch.__float_bin__(10.293)
    #
    # print(n)
    # print(type(n))
