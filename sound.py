import random

import numpy

from algorithm import Genome
from envelope import Envelope
from oscillator import Oscillator
from pcm_audio import PcmAudio
from spectrogram import Spectrogram


class _Sound(Genome):

    _minimal_frequency = 20
    _maximal_frequency = 20000

    _point_count = 5

    def __init__(self):

        Genome.__init__(self)

        self._frequency = self.random_frequency()
        self._phase = self.random_phase()

        self._amplitude_envelope_points = [
            Envelope.Point(time=self.random_time(),
                           value=self.random_amplitude())
            for _ in xrange(self._point_count)
        ]

    def mutate(self, rate):

        mutated = False

        def mutated_value(value, minimal_value, maximal_value):
            """ The gaussian mutation operator. """
            return numpy.clip(
                random.normalvariate(
                    value, (maximal_value - minimal_value) * 0.5),
                minimal_value,
                maximal_value)

        if random.random() <= rate:
            self._frequency = mutated_value(
                self._frequency,
                self._minimal_frequency,
                self._maximal_frequency)
            mutated = True

        if random.random() <= rate:
            self._phase = mutated_value(self._phase, 0, 2 * numpy.pi)
            mutated = True

        for point in self._amplitude_envelope_points:
            if random.random() <= rate:
                point.time = mutated_value(
                    point.time, 0, self._reference_pcm_audio.duration)
                point.value = mutated_value(
                    point.value, 0, self._maximal_amplitude)
                mutated = True

        return mutated

    def cross(self, other):

        child_factory = type(self)
        first_child, second_child = child_factory(), child_factory()

        def child_value_pair(
                first_parent_value, second_parent_value,
                minimal_value, maximal_value):

            mean = (first_parent_value + second_parent_value) / 2
            standard_deviation = abs(first_parent_value - mean)

            first_child_value = numpy.clip(
                random.normalvariate(mean, standard_deviation),
                minimal_value,
                maximal_value)

            second_child_value = numpy.clip(
                random.normalvariate(mean, standard_deviation),
                minimal_value,
                maximal_value)

            return first_child_value, second_child_value

        first_child._frequency, second_child._frequency = child_value_pair(
            self._frequency, other._frequency,
            self._minimal_frequency, self._maximal_frequency)

        first_child._phase, second_child._phase = child_value_pair(
            self._phase, other._phase, 0, 2 * numpy.pi)

        self._sort_amplitude_envelope_points()
        other._sort_amplitude_envelope_points()

        first_child._amplitude_envelope_points = []
        second_child._amplitude_envelope_points = []

        for self_point, other_point in zip(
                self._amplitude_envelope_points,
                other._amplitude_envelope_points):

            first_time, second_time = child_value_pair(
                self_point.time, other_point.time,
                0, self._reference_pcm_audio.duration)

            first_amplitude, second_amplitude = child_value_pair(
                self_point.value, other_point.value, 0, self._maximal_amplitude)

            first_child._amplitude_envelope_points.append(
                Envelope.Point(first_time, first_amplitude))
            second_child._amplitude_envelope_points.append(
                Envelope.Point(second_time, second_amplitude))

        return first_child, second_child

    def evaluate(self):

        spectrogram = Spectrogram(self.to_pcm_audio().samples)

        ranks = []

        for magnitudes1, magnitudes2 in zip(
                self._reference_spectrogram, spectrogram):

            differences = magnitudes2 - magnitudes1

            # The result is computed using the following formula:
            # rank = sum(differences**2) / sum(magnitudes1**2)

            rank = (
                numpy.dot(differences, differences) /
                numpy.dot(magnitudes1, magnitudes1)
            )

            ranks.append(rank)

        return -numpy.mean(ranks)

    def to_pcm_audio(self):

        oscillator = Oscillator(self._frequency, self._phase)
        envelope = Envelope()
        for point in self._amplitude_envelope_points:
            envelope.add_point(point)

        samples = oscillator.get_output(self._sample_times)
        samples *= envelope.get_output(self._sample_times)

        if self._base_pcm_audio:
            samples += self._base_pcm_audio.samples

        return PcmAudio(self._reference_pcm_audio.sampling_rate, samples)

    def _sort_amplitude_envelope_points(self):
        self._amplitude_envelope_points.sort(key=lambda point: point.time)

    def __repr__(self):

        self._sort_amplitude_envelope_points()

        return '\n'.join(
            (
                "Score: %.2f" % self.score,
                "Frequency: %.1f Hz" % self._frequency,
                "Phase: %.2f" % self._phase,
                "Amplitude envelope: %s" % str(self._amplitude_envelope_points)
            ))

    @classmethod
    def random_time(cls):
        return random.uniform(0, cls._reference_pcm_audio.duration)

    @classmethod
    def random_amplitude(cls):
        return random.uniform(0, cls._maximal_amplitude)

    @classmethod
    def random_frequency(cls):
        return random.uniform(cls._minimal_frequency, cls._maximal_frequency)

    @staticmethod
    def random_phase():
        return random.uniform(0, 2 * numpy.pi)


def get_sound_factory(reference_pcm_audio, base_pcm_audio=None):

    class Sound(_Sound):

        _reference_pcm_audio = reference_pcm_audio
        _reference_spectrogram = Spectrogram(reference_pcm_audio.samples)
        _base_pcm_audio = base_pcm_audio
        _maximal_amplitude = numpy.max(
            [magnitudes.max() for magnitudes in _reference_spectrogram])

        _sample_times = numpy.linspace(
            0, reference_pcm_audio.duration, len(reference_pcm_audio.samples))

    return Sound
