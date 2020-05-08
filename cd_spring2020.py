import sys
import math
from copy import deepcopy

# Movement Directions
LEFT = (-1, 0)
RIGHT = (1, 0)
UP = (0, -1)
DOWN = (0, 1)

DIRECTIONS = (LEFT, RIGHT, UP, DOWN)

# Euclid distance
def distance(p1, p2):
    xd = p2[0] - p1[0]
    yd = p2[1] - p1[1]
    return ((xd ** 2) + (yd ** 2)) ** 0.5

def manhattan(grid, h, w, x, y):
    manhattan = deepcopy(grid)
    for i in range(h):
        for k in range(w):
            manhattan[i][k] = abs(i - y) + abs(k - x)
    return manhattan
 
class Pac():
    def __init__(self, pacid, x, y):
        self.pid = int(pacid)
        self.x = int(x)
        self.y = int(y)
    
    def update(self, x, y):
        self.x = int(x)
        self.y = int(y)
    
    def simple_move(self, map, h, w):
        dist_grid = manhattan(map, h, w, self.x, self.y)
        closest = (sys.maxsize, sys.maxsize)
        closest_dist = sys.maxsize
        me = (self.x, self.y)
        for y in range(h):
            for x in range(w):
                if map[y][x] > 0 and closest_dist > dist_grid[y][x]:
                    closest = (x, y)
                    closest_dist = dist_grid[y][x]
        print(f"MOVE {self.pid} {closest[0]} {closest[1]}")



class Game():
    def __init__(self, height, width, raw_map):
        self.height = height
        self.width = width
        self.org_map = self.create_map(raw_map)
        self.turn_map = None
        self.visible_pacs = dict()
        self.visible_pellets = dict()
        self.mypac = None
        self.enpac = None
        self.my_score = 0
        self.en_score = 0

    def __str__(self):
        s = ""
        for row in self.turn_map:
            s += str(row) + "\n"
        return s

    def create_map(self, raw_map):
        map = list()
        for row in raw_map:
            new = list()
            for c in row:
                if c == '#':
                    new.append(-1)
                elif c == ' ':
                    new.append(0)
            map.append(new)
        return map

    def read_visible_pacs(self):
        self.visible_pacs = dict()
        visible_pac_count = int(input())  # all your pacs and enemy pacs in sight
        for i in range(visible_pac_count):
            # pac_id: pac number (unique within a team)
            # mine: true if this pac is yours
            # x: position in the grid
            # y: position in the grid
            # type_id: unused in wood leagues
            # speed_turns_left: unused in wood leagues
            # ability_cooldown: unused in wood leagues
            pac_id, mine, x, y, type_id, speed_turns_left, ability_cooldown = input().split()
            print(f"{pac_id} | {mine} | {x} {y}", file=sys.stderr)
            mine = mine == '1'
            if mine:
                if self.mypac:
                    self.mypac.update(x, y)
                else:
                    self.mypac = Pac(pac_id, x, y)
            else:
                if self.enpac:
                    self.enpac.update(x, y)
                else:
                    self.enpac = Pac(pac_id, x, y)
            speed_turns_left = int(speed_turns_left)
            ability_cooldown = int(ability_cooldown)
    
    def read_visible_pellets(self):
        self.visible_pellets = dict()
        self.turn_map = deepcopy(self.org_map)
        visible_pellet_count = int(input())  # all pellets in sight
        for i in range(visible_pellet_count):
            x, y, value = [int(j) for j in input().split()]
            self.visible_pellets[(x, y)] = value
            self.turn_map[y][x] = value
        self.turn_map[self.enpac.y][self.enpac.x] = -1

    def move(self):
        self.mypac.simple_move(self.turn_map, self.height, self.width)


## INIT
# Grab the pellets as fast as you can!

# width: size of the grid
# height: top left corner is (x=0, y=0)
width, height = [int(i) for i in input().split()]
raw_map = list()
for i in range(height):
    row = input()  # one line of the grid: space " " is floor, pound "#" is wall
    raw_map.append(row)
mygame = Game(height, width, raw_map)
init_round = True
# game loop
while True:
    mygame.my_score, mygame.en_score = [int(i) for i in input().split()]
    mygame.read_visible_pacs()
    mygame.read_visible_pellets()

    # MOVE <pacId> <x> <y>
    mygame.move()