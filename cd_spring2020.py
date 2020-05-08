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

def get_direction(p1, p2):
    xd = p2[0] - p1[0]
    yd = p2[1] - p1[1]
    if xd:
        xd = xd // abs(xd)
    if yd:
        yd = yd // abs(yd)
    return (xd, yd)

class Pac():
    def __init__(self, pacid, x, y, pac_type, speed, cd):
        self.pid = pacid
        self.x = int(x)
        self.y = int(y)
        self.pac_type = pac_type
        self.speed = int(speed)
        self.cd = int(cd)
        self.alive = True
        self.collision = False
        self.target = None
    
    def update(self, x, y, pac_type, speed, cd):
        if self.x == int(x) and self.y == int(y):
            self.collision = True
        else:
            self.collision = False
        self.x = int(x)
        self.y = int(y)
        self.pac_type = pac_type
        self.speed = int(speed)
        self.cd = int(cd)
        self.alive = True
    
    def simple_move(self, map, h, w):
        if not self.cd:
            return f"SPEED {self.pid}"
        dist_grid = manhattan(map, h, w, self.x, self.y)
        closest = None
        closest_dist = sys.maxsize
        me = (self.x, self.y)
        for y in range(h):
            for x in range(w):
                if map[y][x] > 0 and closest_dist > dist_grid[y][x]:
                    # if self.collision and self.target and get_direction(me, (x, y)) == get_direction(me, self.target):
                    #     continue
                    closest = (x, y)
                    closest_dist = dist_grid[y][x]
        self.target = closest
        if closest:
            return f"MOVE {self.pid} {closest[0]} {closest[1]}"
        else:
            return None

class Game():
    def __init__(self, height, width, raw_map):
        self.height = height
        self.width = width
        self.org_map = self.create_map(raw_map)
        self.turn_map = None
        self.visible_pacs = dict()
        self.visible_pellets = dict()
        self.mypacs = dict()
        self.enpacs = dict()
        self.my_score = 0
        self.en_score = 0
        self.turn = ""
        self.discovered_map = deepcopy(self.org_map)
        for y in range(self.height):
            for x in range(self.width):
                if self.discovered_map[y][x] == 0:
                    self.discovered_map[y][x] = 1

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
        self.set_pacs_dead()
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
            pac_id = int(pac_id)
            print(f"{pac_id} | {mine} | {x} {y}", file=sys.stderr)
            mine = mine == '1'
            if mine:
                if pac_id in self.mypacs.keys():
                    self.mypacs[pac_id].update(x, y, type_id, speed_turns_left, ability_cooldown)
                else:
                    self.mypacs[pac_id] = Pac(pac_id, x, y, type_id, speed_turns_left, ability_cooldown)
                print(f"Alive: {self.mypacs[pac_id].alive}", file=sys.stderr)
                self.discovered_map[int(y)][int(x)] = 0
            else:
                if pac_id in self.enpacs.keys():
                    self.enpacs[pac_id].update(x, y, type_id, speed_turns_left, ability_cooldown)
                else:
                    self.enpacs[pac_id] = Pac(pac_id, x, y, type_id, speed_turns_left, ability_cooldown)
        self.remove_dead_pacs()
        print(self.mypacs.keys(), file=sys.stderr)
    
    def read_visible_pellets(self):
        self.visible_pellets = dict()
        self.turn_map = deepcopy(self.org_map)
        visible_pellet_count = int(input())  # all pellets in sight
        for i in range(visible_pellet_count):
            x, y, value = [int(j) for j in input().split()]
            self.visible_pellets[(x, y)] = value
            self.turn_map[y][x] = value
            self.discovered_map[y][x] = 0
        for pid, pac in self.enpacs.items():
            self.turn_map[pac.y][pac.x] = -1

    def move(self):
        self.turn = ""
        for pid in self.mypacs.keys():
            new = self.mypacs[pid].simple_move(self.turn_map, self.height, self.width)
            if not new:
                new =  self.mypacs[pid].simple_move(self.discovered_map, self.height, self.width)
            if new:
                if self.turn != "":
                    self.turn += " | " + new
                else:
                    self.turn += new
        print(self.turn)

    def set_pacs_dead(self):
        for pid, pac in self.mypacs.items():
            pac.alive = False
        for pid, pac in self.enpacs.items():
            pac.alive = False
    
    def remove_dead_pacs(self):
        to_kill = list()
        for pid, pac in self.mypacs.items():
            if pac.alive == False:
                to_kill.append(pid)
        for pid in to_kill:
            del self.mypacs[pid]
        to_kill = list()  
        for pid, pac in self.enpacs.items():
            if pac.alive == False:
                to_kill.append(pid)
        for pid in to_kill:
            del self.enpacs[pid]

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
