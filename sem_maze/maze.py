from sem_maze.semantics.words import choose_word_constrained, generate_sim_map
import fire
import curses
import time

def write_maze(stdscr, maze, known_paths, known_walls, current_spot=None, explore_queue=[], last_candidates=[], close_words=[], far_words=[], lives=None):
    col_width = 18

    def get_color(row_i, col_i):
        if (row_i, col_i) in known_paths:
            return 1 
        elif (row_i, col_i) in known_walls:
            return 2 
        else:
            return 0
    def maybe_indicate_current(row_i, col_i, c): 
        return_str = f'*{c}*' if ((row_i, col_i) == current_spot) else c
        filled = return_str + (col_width - len(return_str))*' '
        return filled

    for row_i, row in enumerate(maze):
        for col_i, c in enumerate(row):
            stdscr.addstr(row_i, col_i*col_width, maybe_indicate_current(row_i, col_i, c), curses.color_pair(get_color(row_i, col_i)))
    if lives is None:
        stdscr.addstr(row_i + 1, 0, 'Close words: ' + ','.join(close_words) + '                                                   ')
        stdscr.addstr(row_i + 2, 0, 'Far words: ' + ','.join(far_words) + '                                                       ')
        stdscr.addstr(row_i + 3, 0, 'Last candidates: ' + ','.join(last_candidates) + '                                           ')
    else:
        stdscr.addstr(row_i + 1, 0, f'Lives: {lives}', curses.color_pair(3))
    stdscr.refresh()

def generate_maze(nrows, ncols):
    from mazelib import Maze
    from mazelib.generate.Prims import Prims

    m = Maze()
    m.generator = Prims(nrows, ncols)
    m.generate()
    m.generate_entrances()
    return m

def sort_explore_stack(explore_stack, maze):
    wall_indicator = lambda cell: 0 if maze[cell[0]][cell[1]] == '#' else 1
    explore_stack.sort(key=wall_indicator)


def fill_in_next_word(maze, noun_map, explore_stack, explored, used_nouns):
    # pop from stack
    nxt = explore_stack.pop()
    nxt_type = 'wall' if maze[nxt[0]][nxt[1]] == '#' else 'path'

    # need to fill NXT with a word satisfying nearby constraints
    # find all neighbors of NXT
    nxt_neighbors = nearby(nxt, len(maze), len(maze[0]))
    # some may be "wall constraints," i.e. must be far
    if nxt_type == 'path':
        far_neighbors = [explored[n]['noun'] for n in nxt_neighbors if n in explored and explored[n]['type'] == 'wall']
        close_neighbors = [explored[n]['noun'] for n in nxt_neighbors if n in explored and explored[n]['type'] == 'path']
    if nxt_type == 'wall': # note we don't actually care about wall-to-wall distances, only wall-to-path
        far_neighbors = [explored[n]['noun'] for n in nxt_neighbors if n in explored and explored[n]['type'] == 'path']
        close_neighbors = [] 

    # choose a word for NXT according to close/far constraints
    nxt_noun, candidates = choose_word_constrained(noun_map, close_words=close_neighbors, far_words=far_neighbors, do_not_use=used_nouns)

    # update the maze
    maze[nxt[0]][nxt[1]] = nxt_noun

    # update our data structures
    used_nouns.append(nxt_noun)
    explored[nxt] = {
        'type' : nxt_type,
        'noun' : nxt_noun
    }
    for n in nxt_neighbors:
        if n not in explored and n not in explore_stack:
            explore_stack.append(n)
    sort_explore_stack(explore_stack, maze) 

    return candidates, close_neighbors, far_neighbors

def nearby(cell, nrows, ncols, directions=False):
    i, j = cell
    adjacent = [
        (i + 1, j) if i + 1 < nrows else None,
        (i - 1, j) if i - 1 >= 0 else None,
        (i, j + 1) if j + 1 < ncols else None,
        (i, j - 1) if j - 1 >= 0 else None,
    ]
    if directions:
        return {direc : cell for direc, cell in zip('durl', adjacent)}
    else:
        return list(filter(lambda c : c is not None, adjacent))


def unexplored(cells, explored):
    return list(filter(lambda c: c not in explored, cells))

def main(nrows=8, ncols=4, see_creation=False):
    print('Loading maze...')
    maze = generate_maze(nrows, ncols)
    start, end = maze.start, maze.end
    maze = [[c for c in s] for s in maze.tostring().split('\n')]
    nrows, ncols = len(maze), len(maze[0])
    maze[start[0]][start[1]] = 'S'
    maze[end[0]][end[1]] = 'F'
    orig_maze = maze.copy()
    known_paths = [start, end]
    known_walls = []
    current_spot = start
    explore_queue = [start] 
    explored = {}
    used_nouns = []
    last_candidates, close_words, far_words = [], [], []

    print('Loading noun map...')
    noun_map = generate_sim_map()
    print(f'Num of nouns: {len(noun_map)}')

    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(1)

    lives = 3

    try:
        # CREATE MAZE ~
        while explore_queue:
            if see_creation:
                known_paths = [cell for cell, data in explored.items() if data['type'] == 'path']
                known_walls = [cell for cell, data in explored.items() if data['type'] == 'wall']
                write_maze(stdscr, maze, known_paths, known_walls, current_spot, explore_queue, last_candidates, close_words, far_words)
            last_candidates, close_words, far_words = fill_in_next_word(maze, noun_map, explore_queue, explored, used_nouns)
            if see_creation:
                time.sleep(0.03)
        
        # END OF CREATION
        if see_creation:
            known_paths = [cell for cell, data in explored.items() if data['type'] == 'path']
            known_walls = [cell for cell, data in explored.items() if data['type'] == 'wall']
            write_maze(stdscr, maze, known_paths, known_walls, current_spot, explore_queue, last_candidates, close_words, far_words)
            time.sleep(5)
        stdscr.clear()
        stdscr.refresh()
        
        # PLAY GAME!!
        known_paths, known_walls = [start, end], []
        while True:
            write_maze(stdscr, maze, known_paths, known_walls, current_spot, explore_queue, last_candidates, close_words, far_words, lives=lives)
            char = stdscr.getch()
            if char == 67: key = 'r' 
            elif char == 68: key = 'l' 
            elif char == 65: key = 'u' 
            elif char == 66: key = 'd' 
            else: char = -1

            if char == -1:
                time.sleep(0.03)
                continue

            nearby_current = nearby(current_spot, nrows, ncols, directions=True)
            user_next = nearby_current[key]
            if user_next is None:
                # out of bounds, do nothing
                pass
            elif explored[user_next]['type'] == 'wall':
                # uh oh, user hits the wall!
                if user_next not in known_walls:
                    known_walls.append(user_next)
                lives -= 1
            elif explored[user_next]['type'] == 'path':
                # great choice, user!
                if user_next not in known_paths:
                    known_paths.append(user_next)
                current_spot = user_next
            time.sleep(0.05)

    finally:
        curses.echo()
        curses.nocbreak()
        curses.endwin()

if __name__ == '__main__':
    fire.Fire(main)