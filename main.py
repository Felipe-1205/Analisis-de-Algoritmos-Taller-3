import math
import random
from itertools import combinations

ROWS = 10
COLUMNS = 10
MINE_COUNT = 10

BOARD = []
MINES = set()
EXTENDED = set()

MATRIX = [['?'] * COLUMNS for i in range(ROWS)]


class Colors(object):
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def colorize(s, color):
    return '{}{}{}'.format(color, s, Colors.ENDC)


def get_index(i, j):
    if 0 > i or i >= COLUMNS or 0 > j or j >= ROWS:
        return None
    return i * ROWS + j


def create_board():
    squares = ROWS * COLUMNS

    # Create board
    for _ in range(squares):
        BOARD.append('[ ]')

    # Create mines
    while True:
        if len(MINES) >= MINE_COUNT:
            break
        MINES.add(int(math.floor(random.random() * squares)))


def draw_board():
    lines = []

    for j in range(ROWS):
        if j == 0:
            lines.append('   ' + ''.join(' {} '.format(x) for x in range(COLUMNS)))

        line = [' {} '.format(j)]
        for i in range(COLUMNS):
            line.append(BOARD[get_index(i, j)])
        lines.append(''.join(line))

    return '\n'.join(reversed(lines))


def parse_selection(raw_selection):
    try:
        return [int(x.strip(','), 10) for x in raw_selection.split(' ')]
    except Exception:
        return None


def adjacent_squares(i, j):
    num_mines = 0
    squares_to_check = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            # Skip current square
            if di == dj == 0:
                continue

            coordinates = i + di, j + dj

            # Skip squares off the board
            proposed_index = get_index(*coordinates)
            if not proposed_index:
                continue

            if proposed_index in MINES:
                num_mines += 1

            squares_to_check.append(coordinates)

    return num_mines, squares_to_check


def update_board(square, selected=True):
    i, j = square
    index = get_index(i, j)
    EXTENDED.add(index)

    # Check if we hit a mine, and if it was selected by the user or merely traversed
    if index in MINES:
        if not selected:
            return
        BOARD[index] = colorize(' X ', Colors.RED)
        return True
    else:
        num_mines, squares = adjacent_squares(i, j)
        MATRIX[i][j] = num_mines
        if num_mines:
            if num_mines == 1:
                text = colorize(num_mines, Colors.BLUE)
            elif num_mines == 2:
                text = colorize(num_mines, Colors.GREEN)
            else:
                text = colorize(num_mines, Colors.RED)

            BOARD[index] = ' {} '.format(text)
            return
        else:
            BOARD[index] = '   '

            for asquare in squares:
                aindex = get_index(*asquare)
                if aindex in EXTENDED:
                    continue
                EXTENDED.add(aindex)
                update_board(asquare, False)


def reveal_mines():
    for index in MINES:
        if index in EXTENDED:
            continue
        BOARD[index] = colorize(' X ', Colors.YELLOW)


def has_won():
    return len(EXTENDED | MINES) == len(BOARD)


def is_safe(square):
    """Verifica si una casilla es segura para seleccionar (sin minas conocidas o probables adyacentes)."""
    i, j = square
    num_mines, adj_squares = adjacent_squares(i, j)
    
    # Verificar si tiene minas adyacentes
    if num_mines > 0:
        return False  # No es seguro si hay minas adyacentes
    
    # Revisar si los vecinos adyacentes son seguros
    for adj in adj_squares:
        adj_i, adj_j = adj
        if MATRIX[adj_i][adj_j] == 'X':  # Si un vecino es conocido como mina
            return False
        
        # Verificar el riesgo calculado de casillas no exploradas adyacentes
        if MATRIX[adj_i][adj_j] == '?' and calculate_risk((adj_i, adj_j)) > 0.5:
            return False
        
    return True




