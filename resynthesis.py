from algorithm import GeneticAlgorithm, Population
from sound import get_sound_factory


def resynthesize(reference_pcm_audio):

    # Frequency: 390.2 Hz
    # Phase: 3.46
    # Amplitude envelope: [(0.027701006219742898, 2602.3552948434503), (0.067593186648
    # 14702, 1844.6025509563485), (0.128719433053636, 1070.337633014105), (0.288116126
    # 97729155, 451.8047113416502), (0.6915564235579005, 68.6864594455799)]
    # Score: 0.80

    algorithm = GeneticAlgorithm()

    pcm_audio = None

    for index in range(4):

        genome_factory = get_sound_factory(reference_pcm_audio, pcm_audio)
        population = Population(genome_factory, 80)
        best_sound = algorithm.run(population)

        print best_sound

        pcm_audio = best_sound.to_pcm_audio()

        pcm_audio.to_wave_file("debug%d.wav" % index)

    return pcm_audio
