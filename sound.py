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

    __windows = {}

    def __init__(self, samples):
        """ Note: this function modifies the contents of 'samples' """
        self.__apply_window_function(samples)
        fft_result = scipy.fftpack.rfft(samples, overwrite_x=True)
        self.__magnitudes = numpy.abs(fft_result, out=fft_result)

    @classmethod
    def __apply_window_function(cls, samples):
        length = len(samples)
        window = cls.__windows.get(length)
        if window is None:
            window = cls.__windows[length] = numpy.hanning(length)
        samples *= window

    @property
    def magnitudes(self):
        return self.__magnitudes


def _generate_frames_spectrums(
        pcm_audio, frame_size=4096, overlapping_size=2048):

    sample_count = len(pcm_audio.samples)

    frame_count = int(numpy.floor(
        (sample_count - frame_size) / (frame_size - overlapping_size)) + 1)

    def frame(index):
        start_sample_index = index * (frame_size - overlapping_size)
        return numpy.array(pcm_audio.samples[
            start_sample_index : start_sample_index + frame_size])

    return [Spectrum(frame(index)) for index in xrange(frame_count)]


class _Sound(Genome):

    _minimal_frequency = 20
    _maximal_frequency = 4200

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

        if random.random() <= rate:
            self._frequency = self.random_frequency()
            mutated = True

        if random.random() <= rate:
            self._phase = self.random_phase()
            mutated = True

        for point in self._amplitude_envelope_points:

            if random.random() <= rate:
                point.time = self.random_time()
                mutated = True

            if random.random() <= rate:
                point.value = self.random_amplitude()
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

        first_child._amplitude_envelope_points = []
        second_child._amplitude_envelope_points = []

        for self_point, other_point in zip(
                self._amplitude_envelope_points,
                other._amplitude_envelope_points):

            first_time, second_time = child_value_pair(
                self_point.time, other_point.time)

            first_amplitude, second_amplitude = child_value_pair(
                self_point.value, other_point.value)

            first_child._amplitude_envelope_points.append(
                Envelope.Point(first_time, first_amplitude))
            second_child._amplitude_envelope_points.append(
                Envelope.Point(second_time, second_amplitude))

        return first_child, second_child

    def evaluate(self):

        generated_frames_spectrums =\
            _generate_frames_spectrums(self.to_pcm_audio())

        ranks = []

        for spectrum1, spectrum2 in zip(
                self._reference_frames_spectrums, generated_frames_spectrums):

            # Remove unaudible frequencies
            frequency_step = (self._reference_pcm_audio.sampling_rate * 0.5 /
                len(spectrum1.magnitudes))
            lower_bound =\
                int(numpy.ceil(self._minimal_frequency / frequency_step))
            magnitudes1 = spectrum1.magnitudes[lower_bound:]
            magnitudes2 = spectrum2.magnitudes[lower_bound:]

            squared = magnitudes1 * magnitudes1

            frequency_rank = numpy.minimum(
                magnitudes1 * magnitudes2, squared).sum() / squared.sum()

            magnitude_rank = 1 / (1 +
                numpy.abs(magnitudes2 - magnitudes1).sum() / magnitudes1.sum())

            ranks.append((frequency_rank + magnitude_rank) / 2)

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

    @classmethod
    def random_time(cls):
        return random.uniform(0, cls._reference_pcm_audio.duration)

    @classmethod
    def random_amplitude(cls):
        return random.randint(0, cls._maximal_amplitude)

    @classmethod
    def random_frequency(cls):
        return random.uniform(cls._minimal_frequency, cls._maximal_frequency)

    @staticmethod
    def random_phase():
        return random.uniform(0, 2 * numpy.pi)


def get_sound_factory(reference_pcm_audio, base_pcm_audio=None):

    class Sound(_Sound):

        _reference_pcm_audio = reference_pcm_audio
        _reference_frames_spectrums =\
            _generate_frames_spectrums(reference_pcm_audio)
        _base_pcm_audio = base_pcm_audio
        _maximal_amplitude = numpy.abs(reference_pcm_audio.samples).max()

    return Sound
