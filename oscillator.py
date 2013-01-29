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

    def _get_sine_output(self, time_points):
        arguments = (2 * numpy.pi * self.frequency) * time_points
        arguments += self.phase
        return numpy.sin(arguments, out=arguments)

    def _get_sawtooth_output(self, time_points):
        arguments = self.frequency * time_points
        arguments += self.phase
        return numpy.modf(arguments)[0] * 2 - 1
