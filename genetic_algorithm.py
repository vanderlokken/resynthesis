import random


def random_choice(sequence, count):
    return [random.choice(sequence) for _ in xrange(count)]


class GeneticAlgorithm:

    def __call__(self, generations=10, survived_count=10, hybrid_count=80, mutant_count=80):

        population_count = survived_count + hybrid_count + mutant_count

        self._individuals = [self._spawn() for _ in xrange(population_count)]

        fitness_by_object_id = {}

        for _ in xrange(generations):

            for individual in self._individuals:
                if id(individual) not in fitness_by_object_id:
                    fitness_by_object_id[id(individual)] = self._fit(individual)

            # Sort from the fittest to the least fit
            self._individuals.sort(
                key=lambda individual: fitness_by_object_id[id(individual)],
                reverse=True)

            survived = self._individuals[:survived_count]
            hybrids = map(self._cross, random_choice(survived, hybrid_count), random_choice(survived, hybrid_count))
            mutants = map(self._mutate, random_choice(survived, mutant_count))

            self._individuals = survived + hybrids + mutants

        return survived[0]

    def _fit(self, individual):
        raise NotImplementedError()

    def _spawn(self):
        raise NotImplementedError()

    def _cross(self, first, second):
        raise NotImplementedError()

    def _mutate(self, individual):
        raise NotImplementedError()
