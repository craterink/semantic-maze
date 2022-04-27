import cohere
import fire
from tqdm import tqdm
import numpy as np

NOUNLIST_PATH = 'sem_maze/data/nounlist.txt'

def load_nounlist():
    with open(NOUNLIST_PATH) as f:
        nouns = [noun.replace('\n', '') for noun in f.readlines()]
    return nouns

def embed_nounlist(api_key : str, embed_method : str='cohere', cohere_model:str='large-20220328', output_file:str='sem_maze/data/nounlist.npy'):
    assert embed_method == 'cohere'

    nouns = load_nounlist()

    co = cohere.Client(api_key)

    batch_size = 128
    all_embeddings = []
    for i in tqdm(range((len(nouns) // batch_size) + 1)):
        batch_nouns = nouns[batch_size*i:batch_size*(i+1)]
        batch_embeddings = co.embed(model='large', texts=batch_nouns)
        all_embeddings.extend(batch_embeddings.embeddings)
    embeddings_array = np.stack(all_embeddings)

    np.save(output_file, embeddings_array)

if __name__ == '__main__':
    fire.Fire(embed_nounlist)