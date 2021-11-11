from deap import base
from deap import creator
import operator
from deap import tools
from random import randint, choice, shuffle, random
from deap import gp

INDPB = 0.0
MUTPB = 0.0
CXPB = 0.0
GENERATION_COUNT = 10
POPULATION_SIZE = 1000
TOURNAMENT_SIZE = 100


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

NUMBERS = [10, 25, 100, 5, 3]
OPERATORS = ['+', '-', '*', '/']
TARGET = 2512

# create base types operator and operand
toolbox.register("attr_operand", choice, NUMBERS)
toolbox.register("attr_operator", choice, OPERATORS)

# the cycle genereates one operand too many, it will be ignored
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_operand, toolbox.attr_operator), n=len(NUMBERS))

toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def evaluate(individual):
    # print(individual)
    converted = [str(i) if type(i) is int else i for i in individual]

    # cut the last operand as it is not important and makes the expression invalid
    converted = converted[:-1]

    # join expression to string
    expression = ' '.join(converted)

    # evaluate
    value = float(eval(expression))

    # return the absolute distance from the target number
    diff = abs(TARGET - value)
    print('score:', diff)
    return (diff,)


def mutate(ind1):
    mutant = toolbox.clone(ind1)

    for i in range(len(mutant)):
        # decide whether to mutate based on individual probability
        if random() <= INDPB:
            # odd positions must be swapped with operands, even with operators
            if i % 2 == 1:
                # odd, swap with operand
                mutant[i] = choice(NUMBERS)
            else:
                # even, swap with operator
                mutant[i] = choice(OPERATORS)
    
    del mutant.fitness.values

    return mutant


def crossover(ind1, ind2):
    child1, child2 = [toolbox.clone(ind) for ind in (ind1, ind2)]

    cut = randint(1, len(child1) - 2)
    toolbox.
    child1[cut:], child2[cut:] = child2[cut:], child1[cut:]

    del child1.fitness.values
    del child2.fitness.values

    return child1, child2




toolbox.register("mate", crossover)
toolbox.register("mutate", mutate)
toolbox.register("select", tools.selTournament, tournsize=TOURNAMENT_SIZE)
toolbox.register("evaluate", evaluate)


population = toolbox.population(n=POPULATION_SIZE)

for generation in range(GENERATION_COUNT):
    
    # select the next generation
    offspring = toolbox.select(population, len(population))
    
    # clone them
    offspring = list(map(toolbox.clone, offspring))

    # Apply crossover on the offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random() < CXPB:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

    # Apply mutation on the offspring
    for mutant in offspring:
        if random() < MUTPB:
            toolbox.mutate(mutant)
            del mutant.fitness.values

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # The population is entirely replaced by the offspring
    population[:] = offspring

population.sort(key = lambda x: evaluate(x))
print(evaluate(population[0]))

"""
TODO:
- does mutate even work?
- focuses on one solution (either take more different ones or mutate more)
- make a random search from the same functions
- generate different test cases
- plot
- notebook (pdf)
"""