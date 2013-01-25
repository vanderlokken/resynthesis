import math

import numpy


class Oscillator:

    def __init__(self, frequency=440, phase=0, wave="sine"):

        self.frequency = frequency
        self.phase = phase

        output_method_by_wave = {
            "sine": self._get_sine_output,
            "sawtooth": self._get_sawtooth_output
        }

        self.get_output = output_method_by_wave[wave]

    def _get_sine_output(self, sample_count, sample_duration):

        start = self.phase
        end = self.phase + 2 * math.pi * (
            self.frequency * sample_duration * sample_count)

        return numpy.sin(numpy.linspace(start, end, sample_count))

    def _get_sawtooth_output(self, sample_count, sample_duration):

        start = self.phase
        end = self.phase + sample_duration * sample_count * self.frequency

        return numpy.modf(numpy.linspace(start, end, sample_count))[0] * 2 - 1
