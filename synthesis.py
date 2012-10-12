import numpy
import scipy.fftpack

from genetic_algorithm import GeneticAlgorithm
from ga_sound import Sound


class Spectrum:

    def __init__(self, samples, window_size):

        amplitudes = scipy.fftpack.fft(numpy.array(samples), window_size)

        # Exclude 0 Hz frequency and truncate (due to the Nyquist theorem?)
        amplitudes = amplitudes[1:window_size / 2 + 1]

        self._magnitudes = numpy.abs(amplitudes)

    @property
    def magnitudes(self):
        return self._magnitudes


def synthesize(reference_pcm_audio):


    def spectrum_list(pcm_audio, window_size=4096):

        window_count = len(pcm_audio.samples) / window_size
        window = lambda index: \
            pcm_audio.samples[index * window_size : (index + 1) * window_size]

        return [Spectrum(window(index), window_size)
            for index in range(window_count)]


    reference_spectrum_list = spectrum_list(reference_pcm_audio)


    class SynthesisAlgorithm(GeneticAlgorithm):

        @staticmethod
        def _fit(sound):

            generated_pcm_audio = sound.to_pcm_audio(reference_pcm_audio)
            generated_spectrum_list = spectrum_list(generated_pcm_audio)

            ranks = []
            antiranks = []

            for spectrum1, spectrum2 in zip(
                    reference_spectrum_list, generated_spectrum_list):
                
                spectral_similarity = (spectrum1.magnitudes * spectrum2.magnitudes).sum()
                magnitude_difference = (numpy.clip(spectrum2.magnitudes - spectrum1.magnitudes, 0, float("inf"))**2).sum()

                if spectral_similarity > magnitude_difference:
                    rank = spectral_similarity / (magnitude_difference + 1)
                else:
                    rank = 1
                    antiranks.append(magnitude_difference / (spectral_similarity + 1))
                
                ranks.append(rank)

            return numpy.average(numpy.array(ranks)) / numpy.average(numpy.array(antiranks))

        @staticmethod
        def _spawn():
            return Sound.spawn()

        @staticmethod
        def _cross(first_sound, second_sound):
            return first_sound.cross(second_sound)

        @staticmethod
        def _mutate(sound):
            return sound.mutate()

    best = SynthesisAlgorithm()()

    return best.to_pcm_audio(reference_pcm_audio)
