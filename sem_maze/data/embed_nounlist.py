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

def load_nounlist():
    with open(NOUNLIST_PATH) as f:
        nouns = [noun.replace('\n', '') for noun in f.readlines()]
    return nouns

def embed_nounlist(api_key : str, embed_method : str='cohere', cohere_model:str='large-20220328', output_file:str='sem_maze/data/nounlist.npy', sims_output_file: str='sem_maze/data/nounlist_sims'):
    assert embed_method == 'cohere'

    nouns = load_nounlist()

    co = cohere.Client(api_key)

    batch_size = 128
    all_embeddings = []
    for i in tqdm(range((len(nouns) // batch_size) + 1)):
        batch_nouns = nouns[batch_size*i:batch_size*(i+1)]
        batch_embeddings = co.embed(model=cohere_model, texts=batch_nouns)
        all_embeddings.extend(batch_embeddings.embeddings)
    embeddings_array = np.stack(all_embeddings)

    np.save(output_file, embeddings_array)

    # also compute similarities 
    sims = 1 - cosine_distances(embeddings_array)
    np.save(sims_output_file, sims)

if __name__ == '__main__':
    fire.Fire(embed_nounlist)