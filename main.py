import sys

from pcm_audio import PcmAudio
from synthesis import synthesize


def main():

    if len(sys.argv) < 3:
        sys.exit("Usage: python wavegen.py <input .wav file name> <output .wav file name>")

    _, input_filename, output_filename = sys.argv

    pcm_audio = PcmAudio.from_wave_file(input_filename)
    synthesized_pcm_audio = synthesize(pcm_audio)
    synthesized_pcm_audio.to_wave_file(output_filename)


if __name__ == "__main__":
    main()
