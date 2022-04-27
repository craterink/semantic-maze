from fileinput import close
from tkinter import W
import numpy as np
import fire
from tqdm import tqdm
import time
import random
import itertools

import matplotlib.pyplot as plt

from sem_maze.data.sims_nounlist import load_nounlist

NOUNLIST_SIMS_PATH = 'sem_maze/data/nounlist_sims.npy'

def load_noun_similarities_matrix():
    return np.load(NOUNLIST_SIMS_PATH)


def generate_sim_map(nouns=load_nounlist(), sims=load_noun_similarities_matrix(), max_wordlen_chars=16):
    return { noun: {
        j_noun: s for j_noun, s in zip(nouns, sims[idx]) if len(j_noun) <= max_wordlen_chars
    } for idx, noun in enumerate(nouns) if len(noun) <= max_wordlen_chars }

def generate_close_far_map(nouns=load_nounlist(), sims=load_noun_similarities_matrix(), close_threshold=0.7, far_threshold=0.3, min_close=0, min_far = 0, max_wordlen_chars=7):
    sim_map = {}
    close_counts, far_counts = [], []
    
    for noun, noun_sims in zip(nouns, sims):
        close = [n for n, s in zip(nouns, noun_sims) if s > close_threshold]
        far =  [n for n, s in zip(nouns, noun_sims) if s < far_threshold]

        if len(close) < min_close or len(far) < min_far or len(noun) > max_wordlen_chars: 
            continue

        sim_map[noun] = {
            'close' : close,
            'far' : far
        }
        close_counts.append(len(close))
        far_counts.append(len(far))
    return sim_map, close_counts, far_counts

def choose_word_constrained(sim_map, close_words, far_words, do_not_use=[], constrain_margin=0.2):
    # i.e. must be close to close_words and far from far_words

    # if no constraints given, return a random word 
    if not close_words and not far_words:
        return random.choice(list(set(sim_map.keys()).difference(do_not_use))), []

    c_f_combos = list(itertools.product(close_words, far_words))

    scores = []
    nouns = list(sim_map.keys())
    for noun in nouns:
        # only search candidate words
        if noun in do_not_use:
            scores.append(-100)
            continue
        
        # apply constraint: for all pairs (c, f) in combinations(close_words, far_words)
        # assure that sim(noun, c) > sim(noun, f) by some margin M
        constraint_hit = False
        for c, f in c_f_combos:
            if sim_map[noun][c] - sim_map[noun][f] < constrain_margin:
                scores.append(-100)
                constraint_hit = True
                break
        if constraint_hit:
            continue

        # find argmax scores
        # want argmax_{w in words}{sum_over_close{sim(w, c)} - sum_over_far{sim(w, f)}}
        scores.append(sum(sim_map[noun][c] for c in close_words) - sum(sim_map[noun][f] for f in far_words))

    scores = np.array(scores)
    assert sum(scores > -100) >= 3, 'less than 3 qualifying words remain!!'

    # choose one of the best 3 words
    # search_n = min(5, sum(scores > -100)) # option to make this more configurable
    best_idxs = np.argsort(-scores)[:3]
    best_word = nouns[random.choice(best_idxs)] 
    candidates = [n for idx, n in enumerate(nouns) if idx in best_idxs]
    return best_word, candidates

    


    # options = list(set(sim_map.keys()).difference(do_not_use))
    # if close_words:
    #     pass
    # else:
    #     close_candidates = list(sim_map.keys())
    
    # if far_words:
    #     pass
    # else:
    #     far_candidates = list(sim_map.keys())

    # try:
    #     remaining_choices = remaining_choices.intersection(close_candidates)
    #     remaining_choices = remaining_choices.intersection(all_far)
    #     remaining_choices = remaining_choices.difference(do_not_use)
    # except Exception as ex:
    #     breakpoint()

    # return np.random.choice(list(remaining_choices))


def analyze_word_map():
    nouns, sims = load_nounlist(), load_noun_similarities_matrix()

    m, _, _ = generate_close_far_map(nouns, sims)
    print(f'Number of nouns remaining: {len(m.values())}')

    # investigate far thresholds
    far_thresholds = np.linspace(0, 0.3, 10)
    medians = []
    for i, th in tqdm(enumerate(far_thresholds), total=len(far_thresholds)):
        _, _, far_ct = generate_close_far_map(nouns, sims, far_threshold=th)
        medians.append(np.median(far_ct))
    
    plt.plot(far_thresholds, medians)
    plt.show()

    # investigate close thresholds
    close_thresholds = np.linspace(0.3, 1, 10)
    medians = []
    for i, th in tqdm(enumerate(close_thresholds), total=len(close_thresholds)):
        _, close_ct, _ = generate_close_far_map(nouns, sims, close_threshold=th)
        medians.append(np.median(close_ct))
    
    plt.plot(close_thresholds, medians)
    plt.show()


def anlayze_distances():
    nouns, sims = load_nounlist(), load_noun_similarities_matrix()

    # for a given noun, print its 5 most similar nouns
    for idx,noun in enumerate(nouns):
        # if not noun == 'bike':
        #     continue
        most_sim = np.argsort(-sims[idx])[1:15]
        most_sim_nouns = [nouns[i] for i in most_sim]
        print(f'5 nouns most similar to "{noun}": {", ".join(most_sim_nouns)}')
        time.sleep(0.6)


if __name__ == '__main__':
    fire.Fire(anlayze_distances)
    # fire.Fire(analyze_word_map)