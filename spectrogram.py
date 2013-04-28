from colorsys import hsv_to_rgb
import struct

import numpy
import scipy.fftpack


def spectrum(signal, fft_length=None):

    signal = numpy.array(signal, dtype=numpy.float64)

    if not fft_length:
        fft_length = len(signal)

    fft_result = scipy.fftpack.rfft(signal, fft_length, overwrite_x=True)

    # From the documentation for scipy.fftpack.rfft:
    # The returned real arrays contains:
    # [y(0), Re(y(1)), Im(y(1)), ..., Re(y(n/2))] if n is even

    assert fft_length % 2 == 0, "'fft_length' is not even"

    real_parts = fft_result[1:-1:2]
    imaginary_parts = fft_result[2::2]

    magnitudes = numpy.sqrt(
        numpy.square(real_parts, out=real_parts) +
        numpy.square(imaginary_parts, out=imaginary_parts)
    )
    magnitudes = numpy.concatenate(
        (abs(fft_result[:1]), magnitudes, abs(fft_result[-1:])))

    # Scale magnitudes. This allows to use them as amplitudes of sine waves
    # during the proccess of sound synthesis (now it's used only to calculate
    # the maximal possible amplitude).
    magnitudes /= fft_length / 2
    magnitudes[0] /= 2
    magnitudes[-1] /= 2

    return magnitudes


class Spectrogram(object):

    def __init__(self, signal, frame_size=4096, overlapping_size=2048,
                 fft_length=4096):
        """ This function uses short-time Fourier transform (STFT) to calculate
        a spectrogram of the specified 'signal'. """

        frame_starts = xrange(0, len(signal), frame_size - overlapping_size)

        self.__spectrogram = [
            spectrum(signal[frame_start:frame_start + frame_size], fft_length)
                for frame_start in frame_starts]

        self.__fft_length = fft_length

    def __getitem__(self, key):
        return self.__spectrogram[key]

    def __iter__(self):
        return iter(self.__spectrogram)

    def __len__(self):
        return len(self.__spectrogram)

    def get_frequencies(self, sampling_rate):
        return numpy.linspace(0, 0.5, self.__fft_length / 2 + 1) * sampling_rate

    def to_tga_file(self, filename="out.tga"):

        # TODO: rewrite this

        maximal_magnitude = numpy.max(
            [magnitudes.max() for magnitudes in self.__spectrogram])

        db = lambda value: numpy.log10(value + 1)

        def magnitude_to_color(magnitude):
            r, g, b = hsv_to_rgb(
                max(0, db(magnitude) / db(maximal_magnitude)), 1, 1)
            return int(r * 255), int(g * 255), int(b * 255)

        pixels = [
            [magnitude_to_color(magnitude) for magnitude in magnitudes]
                for magnitudes in self.__spectrogram]

        with open(filename, "wb") as output:

            image_id_field_length = 0
            color_map_type = 0 # No color map
            image_type = 2 # 24-bit, uncompressed, no color map
            x_origin = 0
            y_origin = 0
            width = len(pixels[0])
            height = len(pixels)
            color_depth = 24
            image_descriptor = 0

            header = struct.pack(
                "<BBB5BHHHHBB",
                image_id_field_length, color_map_type, image_type,
                0, 0, 0, 0, 0, x_origin, y_origin, width, height,
                color_depth, image_descriptor)

            output.write(header)

            for row in pixels:
                for pixel in row:
                    output.write(
                        struct.pack("<3B", pixel[0], pixel[1], pixel[2]))
