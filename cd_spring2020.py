import sys
import math
from copy import deepcopy

# Movement Directions
LEFT = (-1, 0)
RIGHT = (1, 0)
UP = (0, -1)
DOWN = (0, 1)

DIRECTIONS = (LEFT, RIGHT, UP, DOWN)

class Map():
    def __init__(self, height, width, raw_data):
        self.height = height
        self.width = width
        self.grid = self.create_map(raw_data)
        self.pellets = list()
        self.init_pellets()
        self.super_pellets = list()

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

    def init_pellets(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 0:
                    self.pellets.append((x, y))

    def xy_to_coords(self, x, y):
        return (x, y)

    def remove_pellet(self, x, y):
        pel = self.xy_to_coords(x, y)
        if pel in self.pellets:
            i = self.pellets.index(pel)
            del self.pellets[i]
        # elif pel in self.super_pellets:
        #     i = self.super_pellets.index(pel)
        #     del self.super_pellets[i]
    
    def xy_inbonds(self, x, y):
        return (0 <= x < self.width) and (0 <= y < self.height)

    def update_map(self, pac_x, pac_y, round_pellets):
        def look_in_direction(x, y, direction):
            while self.xy_inbonds(x, y) and self.grid[y][x] == 0:
                if not (x, y) in round_pellets:
                    self.remove_pellet(x, y)
                x += direction[0]
                y += direction[1]
        # Remove the pellet, pac is standing on
        self.remove_pellet(pac_x, pac_y)
        # Look left
        look_in_direction(pac_x - 1, pac_y, LEFT)
        # Look right
        look_in_direction(pac_x + 1, pac_y, RIGHT)
        # Look up
        look_in_direction(pac_x, pac_y - 1, UP)
        # Look Down
        look_in_direction(pac_x, pac_y + 1, DOWN)

    def manhattan(self, x, y):
        manhattan = deepcopy(self.grid)
        for i in range(self.height):
            for k in range(self.width):
                manhattan[i][k] = abs(i - y) + abs(k - x)
        return manhattan

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
    
    def simple_move(self, map):
        if not self.cd:
            return f"SPEED {self.pid}"
        dist_grid = map.manhattan(self.x, self.y)
        closest = None
        closest_dist = sys.maxsize
        for pel in map.super_pellets:
            if closest_dist > dist_grid[pel[1]][pel[0]]:
                print(f"Pac{self.pid} heading for Super {pel}", file=sys.stderr)
                closest = pel
                closest_dist = dist_grid[pel[1]][pel[0]]
        if closest:
            return f"MOVE {self.pid} {closest[0]} {closest[1]}"
        for pel in map.pellets:
            if closest_dist > dist_grid[pel[1]][pel[0]]:
                closest = pel
                closest_dist = dist_grid[pel[1]][pel[0]]
        self.target = closest
        if closest:
            return f"MOVE {self.pid} {closest[0]} {closest[1]}"
        else:
            return None

    def directed_move(self, point):
        if not self.cd:
            return f"SPEED {self.pid}"
        return f"MOVE {self.pid} {point[0]} {point[1]}"
    
    def switch(self):
        if not self.cd:
            return f"SWITCH {self.pid}"
        else:
            return None

class Game():
    def __init__(self, height, width, raw_map):
        self.map = Map(height, width, raw_map)
        self.round_pellets = list()
        self.mypacs = dict()
        self.enpacs = dict()
        self.my_score = 0
        self.en_score = 0
        self.turn = ""

    def __str__(self):
        pass

    def game_action(self):
        self.my_score, self.en_score = [int(i) for i in input().split()]
        self.read_visible_pacs()
        self.read_visible_pellets()
        self.update()
        self.move()

    def update(self):
        for pid, pac in self.mypacs.items():
            self.map.update_map(pac.x, pac.y, self.round_pellets)

    def read_visible_pacs(self):
        self.set_pacs_dead()
        visible_pac_count = int(input())
        for i in range(visible_pac_count):
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
            else:
                if pac_id in self.enpacs.keys():
                    self.enpacs[pac_id].update(x, y, type_id, speed_turns_left, ability_cooldown)
                else:
                    self.enpacs[pac_id] = Pac(pac_id, x, y, type_id, speed_turns_left, ability_cooldown)
        self.remove_dead_pacs()
        print(self.mypacs.keys(), file=sys.stderr)
    
    def read_visible_pellets(self):
        self.round_pellets = list()
        self.map.super_pellets = list()
        visible_pellet_count = int(input())
        for i in range(visible_pellet_count):
            x, y, value = [int(j) for j in input().split()]
            if value == 10:
                self.map.super_pellets.append((x, y))
            self.round_pellets.append((x, y))
        print(f"Supers: {self.map.super_pellets}", file=sys.stderr)

    def move(self):
        self.turn = ""
        for pid in self.mypacs.keys():
            new = self.mypacs[pid].simple_move(self.map)
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
width, height = [int(i) for i in input().split()]
raw_map = list()
for i in range(height):
    row = input()
    raw_map.append(row)
mygame = Game(height, width, raw_map)

# game loop
while True:
    mygame.game_action()