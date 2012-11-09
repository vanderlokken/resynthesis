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


class _Sound(Genome):

    _minimal_frequency = 40
    _maximal_frequency = 4200

    _point_count = 5
    
    def __init__(self):

        Genome.__init__(self)

        self._frequency = self.random_frequency()
        self._phase = self.random_phase()

        random_point = lambda: Envelope.Point(
            time=self.random_time(), value=self.random_amplitude())

        self._amplitude_envelope_points = [
            random_point() for _ in xrange(self._point_count)]

    def mutate(self, rate):

        mutated = False

        if random.random() <= rate:
            self._frequency = self.random_frequency()
            mutated = True

        if random.random() <= rate:
            self._phase = self.random_phase()
            mutated = True

        # A simple alias
        points = self._amplitude_envelope_points

        for index in xrange(self._point_count):

            if random.random() <= rate:
                points[index] = points[index]._replace(time=self.random_time())
                mutated = True

            if random.random() <= rate:
                points[index] = points[index]._replace(
                    value=self.random_amplitude())
                mutated = True

        return mutated

    def cross(self, other):

        child_factory = type(self)
        first_child, second_child = child_factory(), child_factory()

        def child_value_pair(first_parent_value, second_parent_value):
            first_child_value = random.uniform(
                first_parent_value, second_parent_value)
            second_child_value = \
                first_parent_value + second_parent_value - first_child_value
            return first_child_value, second_child_value

        first_child._frequency, second_child._frequency = child_value_pair(
            self._frequency, other._frequency)
        first_child._phase, second_child._phase = child_value_pair(
            self._phase, other._phase)

        self._amplitude_envelope_points.sort(key=lambda point: point.time)
        other._amplitude_envelope_points.sort(key=lambda point: point.time)

        for index in xrange(self._point_count):

            first_time, second_time = child_value_pair(
                self._amplitude_envelope_points[index].time,
                other._amplitude_envelope_points[index].time)

            first_amplitude, second_amplitude = child_value_pair(
                self._amplitude_envelope_points[index].value,
                other._amplitude_envelope_points[index].value)

            first_child._amplitude_envelope_points[index] = Envelope.Point(
                first_time, first_amplitude)
            second_child._amplitude_envelope_points[index] = Envelope.Point(
                second_time, second_amplitude)

        return first_child, second_child

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
        for point in self._amplitude_envelope_points:
            envelope.add_point(point)

        samples = oscillator.get_output(sample_count, sample_duration)
        samples *= envelope.get_output(sample_count, sample_duration)

        if self._base_pcm_audio:
            samples += self._base_pcm_audio.samples

        return PcmAudio(self._reference_pcm_audio.sampling_rate, samples)

    def __repr__(self):

        self._amplitude_envelope_points.sort(key=lambda point: point.time)

        return '\n'.join(
            (
                "Score: %.2f" % self.score,
                "Frequency: %.1f Hz" % self._frequency,
                "Phase: %.2f" % self._phase,
                "Amplitude envelope: %s" % str(self._amplitude_envelope_points)
            ))

    def random_time(self):
        return random.random() * self._reference_pcm_audio.duration

    def random_amplitude(self):
        return random.randint(0, self._maximal_amplitude)

    @classmethod
    def random_frequency(cls):
        return random.uniform(cls._minimal_frequency, cls._maximal_frequency)

    @staticmethod
    def random_phase():
        return random.uniform(0, 2 * numpy.pi)


def get_sound_factory(reference_pcm_audio, base_pcm_audio=None):

    class Sound(_Sound):

        _reference_pcm_audio = reference_pcm_audio
        _reference_spectrum_list = _generate_spectrum_list(reference_pcm_audio)
        _base_pcm_audio = base_pcm_audio
        _maximal_amplitude = numpy.abs(reference_pcm_audio.samples).max()

    return Sound
