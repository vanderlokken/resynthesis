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
        self.magnitudes = numpy.abs(fft_result, out=fft_result)

    @classmethod
    def __apply_window_function(cls, samples):
        length = len(samples)
        window = cls.__windows.get(length)
        if window is None:
            window = cls.__windows[length] = numpy.hanning(length)
        samples *= window


def _generate_frames_spectrums(
        pcm_audio, frame_size=4096, overlapping_size=2048,
        minimal_frequency=20):

    sample_count = len(pcm_audio.samples)
    frame_count = int(numpy.floor(
        (sample_count - frame_size) / (frame_size - overlapping_size)) + 1)

    frames_spectrums = []

    for frame_index in xrange(frame_count):

        sample_index = frame_index * (frame_size - overlapping_size)
        samples = numpy.array(
            pcm_audio.samples[sample_index : sample_index + frame_size])
        spectrum = Spectrum(samples)
        frames_spectrums.append(spectrum)

        # Remove unaudible frequencies
        frequency_step = (
            pcm_audio.sampling_rate * 0.5 / len(spectrum.magnitudes))
        lower_bound = int(numpy.ceil(minimal_frequency / frequency_step))
        spectrum.magnitudes = spectrum.magnitudes[lower_bound:]

    return frames_spectrums


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
            self._frequency = random.uniform(
                self._frequency, self.random_frequency())
            mutated = True

        if random.random() <= rate:
            self._phase = random.uniform(self._phase, self.random_phase())
            mutated = True

        for point in self._amplitude_envelope_points:
            if random.random() <= rate:
                point.time = random.uniform(point.time, self.random_time())
                point.value = random.uniform(
                    point.value, self.random_amplitude())
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

            first_child_value = random.normalvariate(mean, standard_deviation)
            second_child_value = random.normalvariate(mean, standard_deviation)

            first_child_value = max(first_child_value, minimal_value)
            second_child_value = max(second_child_value, minimal_value)

            first_child_value = min(first_child_value, maximal_value)
            second_child_value = min(second_child_value, maximal_value)

            return first_child_value, second_child_value

        first_child._frequency, second_child._frequency = child_value_pair(
            self._frequency, other._frequency,
            self._minimal_frequency, self._maximal_frequency)

        first_child._phase, second_child._phase = child_value_pair(
            self._phase, other._phase, 0, 2 * numpy.pi)

        self._amplitude_envelope_points.sort(key=lambda point: point.time)
        other._amplitude_envelope_points.sort(key=lambda point: point.time)

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

        generated_frames_spectrums =\
            _generate_frames_spectrums(self.to_pcm_audio())

        ranks = []

        for spectrum1, spectrum2 in zip(
                self._reference_frames_spectrums, generated_frames_spectrums):

            magnitudes1 = spectrum1.magnitudes
            magnitudes2 = spectrum2.magnitudes

            array = magnitudes2 - magnitudes1
            array = numpy.square(array, out=array)
            x = array.sum()

            array = numpy.square(magnitudes1, out=array)
            y = array.sum()

            ranks.append(x / y)

        return -numpy.mean(ranks)

    def to_pcm_audio(self):

        oscillator = Oscillator(self._frequency, self._phase)
        envelope = Envelope(0)
        for point in self._amplitude_envelope_points:
            envelope.add_point(point)

        samples = oscillator.get_output(self._sample_times)
        samples *= envelope.get_output(self._sample_times)

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

        _sample_times = numpy.linspace(
            0, reference_pcm_audio.duration, len(reference_pcm_audio.samples))

    return Sound
