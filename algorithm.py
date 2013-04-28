from collections import deque
import logging
import random
import sys


class Genome(object):

    def __init__(self):
        self.__score = None

    def cross(self, other):
        raise NotImplementedError()

    def mutate(self, rate):
        raise NotImplementedError()

    def evaluate(self):
        raise NotImplementedError()

    @property
    def score(self):
        if self.__score is None:
            self.__score = self.evaluate()
        return self.__score

    def reset_score(self):
        self.__score = None


_genome_score = lambda genome: genome.score


class Population(object):

    def __init__(self, genome_factory, size):
        self._generation_count = 0
        self._size = size
        self._genomes = [genome_factory() for _ in xrange(size)]

    def select(self, selection_rate):
        selected_count = int(self._size * selection_rate)
        self._genomes.sort(key=_genome_score, reverse=True)
        self._genomes = self._genomes[:selected_count]

    def crossbreed(self):

        breed = []

        # Uses tournament selection algorithm
        tournament_size = 4

        while len(self._genomes) + len(breed) < self._size:

            first_tournament = random.sample(self._genomes, tournament_size)
            second_tournament = random.sample(self._genomes, tournament_size)

            first_parent = max(first_tournament, key=_genome_score)
            second_parent = max(second_tournament, key=_genome_score)

            if first_parent is not second_parent:
                breed += first_parent.cross(second_parent)

        self._genomes += breed
        self._genomes = self._genomes[:self._size]

    def mutate(self, mutation_rate, elitism_rate):
        elite_count = int(self._size * elitism_rate)
        for genome in self._genomes[elite_count:]:
            if genome.mutate(mutation_rate):
                genome.reset_score()

    def advance_generation(self):
        self._generation_count += 1

    @property
    def best_genome(self):
        return max(self._genomes, key=_genome_score)

    def output_statistics(self):
        scores = list(genome.score for genome in self._genomes)
        best_score = max(scores)
        worst_score = min(scores)
        mean_score = sum(scores) / float(self._size)
        logger.info(
            "Generation %d. Best: %.2f. Worst: %.2f. Mean: %.2f",
            self._generation_count, best_score, worst_score, mean_score)


class GeneticAlgorithm(object):

    def __init__(self):
        self.generation_limit = sys.maxint
        self.generations_without_improvement_limit = 30
        self.score_improvement_threshold = 100
        self.selection_rate = 0.5
        self.mutation_rate = 0.25
        self.elitism_rate = 0.15
        self.mutation_decrease_rate = 0.01

    def run(self, population):

        current_mutation_rate = self.mutation_rate

        last_generations_scores = deque()

        for generation_index in xrange(self.generation_limit):

            population.select(self.selection_rate)
            population.crossbreed()
            population.mutate(current_mutation_rate, self.elitism_rate)
            population.advance_generation()

            population.output_statistics()

            last_generations_scores.append(population.best_genome.score)

            if len(last_generations_scores) ==\
                    self.generations_without_improvement_limit:
                score_improvement = (population.best_genome.score -
                    last_generations_scores.popleft())
                if score_improvement < self.score_improvement_threshold:
                    break

            current_mutation_rate *= 1 - self.mutation_decrease_rate

        return population.best_genome


def _prepare_logging():
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(name)s %(message)s", "%X"))
    logger.addHandler(handler)


logger = logging.getLogger("GeneticAlgorithm")
_prepare_logging()
