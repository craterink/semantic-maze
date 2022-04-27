import cohere
import fire
from tqdm import tqdm
import numpy as np
from sklearn.metrics.pairwise import cosine_distances

NOUNLIST_PATH = 'sem_maze/data/nounlist.txt'
NOUNLIST_EMBEDDINGS_PATH = 'sem_maze/data/nounlist.npy'

def load_nounlist():
    with open(NOUNLIST_PATH) as f:
        nouns = [noun.replace('\n', '') for noun in f.readlines()]
    return nouns

def load_embeddings():
    return np.load(NOUNLIST_EMBEDDINGS_PATH)

def sims_nounlist(output_file: str='sem_maze/data/nounlist_sims'):
    nouns, embeddings = load_nounlist(), load_embeddings()
    assert len(nouns) == len(embeddings), f'There was some issue getting embeddings: {len(nouns)} nouns vs. {len(embeddings)} embeddings.'

    distances = 1 - cosine_distances(embeddings)

    np.save(output_file, distances)

    from sem_maze.semantics.words import generate_close_far_map
    m = generate_close_far_map(nouns, distances)
    breakpoint()

if __name__ == '__main__':
    fire.Fire(sims_nounlist)