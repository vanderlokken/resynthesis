from algorithm import GeneticAlgorithm, Population
from sound import get_sound_factory


def resynthesize(reference_pcm_audio):

    # Frequency: 390.2 Hz
    # Phase: 3.18
    # Amplitude envelope: [(0.05494893182272953, 1225.3010040521226), (0.0978622683442
    # 7864, 1697.3921809393846), (0.1860495274287318, 930.2889125564799), (0.288980495
    # 3603544, 431.5297860228603), (0.567903772948726, 120.7427716562857)]
    # Rank: 0.79

    algorithm = GeneticAlgorithm()

    pcm_audio = None

    for index in range(4):

        genome_factory = get_sound_factory(reference_pcm_audio, pcm_audio)
        population = Population(genome_factory, 80)
        best_sound = algorithm.run(population)

        print best_sound
        print "Score: %.2f" % best_sound.score

        pcm_audio = best_sound.to_pcm_audio()

        pcm_audio.to_wave_file("debug%d.wav" % index)

    return pcm_audio
