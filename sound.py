from collections import defaultdict
import copy
import random

from algorithm import Genome

import numpy
import scipy.fftpack

from envelope import Envelope
from oscillator import Oscillator
from pcm_audio import PcmAudio


class Spectrum:

    _windows = {}

    def __init__(self, samples):

        if len(samples) not in self._windows:
            self._windows[len(samples)] = numpy.hanning(len(samples))

        amplitudes = scipy.fftpack.rfft(samples * self._windows[len(samples)])

        self._magnitudes = numpy.abs(amplitudes[1:]) # TODO: remove unaudible frequencies

    @property
    def magnitudes(self):
        return self._magnitudes


def _generate_spectrum_list(pcm_audio, window_size=4096):

    window_count = len(pcm_audio.samples) / window_size
    window = lambda index: \
        pcm_audio.samples[index * window_size : (index + 1) * window_size]

    return [Spectrum(window(index)) for index in range(window_count)]


class Sound(Genome):

    _minimal_frequency = 40
    _maximal_frequency = 4200

    _point_count = 5
    
    def __init__(self, reference_pcm_audio, base_pcm=None):

        Genome.__init__(self)

        self._reference_pcm_audio = reference_pcm_audio
        self._reference_spectrum_list = _generate_spectrum_list(reference_pcm_audio)

        self._base_pcm = base_pcm

        self._maximal_amplitude = numpy.abs(reference_pcm_audio.samples).max()

        self._frequency = self.random_frequency()
        self._phase = self.random_phase()
        self._time_points = [random.random() for _ in xrange(self._point_count)]
        self._amplitudes = [self.random_amplitude() for _ in xrange(self._point_count)]

    def mutate(self, rate):

        mutated = False

        if random.random() <= rate:
            self._frequency = self.random_frequency()
            mutated = True

        if random.random() <= rate:
            self._phase = self.random_phase()
            mutated = True

        for index, (time, amplitude) in enumerate(zip(self._time_points, self._amplitudes)):

            if random.random() <= rate:
                self._time_points[index] = random.random()
                mutated = True

            if random.random() <= rate:
                self._amplitudes[index] = self.random_amplitude()
                mutated = True

        return mutated

    def cross(self, other):

        def create_child(first_parent, second_parent):

            child = copy.copy(first_parent)

            child._frequency = random.uniform(
                first_parent._frequency, second_parent._frequency)

            child._phase = random.uniform(
                first_parent._phase, second_parent._phase)

            _1 = list(zip(first_parent._time_points, first_parent._amplitudes))
            _1.sort(key=lambda point: point[0])

            _2 = list(zip(second_parent._time_points, second_parent._amplitudes))
            _2.sort(key=lambda point: point[0])

            child._time_points = child._time_points[:]
            child._amplitudes = child._amplitudes[:]

            for index in range(len(_1)):

                child._time_points[index] = random.uniform(
                    _1[index][0], _2[index][0])

                child._amplitudes[index] = random.uniform(
                    _1[index][1], _2[index][1])

            return child

        first_child = create_child(self, other)
        second_child = create_child(self, other)

        first_child.reset_score()
        second_child.reset_score()

        return (first_child, second_child)

    def evaluate(self):

        generated_pcm_audio = self.to_pcm_audio()
        generated_spectrum_list = _generate_spectrum_list(generated_pcm_audio)

        ranks = []

        for spectrum1, spectrum2 in zip(
                self._reference_spectrum_list, generated_spectrum_list):

            squared = spectrum1.magnitudes * spectrum1.magnitudes

            frequency_rank = numpy.minimum(
                spectrum1.magnitudes * spectrum2.magnitudes, squared).sum() / squared.sum()

            magnitude_rank = 1 / (1 + 
                numpy.abs(spectrum2.magnitudes - spectrum1.magnitudes).sum() / spectrum1.magnitudes.sum())

            ranks.append(frequency_rank + magnitude_rank)

        return numpy.average(ranks)

    def to_pcm_audio(self):

        sample_count = len(self._reference_pcm_audio.samples)
        sample_duration = self._reference_pcm_audio.duration / sample_count

        oscillator = Oscillator(self._frequency, self._phase)
        envelope = Envelope(0)
        for time, amplitude in zip(self._time_points, self._amplitudes):
            envelope.add_point(time * self._reference_pcm_audio.duration, amplitude)

        samples = oscillator.get_output(sample_count, sample_duration)
        samples *= envelope.get_output(sample_count, sample_duration)

        if self._base_pcm:
            samples += self._base_pcm.samples

        return PcmAudio(self._reference_pcm_audio.sampling_rate, samples)

    def __repr__(self):

        points = list(zip(self._time_points, self._amplitudes))
        points.sort(key=lambda point: point[0])

        return '\n'.join(
            (
                "Frequency: %.1f Hz" % self._frequency,
                "Phase: %.2f" % self._phase,
                "Amplitude envelope: %s" % str(points)
            ))

    def random_amplitude(self):
        return random.randint(0, self._maximal_amplitude)

    @classmethod
    def random_frequency(cls):
        return random.uniform(cls._minimal_frequency, cls._maximal_frequency)

    @staticmethod
    def random_phase():
        return random.uniform(0, 2 * numpy.pi)
