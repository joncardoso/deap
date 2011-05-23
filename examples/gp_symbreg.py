#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import sys
import operator
import math
import logging
import random

from deap import algorithms
from deap import base
from deap import creator
from deap import gp
from deap import operators
from deap import toolbox

# Define new functions
def safeDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 0

pset = gp.PrimitiveSet("MAIN", 1)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(safeDiv, 2)
pset.addPrimitive(operator.neg, 1)
pset.addPrimitive(math.cos, 1)
pset.addPrimitive(math.sin, 1)
pset.addEphemeralConstant(lambda: random.randint(-1,1))
pset.renameArguments({"ARG0" : "x"})

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, pset=pset)

tools = toolbox.Toolbox()
tools.register("expr", gp.generateRamped, pset=pset, min_=1, max_=2)
tools.register("individual", creator.Individual, toolbox.Iterate(tools.expr))
tools.register("population", list, toolbox.Repeat(tools.individual, 100))
tools.register("lambdify", gp.lambdify, pset=pset)

def evalSymbReg(individual):
    # Transform the tree expression in a callable function
    func = tools.lambdify(expr=individual)
    # Evaluate the sum of squared difference between the expression
    # and the real function : x**4 + x**3 + x**2 + x
    values = (x/10. for x in xrange(-10,10))
    diff_func = lambda x: (func(x)-(x**4 + x**3 + x**2 + x))**2
    diff = sum(map(diff_func, values))
    return diff,

tools.register("evaluate", evalSymbReg)
tools.register("select", operators.selTournament, tournsize=3)
tools.register("mate", operators.cxTreeUniformOnePoint)
tools.register("expr_mut", gp.generateFull, min_=0, max_=2)
tools.register('mutate', operators.mutTreeUniform, expr=tools.expr_mut)

stats_t = operators.Stats(lambda ind: ind.fitness.values)
stats_t.register("Avg", operators.mean)
stats_t.register("Std", operators.std_dev)
stats_t.register("Min", min)
stats_t.register("Max", max)

def main():
    random.seed(318)
    
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    pop = tools.population()
    hof = operators.HallOfFame(1)
    stats = tools.clone(stats_t)
    
    algorithms.eaSimple(tools, pop, 0.5, 0.1, 40, stats, halloffame=hof)
    logging.info("Best individual is %s, %s", gp.evaluate(hof[0]), hof[0].fitness)
    
    return pop, stats, hof

if __name__ == "__main__":
    main()
