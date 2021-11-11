import copy
from random import randint, choice, shuffle, random, sample
from copy import deepcopy

INDPB = 0.4
MUTPB = 0.8
CXPB = 0.8
MAX_INT = 500
MIN_INT = 1
GENERATION_COUNT = 1000
POPULATION_SIZE = 500
TOURNAMENT_SIZE = 15

# task settings
OPERAND_COUNT = 15
MAX_ERROR = 1
OPERATORS = ['+', '-', '*', '/']

class Individual:
    def __init__(self) -> None:
        self.expression = []
        self.score = None
    
    def add_operator(self, operator):
        if len(self.expression) % 2 == 0:
            raise "operand expected"
        
        if operator not in OPERATORS:
            raise "not an operator"

        self.expression.append(operator)

    def add_operand(self, operand):
        if len(self.expression) % 2 == 1:
            raise "operator expected"
        
        if type(operand) is not int:
            raise "int expected"

        self.expression.append(operand)

    def calculate_score(self, target):
        # return the absolute distance from the target number
        self.score = abs(target - self.evaluate())
        return self.score

    def evaluate(self):
        return float(eval(str(self)))

    def __str__(self):
        # convert to list of strings
        converted = [str(i) if type(i) is int else i for i in self.expression]

        # join expression to string
        return ' '.join(converted)

    def __len__(self):
        return len(self.expression)


def generate_random_individual_from_numbers(numbers):
    # copy and scrable numbers
    scrambled = deepcopy(numbers)
    shuffle(numbers)

    # create individual with random operators
    ind = Individual()
    for i, num in enumerate(numbers):
        if i != 0:
            ind.add_operator(choice(OPERATORS))
        
        ind.add_operand(num)
    
    return ind

def generate_population(size, numbers):
    population = [generate_random_individual_from_numbers(numbers) for _ in range(size)]
    return population


def generate_task(operand_count = 5):
    # generate numbers
    numbers = []
    for _ in range(operand_count):
        numbers.append(randint(MIN_INT, MAX_INT))

    # create an individual
    ind = generate_random_individual_from_numbers(numbers)

    # evaluate to determine one possible target
    target = ind.evaluate()

    return numbers, target


def mutate(ind, numbers):
    # copy and reset score
    mutant = copy.deepcopy(ind)
    mutant.score = None

    for i in range(len(mutant)):
        # decide whether to mutate based on an individual probability
        if random() <= INDPB:
            # odd positions must be swapped with operands, even positions with operators
            if i % 2 == 0:
                # odd, swap with another operand from the same equation
                to_swap_with = 2*randint(0, len(numbers) - 1)
                mutant.expression[i], mutant.expression[to_swap_with] = mutant.expression[to_swap_with], mutant.expression[i]

            else:
                # even, swap with operator
                mutant.expression[i] = choice(OPERATORS)

    return mutant


def crossover(ind1, ind2):
    """
    Leaves operands where they are and only swaps operators.
    """
    # clone and reset score
    child1, child2 = deepcopy(ind1), deepcopy(ind2)
    child1.score, child2.score = None, None

    # decide where to cut
    operands1 = child1.expression[1::2]
    operands2 = child2.expression[1::2]
    cut = randint(1, len(operands1) - 2)

    # cross operators at cut
    operands1, operands2 = [*operands1[:cut], *operands2[cut:]], [*operands2[:cut], *operands1[cut:]]

    # inject operands back
    for i in range(len(operands1)):
        child1.expression[2*i+1] = operands1[i]
        child2.expression[2*i+1] = operands2[i]

    return child1, child2


def select_tournament(population, tournament_size, count, target):
    best = []

    for _ in range(count):
        subset = sample(population, tournament_size)

        # calculate scores
        for ind in subset:
            if ind.score is None:
                ind.calculate_score(target)
        
        # add best to the pool
        best.append(min(subset, key=lambda x: x.score))
    
    return best

def evolve(numbers, target, population):
    for generation in range(GENERATION_COUNT):
        
        # select the next generation
        offspring = select_tournament(population, TOURNAMENT_SIZE,  len(population), target)
        
        # clone each one
        offspring = [deepcopy(ind) for ind in offspring]

        # crossover
        for i in range(len(population)):
            if random() < CXPB:
                other = randint(0, len(population) - 1)

                if other == i:
                    continue
                population[i], population[other] = crossover(population[i], population[other])

    #     # Apply mutation on the offspring
        for i in range(len(offspring)):
            if random() < MUTPB:
                offspring[i] = mutate(offspring[i], numbers)

        # The population is entirely replaced by the offspring
        population = deepcopy(offspring)

        # calculate scores
        for ind in population:
            if ind.score is None:
                ind.calculate_score(target)
        
        # find best individual
        best = min(population, key=lambda x : x.score)

        # print best result at the moment
        print(best.score)

        # break early if target individual was found
        if best.score < MAX_ERROR:
            break


def random_search(numbers, target):
    ind = generate_random_individual_from_numbers(numbers)
    while ind.calculate_score(target) >= MAX_ERROR:
        ind = generate_random_individual_from_numbers(numbers)
    print(ind.score)

# generate task
numbers, target = generate_task(operand_count=OPERAND_COUNT)
print(numbers, target)
print()

# generate population
population = generate_population(POPULATION_SIZE, numbers)

evolve(numbers, target, population)
print('evolved')
random_search(numbers, target)