def calculate_risk(square):
    """Calcula el riesgo de una casilla basado en el número de minas adyacentes y casillas no exploradas."""
    i, j = square
    num_mines, adj_squares = adjacent_squares(i, j)
    
    unexplored_adj = []
    for adj in adj_squares:
        if MATRIX[adj[0]][adj[1]] == '?':
            unexplored_adj.append(adj)
    
    if len(unexplored_adj) == 0:  # Sin casillas no exploradas adyacentes
        return float('inf')
    
    # Calcular la proporción de riesgo basado en minas conocidas y número de casillas adyacentes no exploradas
    total_adjacent = 0
    for adj in adj_squares:
        total_adjacent += 1
    
    unexplored_ratio = len(unexplored_adj) / total_adjacent
    risk = (num_mines / total_adjacent) * unexplored_ratio

    return risk



def forma2():
    unexplored_squares = [(i, j) for i in range(ROWS) for j in range(COLUMNS) if MATRIX[i][j] == '?']
    
    # Verificar primero las casillas seguras
    safe_moves = [square for square in unexplored_squares if is_safe(square)]
    
    if safe_moves:
        selected_square = random.choice(safe_moves)
        print(f"Jugador Fuerza Bruta juega en una casilla segura: {selected_square}")
        if update_board(selected_square):
            print(f"Jugador Fuerza Bruta ha activado una mina en: {selected_square}")
        elif has_won():
            print("Jugador Fuerza Bruta ha ganado el juego.")
        return selected_square
    
    # Si no hay movimientos seguros, seleccionar la casilla con menor riesgo
    min_risk_square = min(unexplored_squares, key=lambda sq: calculate_risk(sq))
    
    print(f"Jugador Fuerza Bruta juega en la casilla de menor riesgo: {min_risk_square}")
    if update_board(min_risk_square):
        print(f"Jugador Fuerza Bruta ha activado una mina en: {min_risk_square}")
    elif has_won():
        print("Jugador Fuerza Bruta ha ganado el juego.")
    return min_risk_square

def forma1():
    unexplored_squares = [(i, j) for i in range(ROWS) for j in range(COLUMNS) if MATRIX[i][j] == '?']

    best_square = None
    best_score = float('inf')  # Entre menor sea el puntaje, mejor

    for square in unexplored_squares:
        i, j = square
        num_mines, adj_squares = adjacent_squares(i, j)

        # Calcula una "puntuación de seguridad" en base al número de minas adyacentes
        adj_count = len(adj_squares)

        # Incorporar una ponderación adicional basada en el número de casillas no exploradas adyacentes
        unexplored_adj_count = sum(1 for adj in adj_squares if MATRIX[adj[0]][adj[1]] == '?')

        # Score penaliza la proximidad a minas y la falta de información en las casillas adyacentes
        score = (num_mines + unexplored_adj_count) / (adj_count + 1)

        if score < best_score:
            best_score = score
            best_square = square

    if best_square:
        print(f"Jugador Heurístico juega en: {best_square}")
        if update_board(best_square):
            print(f"Jugador Heurístico ha activado una mina en: {best_square}")
        elif has_won():
            print("Jugador Heurístico ha ganado el juego.")
        return best_square




def random_player():
    options = []
    for i in range(ROWS):
        for j in range(COLUMNS):
            if MATRIX[i][j] == '?':
                options.append((i, j))
    rand_square = options[random.randint(0, len(options))]
    print(f'Random player plays {rand_square}')
    return rand_square
    # NO SE PUEDE REVISAR  MINES!!!
    #TODO: 1. Combinaciones de opciones seleccionadas y no seleccionadas (fuerza bruta)
    #TODO: 2. Heurística: Revisar combinaciones promisorias

if __name__ == '__main__':
    create_board()

    print('Enter coordinates (ie: 0 3)')

    while True:

        print(draw_board())
        # square = random_player()
        # square = forma2()
        square = forma1() 
        # square = parse_selection(input('> '))
        if not square or len(square) < 2:
            print('Unable to parse indicies, try again...')
            continue

        mine_hit = update_board(square)
        if mine_hit or has_won():
            if mine_hit:
                reveal_mines()
                print(draw_board())
                print('Game over')
            else:
                print(draw_board())
                print('You won!')
            break
