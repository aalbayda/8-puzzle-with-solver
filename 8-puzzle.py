# Coded by Bob Albayda
# github.com/aalbayda

# Pygame 2.1.2
import pygame, sys
from pygame.locals import *
from copy import deepcopy

# Tkinter for importing files via window dialog box
import tkinter
import tkinter.filedialog

# Game window
WIDTH = 640
HEIGHT = 500
BG_COLOR = (197,250,247) 
BG_COLOR_SOLVED = (0,255,200)
BG_COLOR_UNSOLVABLE = (255,112,112)

# Tiles
TILE_SIZE = 78
TILE_COLOR = (51,153,255)

# Board
ROWS = COLS = 3
BORDER_COLOR = (0,0,0)
X_PADDING = 202
Y_PADDING = 132

# Font
TEXT_COLOR = (0,0,0)
FONT_SIZE = 30

# Moves
UP = 'U'
DOWN = 'D'
LEFT = 'L'
RIGHT = 'R'

# Animation
FPS = 40
SPEED = 10

# Order of a solved board
def solved():
    return [[1,4,7],[2,5,8],[3,6,0]]

# Check if the puzzle is solvable
def solvable(board):
    nums = []
    for i in range(3):
        for row in board:
            nums.append(row[i])

    # Count inversions
    count = 0
    for i in range(9):
        for j in range(i+1,9):
            if (nums[j] > 0 and nums[i] > 0 and nums[i] > nums[j]):
                count += 1
    
    # Num of inversions must be even to be solvable
    return (count % 2 == 0)
    

# Position of empty (0) tile
def getEmptyTile(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return (i,j)

# Move board position
def move(board, direction):
    x, y = getEmptyTile(board)
    if direction == DOWN:
        board[x][y], board[x][y+1] = board[x][y+1], board[x][y]
    elif direction == UP:
        board[x][y], board[x][y-1] = board[x][y-1], board[x][y]
    elif direction == RIGHT:
        board[x][y], board[x+1][y] = board[x+1][y], board[x][y]
    elif direction == LEFT:
        board[x][y], board[x-1][y] = board[x-1][y], board[x][y]
    return board

# Check for border collision
def validateMove(board, direction):
    x, y = getEmptyTile(board)
    if direction == DOWN:
        return y != len(board[0])-1
    elif direction == UP:
        return y != 0
    elif direction == RIGHT:
        return x != len(board)-1
    elif direction == LEFT:
        return x != 0

# Convert array (board) position to pixel (window) position
def getPixelPosition(tile_x, tile_y):
    left = X_PADDING + (tile_x * TILE_SIZE) + (tile_x - 1)
    top = Y_PADDING + (tile_y * TILE_SIZE) + (tile_y - 1)
    return (left, top)

# Get array (board) position of clicked pixel
def getBoardPosition(board, x, y):
    for tile_x in range(len(board)):
        for tile_y in range(len(board[0])):
            left, top = getPixelPosition(tile_x, tile_y)
            tileRect = pygame.Rect(left, top, TILE_SIZE, TILE_SIZE)
            if tileRect.collidepoint(x, y):
                return (tile_x, tile_y)
    return (None, None)

# Render tile
def drawTile(tile_x, tile_y, number, adj_x=0, adj_y=0):
    left, top = getPixelPosition(tile_x, tile_y)
    pygame.draw.rect(DISPLAY_SURF, TILE_COLOR, (left + adj_x, top + adj_y, TILE_SIZE, TILE_SIZE))
    textSurf = FONT.render(str(number), True, TEXT_COLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILE_SIZE / 2) + adj_x, top + int(TILE_SIZE / 2) + adj_y
    DISPLAY_SURF.blit(textSurf, textRect)

# Render text
def makeText(text, color, bgcolor, top, left):
    textSurf = FONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)

