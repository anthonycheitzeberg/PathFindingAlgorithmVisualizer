import pygame
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Visualizer")
DOUBLECLICKTIME = 500

colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "dirty_green": (134, 134, 121),
    "blue": (0, 255, 0),
    "yellow": (255, 255, 0),
    "white": (255, 255, 255),
    "dirty_white": (204, 191, 179),
    "black": (0, 0, 0),
    "purple": (128, 0, 128),
    "orange": (255, 165, 0),
    "grey": (128, 128, 128),
    "turquoise": (64, 224, 208),
}


class PathFinder:
    def __init__(self, algorithm):
        self.algorithm = algorithm


class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = width * row
        self.y = width * col
        self.color = colors["dirty_white"]
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def check_state(self, state):
        switcher = {
            "closed": self.color == colors["red"],
            "open": self.color == colors["green"],
            "barrier": self.color == colors["dirty_green"],
            "start": self.color == colors["orange"],
            "end": self.color == colors["turquoise"]
        }

        return switcher[state]

    def is_closed(self):
        return self.color == colors["red"]

    def is_open(self):
        return self.color == colors["green"]

    def is_barrier(self):
        return self.color == colors["dirty_green"]

    def is_start(self):
        return self.color == colors["orange"]

    def is_end(self):
        return self.color == colors["turquoise"]

    def reset(self):
        self.color = colors["dirty_white"]

    def make_start(self):
        self.color = colors["orange"]

    def make_closed(self):
        self.color = colors["turquoise"]

    def make_open(self):
        self.color = colors["green"]

    def make_barrier(self):
        self.color = colors["dirty_green"]

    def make_end(self):
        self.color = colors["red"]

    def make_path(self):
        self.color = colors["white"]

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])


def manhanttan_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def a_star_algorithm(draw_function, grid, start, end):
    """
    Implementation of the A* Path Finding Algorithm
    :param draw_function: lambda
    :param grid: list[][]
    :param start: Node
    :param end: Node
    :return: void
    """
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = f_score = {spot: float("inf") for row in grid for spot in row}

    g_score[start] = 0
    f_score[start] = manhanttan_distance(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw_function)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + manhanttan_distance(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw_function()

        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    """
    Creates the grid of object type Nodes to match
    with the visual grid
    :param rows: int
    :param width: int
    :return: grid: Node[]
    """
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid


def draw_grid(win, rows, width):
    """
    This handles drawing the grid lines on the window
    :param win: Surface
    :param rows: int
    :param width: int
    """
    gap = width // rows

    """
    First draw the horizontal lines and then the vertical lines
    """
    for i in range(rows):
        pygame.draw.line(win, colors["grey"], (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, colors["grey"], (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    """
    To draw and update the grid and objects
    :param win: Surface
    :param grid: list[][]
    :param rows: int
    :param width: int
    """
    win.fill(colors["dirty_white"])

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(win, width):
    ROWS = 25
    grid = make_grid(ROWS, width)

    start = None
    end = None
    run = True

    dbclock = pygame.time.Clock()

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            pos = pygame.mouse.get_pos()
            row, col = get_clicked_pos(pos, ROWS, width)
            node = grid[row][col]

            if pygame.mouse.get_pressed()[0]:
                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != end and node != start:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    a_star_algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

                if event.key == pygame.K_q:
                    stop = True

    pygame.quit()


if __name__ == '__main__':
    main(WIN, WIDTH)
