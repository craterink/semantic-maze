# semantic-maze
Play a maze game in which semantic distances between words indicte which directions you can safely explore 🤓🤔 

Inspired by [Semantle](https://semantle.novalis.org/) & [Cohere](https://cohere.ai/).

## Setup

1. Gather the necessary embeddings (you'll need a Cohere API key) `python -m sem_maze.data.embed_nounlist API_KEY`. This will take ~2 minutes.
2. Play the game: `python -m sem_maze.maze` :) 

## Gameplay

![Gameplay image](img/sem_maze.png?raw=true "Gameplay")

In the example game above, navigate from `woodchuck` to `champion` using the arrow keys -- careful, if you try to step to a word that's too "far away" in semantic embedding space, you lose a life! The `*asterisks*` around a word indicate your location on the map.

The finished game:

![Gameplay image -- Finished Game](img/sem_maze_complete.png?raw=true "Gameplay -- Finished Game")

Each game is random, so play multiple times & have fun!
