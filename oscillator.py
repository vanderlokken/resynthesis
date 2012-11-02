import math

import numpy


class Oscillator:

    def __init__(self, frequency=440, phase=0):

        self.frequency = frequency
        self.phase = phase

    def get_output(self, sample_count, sample_duration):

        time_points = numpy.arange(0, sample_count * sample_duration, sample_duration)

        return numpy.sin(time_points * (2 * math.pi * self.frequency) + self.phase)