# Render board
def drawBoard(board):
    DISPLAY_SURF.fill(BG_COLOR)
    
    if solver_mode: # Solver mode, most moves are disabled
        
        # Show next and next move while board is still unsolved
        if len(solution) > 0:
            textSurf, textRect = makeText("Next move: "+solution[0], TEXT_COLOR, BG_COLOR, 220,50)
            DISPLAY_SURF.blit(NEXT_SURF, NEXT_RECT)
        # Freeze board when done solving
        else:
            textSurf, textRect = makeText("Solved for a cost of "+str(cost)+"!", TEXT_COLOR, BG_COLOR, 170, 50)
            DISPLAY_SURF.blit(LOAD_SURF, LOAD_RECT)

    else: # Playable mode    
        # Tell if not solvable
        if solvable(board):
            textSurf, textRect = makeText("Solvable", TEXT_COLOR, BG_COLOR, 250, 50)
        else:
            textSurf, textRect = makeText("Unsolvable!", TEXT_COLOR, BG_COLOR_UNSOLVABLE, 230, 50)

        # Tell if solved
        if board == solved():
            DISPLAY_SURF.fill(BG_COLOR_SOLVED)
            textSurf, textRect = makeText("Solved!", TEXT_COLOR, BG_COLOR_SOLVED, 250, 50)
            DISPLAY_SURF.blit(textSurf, textRect)

        # Draw buttons
        DISPLAY_SURF.blit(LOAD_SURF, LOAD_RECT)
        DISPLAY_SURF.blit(DFS_SURF, DFS_RECT)
        DISPLAY_SURF.blit(BFS_SURF, BFS_RECT)
        DISPLAY_SURF.blit(ASTAR_SURF, ASTAR_RECT)
    
    # Header text
    DISPLAY_SURF.blit(textSurf, textRect)

    # Draw board
    for tile_x in range(3):
        for tile_y in range(3):
            if board[tile_x][tile_y] != 0:
                drawTile(tile_x, tile_y, board[tile_x][tile_y])
    left, top = getPixelPosition(0, 0)
    width = ROWS * TILE_SIZE
    height = COLS * TILE_SIZE
    pygame.draw.rect(DISPLAY_SURF, BORDER_COLOR, (left - 5, top - 5, width + 10, height + 10), 4)

# Animate
def slideAnimation(board, move, speed):
    blank_x, blank_y = getEmptyTile(board)
    if move == DOWN:
        move_x = blank_x
        move_y = blank_y + 1
    elif move == UP:
        move_x = blank_x
        move_y = blank_y -1
    elif move == RIGHT:
        move_x = blank_x + 1
        move_y = blank_y
    elif move == LEFT:
        move_x = blank_x -1
        move_y = blank_y
    drawBoard(board)
    baseSurf = DISPLAY_SURF.copy()
    moveLeft,moveTop = getPixelPosition(move_x,move_y)
    pygame.draw.rect(baseSurf, BG_COLOR, (moveLeft, moveTop, TILE_SIZE, TILE_SIZE))

    # Render loop
    for i in range(0, TILE_SIZE, speed):
        for event in pygame.event.get(QUIT):
            pygame.quit()
            sys.exit()
        DISPLAY_SURF.blit(baseSurf, (0,0))
        if move == DOWN:
            drawTile(move_x, move_y, board[move_x][move_y],0,-1*i)
        elif move == UP:
            drawTile(move_x, move_y, board[move_x][move_y],0,i)
        elif move == RIGHT:
            drawTile(move_x, move_y, board[move_x][move_y],-1*i,0)
        elif move == LEFT:
            drawTile(move_x, move_y, board[move_x][move_y],i,0)
        pygame.display.update()
        FPS_CLOCK.tick(FPS) 

# Window dialog with Tkinter
def selectFile():
    top = tkinter.Tk()
    top.withdraw()
    fname = tkinter.filedialog.askopenfilename(parent=top)
    top.destroy()

    # If no selected file (ie user clicks 'X'), quit
    if not fname:
        pygame.quit()
        sys.exit()
    return fname
    

