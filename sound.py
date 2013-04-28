import random

import numpy

from algorithm import Genome
from envelope import Envelope
from oscillator import Oscillator
from pcm_audio import PcmAudio
from spectrogram import Spectrogram


def wrap_around(value, minimal_value, maximal_value):
    """ This function wraps around a value if it is out of boundaries """
    if value < minimal_value:
        value = 2 * minimal_value - value
    if value > maximal_value:
        value = 2 * maximal_value - value
    return value


class _Sound(Genome):

    _minimal_frequency = 40
    _maximal_frequency = 20000

    _point_count = 5

    def __init__(self):

        Genome.__init__(self)

        self._frequency = self.random_frequency()
        self._phase = self.random_phase()

        self._amplitude_envelope_points = [
            self.random_amplitude_envelope_point()
            for _ in xrange(self._point_count)
        ]

    def mutate(self, rate):

        mutated = False

        def mutated_value(value, minimal_value, maximal_value):
            """ The gaussian mutation operator. """
            return wrap_around(
                random.normalvariate(
                    value, (maximal_value - minimal_value) * (0.2 + rate)),
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
                    point.value, 0,
                    self._amplitude_limit_envelope.get_output(point.time))
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

            first_child_value = wrap_around(
                random.normalvariate(mean, standard_deviation),
                minimal_value,
                maximal_value)

            second_child_value = wrap_around(
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

            first_amplitude = numpy.clip(
                first_amplitude, 0,
                self._amplitude_limit_envelope.get_output(first_time))

            second_amplitude = numpy.clip(
                second_amplitude, 0,
                self._amplitude_limit_envelope.get_output(second_time))

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
            # rank = sum(weights * differences**2)

            rank = numpy.dot(
                differences, differences * self._frequencies_weights)
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
    def random_amplitude_envelope_point(cls):
        time = random.uniform(
            0, cls._reference_pcm_audio.duration)
        value = random.uniform(
            0, cls._amplitude_limit_envelope.get_output(time))
        return Envelope.Point(time, value)

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

    base_sound_spectrogram = (
        Spectrogram(base_pcm_audio.samples) if base_pcm_audio else None)

    # Compute and overwrite maximal frequency

    minimal_significant_amplitude = 20.0

    significant_frequency_indices = [
        index for index, amplitudes in enumerate(
            zip(*Sound._reference_spectrogram))
        if numpy.max(amplitudes) >= minimal_significant_amplitude]

    maximal_frequency_index = numpy.max(significant_frequency_indices)

    Sound._maximal_frequency = Sound._reference_spectrogram.get_frequencies(
        Sound._reference_pcm_audio.sampling_rate)[maximal_frequency_index]

    # Compute and overwrite minimal frequency

    # if base_pcm_audio:

    #     significant_base_frequency_indices = [
    #         index for index, amplitudes in enumerate(
    #             zip(*base_sound_spectrogram))
    #         if numpy.max(amplitudes) >= minimal_significant_amplitude]

    #     minimal_frequency_index = numpy.min([
    #         index for index in significant_frequency_indices
    #         if index not in significant_base_frequency_indices])

    #     Sound._minimal_frequency = base_sound_spectrogram.get_frequencies(
    #         base_pcm_audio.sampling_rate)[minimal_frequency_index]
    #     print Sound._minimal_frequency

    # Compute amplitude limit envelope

    envelope = Envelope()

    frame_length = (
        Sound._reference_pcm_audio.duration / len(Sound._reference_spectrogram))

    for frame_index, magnitudes in enumerate(Sound._reference_spectrogram):
        if base_sound_spectrogram:
            magnitudes = magnitudes - base_sound_spectrogram[frame_index]
        envelope.add_point(
            Envelope.Point(
                time=frame_length * (frame_index + 0.5),
                value=numpy.max(magnitudes)
            )
        )

    Sound._amplitude_limit_envelope = envelope

    # Compute weights by frequencies

    def weight_by_frequency(frequency):
        """ To calculate weights this function uses a technique called
        "A-weighting" """
        return (12200 ** 2) * (frequency ** 4) / (
            (frequency ** 2 + 20.6 ** 2) *
            numpy.sqrt(frequency ** 2 + 107.7 ** 2) *
            numpy.sqrt(frequency ** 2 + 737.9 ** 2) *
            (frequency ** 2 + 12200 ** 2)
        )

    Sound._frequencies_weights = numpy.array(
        map(weight_by_frequency, Sound._reference_spectrogram.get_frequencies(
            Sound._reference_pcm_audio.sampling_rate)))

    return Sound
