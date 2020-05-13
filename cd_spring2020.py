import sys
import math
from copy import deepcopy

# Movement Directions
LEFT = (-1, 0)
RIGHT = (1, 0)
UP = (0, -1)
DOWN = (0, 1)

DIRECTIONS = (LEFT, RIGHT, UP, DOWN)

SEPARATOR = " | "

def win_type(type_to_beat):
    if type_to_beat == "ROCK":
        return "PAPER"
    elif type_to_beat == "PAPER":
        return "SCISSORS"
    else:
        return "ROCK"

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
    
    def check_ngb_tiles(self, x, y, banned):
        def adjust(new_x, new_y):
            if new_x < 0:
                new_x += self.width
            elif new_x >= self.width:
                new_x -= self.width
            if new_y < 0:
                new_y += self.height
            elif new_y >= self.height:
                new_y -= self.height
            return new_x, new_y
        
        def check_tile(direction):
            tx, ty = adjust(x + direction[0], y + direction[1])
            if (tx, ty) in self.pellets:
                return 1
            elif (tx, ty) in banned:
                return -1
            return self.grid[ty][tx]
        tmp = None
        for d in DIRECTIONS:
            ret = check_tile(d)
            if ret == 1:
                return d
            elif ret == 0:
                tmp = d
        return tmp

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
        self.direction = None
    
    def update(self, x, y, pac_type, speed, cd):
        if self.x == int(x) and self.y == int(y):
            self.collision = True
        else:
            self.collision = False
            # self.direction = (int(x) - self.x)
        self.x = int(x)
        self.y = int(y)
        self.pac_type = pac_type
        self.speed = int(speed)
        self.cd = int(cd)
        self.alive = True
    
    def simple_move(self, map, visible, already_taken):
        if not self.cd and not self.collision:
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
            if closest_dist > dist_grid[pel[1]][pel[0]] and not pel in already_taken:
                closest = pel
                closest_dist = dist_grid[pel[1]][pel[0]]
        self.target = closest
        if closest:
            return f"MOVE {self.pid} {closest[0]} {closest[1]}"
        else:
            return None

    def direction_move(self, direction):
        return f"MOVE {self.pid} {self.x + direction[0]} {self.y + direction[1]}"
    
    def switch(self, to_beat):
        if not self.cd:
            new_type = win_type(to_beat)
            return f"SWITCH {self.pid} {new_type}" 
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
        self.turn = list()
        self.collision_tuples = list()
        self.moved = list()

    def __str__(self):
        pass

    def game_action(self):
        self.turn = list()
        self.moved = list()
        self.my_score, self.en_score = [int(i) for i in input().split()]
        self.read_visible_pacs()
        self.read_visible_pellets()
        self.update()
        self.resolve_collision()
        self.move()

    def update(self):
        self.collision_tuples = list()
        collided = list()
        for pid, pac in self.mypacs.items():
            self.map.update_map(pac.x, pac.y, self.round_pellets)
            if pac.collision:
                collided.append(pid)
        if len(collided) > 1:
            while collided:
                pid = collided.pop()
                p1 = self.mypacs[pid]
                opid_i = -1
                for other_pid in collided:
                    p2 = self.mypacs[other_pid]
                    if (p1.x == p2.x and abs(p1.y - p2.y) < 3) or (p1.y == p2.y and abs(p1.x - p2.x) < 3) or (abs(p1.y - p2.y) == 1 and abs(p1.x - p2.x) == 1):
                        opid_i = collided.index(other_pid)
                        print(f"Found collision: {pid}, {other_pid}(index {opid_i})", file=sys.stderr)
                        break
                if opid_i != -1:
                    print("Appending", file=sys.stderr)
                    opid = collided.pop(opid_i)
                    self.collision_tuples.append((pid, opid))
                else:
                    new = p1.switch(p1.pac_type)
                    if new:
                        self.turn.append(new)
                        self.moved.append(pid)
            print(f"Collision: {self.collision_tuples}", file=sys.stderr)
        elif len(collided) == 1:
            pid = collided.pop()
            p1 = self.mypacs[pid]
            new = p1.switch(p1.pac_type)
            if new:
                self.turn.append(new)
                self.moved.append(pid)
            
    def resolve_collision(self):
        # Attempt to resolve current collisions
        ban = list()
        for pid, pac in self.mypacs.items():
            ban.append((pac.x, pac.y))
        for incident in self.collision_tuples:
            p1 = self.mypacs[incident[0]]
            p2 = self.mypacs[incident[1]]
            d = self.map.check_ngb_tiles(p1.x, p1.y, ban)
            if d:
                # P1 moves, P2 waits
                self.turn.append(p1.direction_move(d))
                self.moved.append(p1.pid)
                self.moved.append(p2.pid)
                continue
            d = self.map.check_ngb_tiles(p2.x, p2.y, ban)
            if d:
                # P2 moves, P1 waits
                self.turn.append(p2.direction_move(d))
                self.moved.append(p1.pid)
                self.moved.append(p2.pid)
            # Missing resolution if none can move

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
        taken = list()
        for pid in self.mypacs.keys():
            if not pid in self.moved:
                new = self.mypacs[pid].simple_move(self.map, self.round_pellets, taken)
                taken.append(self.mypacs[pid].target)
                if new:
                    self.turn.append(new)
                self.moved.append(pid)
        print(SEPARATOR.join(self.turn))

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