import contextlib
import struct
import wave


class PcmAudio:

    def __init__(self, sampling_rate, samples):

        self.__sampling_rate = sampling_rate
        self.__samples = samples

    @staticmethod
    def from_wave_file(filename):

        with contextlib.closing(wave.open(filename, "rb")) as wave_file:

            assert wave_file.getnchannels() == 1, "Only mono wave files are supported"

            bytes_per_sample = wave_file.getsampwidth()
            sampling_rate = wave_file.getframerate()
            frames_count = wave_file.getnframes()

            sample_data = wave_file.readframes(frames_count)

        sample_count = len(sample_data) / bytes_per_sample

        if bytes_per_sample == 1:
            sample_format = "B"
        elif bytes_per_sample == 2:
            sample_format = "h"
        elif bytes_per_sample == 4:
            sample_format = "i"

        samples = struct.unpack("<%d%s" % (sample_count, sample_format), sample_data)

        return PcmAudio(sampling_rate, samples)

    def to_wave_file(self, filename):

        with contextlib.closing(wave.open(filename, "wb")) as wave_file:

            wave_file.setnchannels(1)
            wave_file.setframerate(self.__sampling_rate)
            wave_file.setsampwidth(2)
            wave_file.writeframes(struct.pack("<%dh" % len(self.__samples), *self.__samples))

    @property
    def sampling_rate(self):
        return self.__sampling_rate

    @property
    def samples(self):
        return self.__samples

    @property
    def duration(self):
        return len(self.__samples) / float(self.__sampling_rate)