# Read from specified filename, otherwise will use puzzle.in as default
def load(filename):
    f = open(filename, "r")
    board = [[],[],[]]
    given = f.read().split("\n")
    for i in range(3):
        for line in given:
            line = line.split(" ")
            board[i].append(int(line[i]))
    f.close()
    return board

# Read from puzzle.out and animate
def readSolution():
    f = open("puzzle.out", "r")
    solution = f.read().split(" ")
    cost = len(solution)
    return (solution, cost)

## CLASSES FOR SEARCH AGENT ##

# Node for each state
class Node():
    def __init__(self, state, parent, action, g, h):
        self.state = state
        self.parent = parent
        self.action = action

        # Values for A* search
        self.g = g # Path cost so far
        self.h = h # Heuristic
        self.f = self.g + self.h # Total cost

# Frontier blueprint for stack, queue, and priority queue
class Frontier():
    def __init__(self):
        self.frontier = []
    
    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0    

# Stack frontier
class DFS_Frontier(Frontier):
    def remove(self):
        if self.empty():
            raise Exception("Empty frontier!")
        else:
            # LIFO
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

# Queue frontier
class BFS_Frontier(Frontier):
    def remove(self):
        if self.empty():
            raise Exception("Empty frontier!")
        else:
            # FIFO
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

# A* priority queue frontier
class AStar_Frontier(Frontier):
    def remove(self):
        if self.empty():
            raise Exception("Empty frontier!")
        else:
            # Remove the state with the smallest f(n)
            node = min(self.frontier, key=lambda state: state.f)
            self.frontier.remove(node)
            return node
            

class Puzzle():
    def __init__(self):
        self.start = board
        self.goal = solved()
        self.solution = None

    # Returns all possible (state,action) from current node
    def actions(self, state):
        result = []
        moves = [UP, RIGHT, DOWN, LEFT] # Follows order in handout
        for m in moves:
            if validateMove(state, m):
                result.append((m, move(deepcopy(state), m)))
        return result

    # Get x, y positions of given tile value in the goal state
    def get_goal_position(self, tile):
        for x in range(3):
            for y in range(3):
                if self.goal[x][y] == tile:
                    return x, y

    # Find h(n)
    def find_h(self, board):
        # Sum of all computed manhattan distance
        h = 0
        # Go through each tile of the state and get its manhattan distance
        for x2 in range(3):
            for y2 in range(3):
                # Don't count the empty tile
                if board[x2][y2] != 0:
                    # Find position of tile in the goal state
                    x1, y1 = self.get_goal_position(board[x2][y2])
                    # Manhattan distance = | x1 - x2 | + | y1 - y2 |
                    h += abs(x1 - x2) + abs(y1 - y2)

        return h

    # Solver
    def solve(self, algo):
        print("Solving...")
        
        # Initialize
        start = Node(state=self.start, parent=None, action=None, g=0, h=0)
        if algo == "DFS":
            frontier = DFS_Frontier()
        elif algo == "BFS":
            frontier = BFS_Frontier()
        elif algo == "A*":
            frontier = AStar_Frontier()
        frontier.add(start)

        # Keep track of already explored nodes
        # A set will not add elements already inside it
        self.explored = set()

        # Keep exploring new states until found goal state
        while True:
            if frontier.empty():
                print("Empty frontier, unsolvable.")
                pygame.quit()
                sys.exit()
            
            # Mark node as explored
            node = frontier.remove()
            self.explored.add(str(node.state)) # set() does not accept lists; need to stringify entries

            # When found goal state, store solution
            if node.state == self.goal:
                solution = []

                # "Crawl" back to find solution
                while node.parent is not None:
                    solution.append(node.action)
                    node = node.parent
                solution.reverse()

                # Write to puzzle.out
                f = open('puzzle.out', 'w')
                f.write(" ".join(solution))
                f.close()

                print("Solution: " + ", ".join(list(map(lambda move: move, solution))))
                print("Path cost of solution: " + str(len(solution)))
                print("Number of paths explored to find solution: " + str(len(self.explored)))
                return

            # Go through action space and explore each action
            for action, state in self.actions(node.state):
                if not frontier.contains_state(state) and str(state) not in self.explored:
                    child = Node(state=state, parent=node, action=action, g=node.g+1, h=self.find_h(state))
                    frontier.add(child)
                    print(state)

