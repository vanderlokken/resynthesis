import math

import numpy


class Oscillator:

    def __init__(self, frequency=440, phase=0):

        self.frequency = frequency
        self.phase = phase

    def get_output(self, sample_count, sample_duration):
        
        start = self.phase
        end = self.phase + 2 * math.pi * self.frequency * sample_duration * sample_count

        return numpy.sin(numpy.linspace(start, end, sample_count))
