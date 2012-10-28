import copy
import random

import pyevolve.Util
from pyevolve.GenomeBase import GenomeBase

import numpy
import scipy.fftpack

from amplitude_envelope import AmplitudeEnvelope
from oscillator import Oscillator
from pcm_audio import PcmAudio


class Spectrum:

    def __init__(self, samples):

        amplitudes = scipy.fftpack.rfft(
            numpy.array(map(float, samples)) * numpy.hanning(len(samples)))

        self._magnitudes = numpy.abs(amplitudes[1:])

    @property
    def magnitudes(self):
        return self._magnitudes


def _generate_spectrum_list(pcm_audio, window_size=4096):

    window_count = len(pcm_audio.samples) / window_size
    window = lambda index: \
        pcm_audio.samples[index * window_size : (index + 1) * window_size]

    return [Spectrum(window(index)) for index in range(window_count)]


class Sound(GenomeBase):

    _minimal_frequency = 40
    _maximal_frequency = 4200

    _point_count = 5
    
    def __init__(self, reference_pcm_audio):

        GenomeBase.__init__(self)

        self.initializator.set(self._initialize)
        self.mutator.set(self._mutate)
        self.crossover.set(self._cross)
        self.evaluator.set(self._evaluate)

        self._reference_pcm_audio = reference_pcm_audio
        self._reference_spectrum_list = _generate_spectrum_list(reference_pcm_audio)

        self._minimal_amplitude = numpy.min(reference_pcm_audio.samples)
        self._maximal_amplitude = numpy.max(reference_pcm_audio.samples)

    @classmethod
    def _initialize(cls, sound):
        sound._frequency = cls.random_frequency()
        sound._time_points = [random.random() for _ in xrange(cls._point_count)]
        sound._amplitudes = [sound.random_amplitude() for _ in xrange(cls._point_count)]

    @classmethod
    def _mutate(cls, sound, **kwargs):

        mutation_probability = kwargs["pmut"]

        mutation_count = 1

        if pyevolve.Util.randomFlipCoin(mutation_probability):
            sound._frequency = cls.random_frequency()
            mutation_count += 1

        for index, (time, amplitude) in enumerate(zip(sound._time_points, sound._amplitudes)):

            if pyevolve.Util.randomFlipCoin(mutation_probability):
                sound._time_points[index] = random.random()
                mutation_count += 1

            if pyevolve.Util.randomFlipCoin(mutation_probability):
                sound._amplitudes[index] = sound.random_amplitude()
                mutation_count += 1

        return mutation_count

    @staticmethod
    def _cross(sound, **kwargs):

        def create_child(first_parent, second_parent):

            child = first_parent.clone()

            child._frequency = random.uniform(
                first_parent._frequency, second_parent._frequency)

            _1 = list(zip(first_parent._time_points, first_parent._amplitudes))
            _1.sort(key=lambda point: point[0])

            _2 = list(zip(second_parent._time_points, second_parent._amplitudes))
            _2.sort(key=lambda point: point[0])

            for index in range(len(_1)):

                child._time_points[index] = random.uniform(
                    _1[index][0], _2[index][0])

                child._amplitudes[index] = random.uniform(
                    _1[index][1], _2[index][1])

            return child

        first_parent = kwargs["mom"]
        second_parent = kwargs["dad"]
        children_count = kwargs["count"]

        first_child, second_child = None, None

        if children_count >= 1:
            first_child = create_child(first_parent, second_parent)
        if children_count >= 2:
            second_child = create_child(second_parent, first_parent)

        return (first_child, second_child)

    @staticmethod
    def _evaluate(sound):

        generated_pcm_audio = sound.to_pcm_audio()
        generated_spectrum_list = _generate_spectrum_list(generated_pcm_audio)

        ranks = []

        for spectrum1, spectrum2 in zip(
                sound._reference_spectrum_list, generated_spectrum_list):

            squared = spectrum1.magnitudes * spectrum1.magnitudes

            frequency_rank = numpy.minimum(
                spectrum1.magnitudes * spectrum2.magnitudes, squared).sum() / squared.sum()

            magnitude_rank = 1 / (1 + 
                numpy.abs(spectrum2.magnitudes - spectrum1.magnitudes).sum() / spectrum1.magnitudes.sum())

            ranks.append(frequency_rank + magnitude_rank)

        return numpy.average(ranks)

    def copy(self, other):
        GenomeBase.copy(self, other)
        other._reference_pcm_audio = self._reference_pcm_audio
        other._reference_spectrum_list = self._reference_spectrum_list
        other._frequency = self._frequency
        other._time_points = self._time_points[:]
        other._amplitudes = self._amplitudes[:]

    def clone(self):
        return copy.copy(self)

    def to_pcm_audio(self):

        sample_count = len(self._reference_pcm_audio.samples)
        sample_duration = self._reference_pcm_audio.duration / sample_count

        oscillator = Oscillator(self._frequency)
        envelope = AmplitudeEnvelope(0)
        for time, amplitude in zip(self._time_points, self._amplitudes):
            envelope.add_point(time * sample_count * sample_duration, amplitude)

        samples = oscillator.get_output(sample_count, sample_duration) * envelope.get_output(sample_count, sample_duration)
        samples = numpy.clip(samples, -self._maximal_amplitude, self._maximal_amplitude)

        return PcmAudio(self._reference_pcm_audio.sampling_rate, list(samples))

    # def __repr__(self):

    #     points = list(zip(self._time_points, self._amplitudes))
    #     points.sort(key=lambda point: point[0])

    #     interval = lambda index: (
    #         points[index + 1][0] - points[index][0],
    #         points[index + 1][1] - points[index][1])

    #     return '\n'.join(
    #         (
    #             "Frequency: %.1f Hz" % self._frequency,
    #             "Attack: %.2f, %f" % interval(0),
    #             "Delay: %.2f, %f" % interval(0),
    #             "Sustain: %.2f, %f" % interval(1),
    #             "Release: %.2f, %f" % interval(2)
    #         ))

    def random_amplitude(self):
        return random.randint(self._minimal_amplitude, self._maximal_amplitude)

    @classmethod
    def random_frequency(cls):
        return random.uniform(cls._minimal_frequency, cls._maximal_frequency)