# Game
def main():
    # Pygame variables
    global FPS_CLOCK, DISPLAY_SURF, FONT, LOAD_SURF, LOAD_RECT, BFS_SURF, BFS_RECT, DFS_SURF, DFS_RECT, ASTAR_RECT, ASTAR_SURF, NEXT_SURF, NEXT_RECT, solver_mode, solution, cost, board

    pygame.init()
    pygame.display.set_caption("Eight Puzzle: Exercise 3")
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WIDTH, HEIGHT))

    # Render "buttons"
    FONT = pygame.font.Font('freesansbold.ttf', FONT_SIZE)
    LOAD_SURF, LOAD_RECT = makeText('Load Game', TEXT_COLOR, TILE_COLOR, 245, HEIGHT-118)
    BFS_SURF, BFS_RECT = makeText('BFS Solve', TEXT_COLOR, TILE_COLOR, 40, HEIGHT-55)
    DFS_SURF, DFS_RECT = makeText('DFS Solve', TEXT_COLOR, TILE_COLOR, 250, HEIGHT-55)
    ASTAR_SURF, ASTAR_RECT = makeText('A* Solve', TEXT_COLOR, TILE_COLOR, 460, HEIGHT-55)
    NEXT_SURF, NEXT_RECT = makeText('Show next move', TEXT_COLOR, TILE_COLOR, 190, HEIGHT-90)

    
    # Load save file
    board = load(selectFile())
    
    # If solver mode is on most player moves are disabled
    solver_mode = False

    # Game loop
    while True:
        slideTo = 0
        drawBoard(board)

        # Check if quit (clicked 'X')
        for event in pygame.event.get(QUIT):
            pygame.quit()
            sys.exit()

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                spot_x,spot_y = getBoardPosition(board,event.pos[0],event.pos[1])

                # Handle button events
                if (spot_x,spot_y) == (None,None):

                    if solver_mode == True:
                        # Clicks on Next (during solver mode)
                        if NEXT_RECT.collidepoint(event.pos) and len(solution) > 0:                         
                            slideAnimation(board, solution[0], SPEED)
                            move(board, solution[0])
                            solution.pop(0)

                        if LOAD_RECT.collidepoint(event.pos):
                            # Restarts game after solving a game
                            if solver_mode:
                                main()

                    else:
                        # Clicks on Load Puzzle
                        if LOAD_RECT.collidepoint(event.pos):
                            board = load(selectFile())
                        
                        # Clicks on a solve button
                        elif board != solved():
                            algo = None
                            if BFS_RECT.collidepoint(event.pos):
                                algo = "BFS"
                            elif DFS_RECT.collidepoint(event.pos):
                                algo = "DFS"
                            elif ASTAR_RECT.collidepoint(event.pos):
                                algo = "A*"

                            if algo:
                                # Disable player moves except for solution guided moves
                                solver_mode = True

                                # Call the puzzle object or agent and solve with the given algo
                                Puzzle().solve(algo)

                                # Read solution store globally
                                solution, cost = readSolution()

                elif solver_mode:
                    blank_x, blank_y = getEmptyTile(board)

                # Handle tile events
                else:
                    blank_x, blank_y = getEmptyTile(board)
                    if spot_x == blank_x+1 and spot_y == blank_y:
                        slideTo = RIGHT
                    elif spot_x == blank_x-1 and spot_y == blank_y:
                        slideTo = LEFT
                    elif spot_x == blank_x and spot_y == blank_y+1:
                        slideTo = DOWN
                    elif spot_x == blank_x and spot_y == blank_y-1:
                        slideTo = UP
        
        # Animate
        if slideTo:
            slideAnimation(board, slideTo, SPEED)
            move(board, slideTo)
        pygame.display.update()
        FPS_CLOCK.tick(FPS)

main()