import pygame
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
ROWS, COLS = 8, 8
TILE_SIZE = 75
GAP = 5
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Match 3 Game")

# Colors
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (50, 50, 50)

# Gems
GEM_COLORS = ["red", "green", "blue", "yellow", "purple", "orange"]


class Gem:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.x = col * (TILE_SIZE + GAP) + GAP
        self.y = row * (TILE_SIZE + GAP) + GAP
        self.image = pygame.image.load(f"{color}_gem.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))


def create_board(rows, cols):
    board = [[Gem(row, col, random.choice(GEM_COLORS)) for col in range(cols)] for row in range(rows)]
    return board


def draw_board(window, board):
    for row in board:
        for gem in row:
            gem.draw(window)


def get_gem_from_mouse_pos(pos, board):
    x, y = pos
    for row in board:
        for gem in row:
            if gem.x <= x <= gem.x + TILE_SIZE and gem.y <= y <= gem.y + TILE_SIZE:
                return gem
    return None



def are_adjacent(gem1, gem2):
    return (abs(gem1.row - gem2.row) == 1 and gem1.col == gem2.col) or (abs(gem1.col - gem2.col) == 1 and gem1.row == gem2.row)

def find_matches(board):
    matches = []

    # Check horizontal matches
    for row in range(ROWS):
        for col in range(COLS - 2):
            gem1, gem2, gem3 = board[row][col], board[row][col + 1], board[row][col + 2]
            if gem1.color == gem2.color == gem3.color:
                matches.extend([gem1, gem2, gem3])

    # Check vertical matches
    for col in range(COLS):
        for row in range(ROWS - 2):
            gem1, gem2, gem3 = board[row][col], board[row + 1][col], board[row + 2][col]
            if gem1.color == gem2.color == gem3.color:
                matches.extend([gem1, gem2, gem3])

    return matches


def remove_matches(board, matches):
    for gem in matches:
        board[gem.row][gem.col] = None

def drop_gems(board):
    moved_gems = []
    for col in range(COLS):
        empty_slots = 0
        for row in range(ROWS - 1, -1, -1):
            if board[row][col] is None:
                empty_slots += 1
            elif empty_slots > 0:
                gem = board[row][col]
                moved_gems.append((gem, gem.row, gem.col))  # Store original position
                gem.row += empty_slots
                gem.y += empty_slots * (TILE_SIZE + GAP)
                board[row + empty_slots][col] = gem
                board[row][col] = None
    return moved_gems

def animate_drop_gems(moved_gems, board, duration=250):
    start_time = pygame.time.get_ticks()
    end_time = start_time + duration

    while pygame.time.get_ticks() < end_time:
        t = (pygame.time.get_ticks() - start_time) / duration

        for gem, old_row, old_col in moved_gems:
            start_y = old_row * (TILE_SIZE + GAP) + GAP
            target_y = gem.row * (TILE_SIZE + GAP) + GAP
            gem.y = lerp(start_y, target_y, t)

        WINDOW.fill(BACKGROUND_COLOR)
        draw_board(WINDOW, board)
        pygame.display.update()


def fill_empty_slots(board):
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] is None:
                board[row][col] = Gem(row, col, random.choice(GEM_COLORS))

def update_board(board):
    matches = find_matches(board)
    if matches:
        remove_matches(board, matches)
        drop_gems(board)
        fill_empty_slots(board)
    return len(matches)



def lerp(a, b, t):
    return a + (b - a) * t

def animate_swap(gem1, gem2, board, duration=250):
    start_time = pygame.time.get_ticks()
    end_time = start_time + duration

    start_pos1 = (gem1.x, gem1.y)
    start_pos2 = (gem2.x, gem2.y)

    while pygame.time.get_ticks() < end_time:
        t = (pygame.time.get_ticks() - start_time) / duration
        gem1.x, gem1.y = lerp(start_pos1[0], start_pos2[0], t), lerp(start_pos1[1], start_pos2[1], t)
        gem2.x, gem2.y = lerp(start_pos2[0], start_pos1[0], t), lerp(start_pos2[1], start_pos1[1], t)

        WINDOW.fill(BACKGROUND_COLOR)
        draw_board(WINDOW, board)
        pygame.display.update()

    gem1.x, gem1.y = start_pos2[0], start_pos2[1]
    gem2.x, gem2.y = start_pos1[0], start_pos1[1]
    gem1.row, gem2.row = gem2.row, gem1.row
    gem1.col, gem2.col = gem2.col, gem1.col
    board[gem1.row][gem1.col], board[gem2.row][gem2.col] = gem1, gem2





def main():
    run = True
    clock = pygame.time.Clock()
    board = create_board(ROWS, COLS)

    selected_gem = None
    drop_start_time = None

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked_gem = get_gem_from_mouse_pos(pygame.mouse.get_pos(), board)
                if clicked_gem:
                    if not selected_gem:
                        selected_gem = clicked_gem
                    elif selected_gem == clicked_gem:
                        selected_gem = None
                    elif are_adjacent(selected_gem, clicked_gem):
                        animate_swap(selected_gem, clicked_gem, board)
                        matches_found = update_board(board)

                        if matches_found == 0:
                            animate_swap(selected_gem, clicked_gem, board)
                        else:
                            while matches_found > 0:
                                moved_gems = drop_gems(board)
                                animate_drop_gems(moved_gems, board)  # Call the animate_drop_gems function
                                fill_empty_slots(board)
                                matches_found = update_board(board)

                        selected_gem = None
                    elif clicked_gem != selected_gem:
                        selected_gem = clicked_gem

        WINDOW.fill(BACKGROUND_COLOR)
        draw_board(WINDOW, board)
        pygame.display.update()

    pygame.quit()




if __name__ == "__main__":
    main()
