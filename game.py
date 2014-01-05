#!/usr/bin/env python
# encoding: utf-8

import sys
import redis
import random
import time

mapsize_x = 0
mapsize_y = 0

try:
    r = redis.Redis()
    r.ping()
except redis.ConnectionError:
    print 'Cannot connect to the Redis server.  Exiting...'
    sys.exit(1)

SPEED = (30, 25, 15, 10, 5)


class Game(object):

    def __init__(self, n_players=2, map_name='village'):
        r.flushdb()
        self.map_players = []
        self.n_players = n_players
        self.init_map(map_name)
        self.init_game()
        self.init_players(n_players)

    def init_map(self, map_name):
        global mapsize_x
        global mapsize_y
        parsing_rules = {'-': 0, 'X': 11, 'B': 21, 'P': 0}
        map_dict = {'village': 'maps/village.txt',
                'pirate': 'maps/pirate.txt'}
        if map_name not in map_dict:
            print 'The map %s is not defined' % map_name
            sys.exit(1)
        with open(map_dict[map_name]) as f:
            lines = f.read().splitlines()
            mapsize_y = len(lines)
            mapsize_x = len(lines[0])
            y = 0
            for line in lines:
                x = 0
                for char in line:
                    if char == 'P':
                        self.map_players.append((x, y))
                    r.hset('map', '%d,%d' % (x, y), parsing_rules[char])
                    x += 1
                y += 1
        r.set('mapname', map_name)
        r.set('mapsize', '%d,%d' % (mapsize_x, mapsize_y))
        print 'Map %s of size %dx%d is initialized' % (
                map_name, mapsize_x, mapsize_y)

    def init_game(self):
        r.rpush('speed', *SPEED)
        r.set('fps', 30)
        r.set('remaining_frames', 3000)

    def init_players(self, n_players):
        if n_players > len(self.map_players):
            print 'Number of players exceeds maximum of the map'
            sys.exit(1)
        starting_positions = [self.map_players[i] for i in
                sample_m_from_n(n_players, len(self.map_players))]
        r.rpush('player_ids', *range(n_players))
        for i in range(n_players):
            x, y = starting_positions[i]
            r.hmset('player:%d' % i, {
                    'x': x,
                    'y': y,
                    'speed': 0,
                    'cd_time': 0,
                    'bomb_power': 1,
                    'n_bomb': 1,
                    'n_bomb_left': 1,
                    'direction': 'DOWN',
                    })

    def run_game(self):
        fps = 30
        spf = 1.0 / 30
        wait_time = spf / 3
        last_time = time.time()
        while 1:
            now_time = time.time()
            if now_time < last_time + spf:
                time.sleep(wait_time)
                continue
            last_time = now_time
            if r.get('remaining_frames') == 0:
                self.end_game()
                return
            self.job_per_frame()

    def job_per_frame(self):
        # 1. Perform actions from agents
        #    put_bomb / move / do_nothing
        for i in range(self.n_players):
            state_key = 'player:%d' % i
            agent_key = 'agent:%d:action' % i
            agent_action = r.get(agent_key)
            current_action = r.hget(state_key, 'direction')
            current_cd_time = int(r.hget(state_key, 'cd_time'))
            if current_cd_time > 0:
                player_update_position(player_id=i) # This function will decrease the cd_time
            else:
                player_perform_action(player_id=i, action=agent_action)
        # 2. Eat item
        for i in range(self.n_players):
            x, y = player_get_grid_pos(i)
            item_id = r.hget('map', '%d,%d' % (x, y))
            if item_id == 0: continue
            elif item_id <= 10:
                player_eat_item(player_id, x, y, item_id)

        # 3. Bomb explosion
        # ---------------------

        # Retrieve all bomb ids
        bomb_ids = r.lrange('bomb_ids', 0, -1)

        # Get all bombs, save them into an "bomb_id -> bomb" dict
        bombs = {}
        for i in bomb_ids:
            i = int(i)
            bombs[i] = r.hgetall('bomb:%d' % i)
            for int_val_name in ('x', 'y', 'power', 'cd_time', 'player_id'):
                bombs[i][int_val_name] = int(bombs[i][int_val_name])

        # Construct a "(x, y) -> bomb_id" dict
        pos_to_bomb = {}
        for bomb_id, bomb in bombs.iteritems():
            pos_to_bomb[(bomb.x, bomb.y)] = bomb_id

        # Foreach bomb, check if needs to explode? or just cd_time--
        for i, bomb in bombs.iteritems():
            if bomb['cd_time'] > 0:
                r.hset('bomb:%d' % i, 'cd_time', bomb['cd_time'] - 1)
            else:
                # TODO TODO TODO TODO TODO TODO TODO TODO
                # BFS at most `power` distance for 4 directions
                power = bomb['power']
                bomb_explode(i, bomb)

        # 4. Update remaining time for game
        r.decr('remaining_frames')

    def end_game(self):
        print 'End'


class GameState(object):

    def __init__(self):
        self.players = []

    def get_legal_actions(self, player):
        pass

    def get_successor(self, player, action):
        pass

    def update_player_state(self, player):
        pass

    def update_gamemap(self):
        pass

    def bomb_explode(self, bomb):
        pos = bomb.get_pos()
        power = bomb.get_power()
        this.gamemap.remove_item(pos)

    def update(self, action_list):
        pass


class Player(object):

    def can_move(self):
        return self.cd_time == 0

    def eat_item(self, item_id):
        pass

    def apply_action(self, action):
        pass


def sample_m_from_n(m, n):
    """
    Get m numbers in [0, 1, ... n-1]

    >>> sample_m_from_n(3, 10)
    [2, 9, 6]

    >>> sample_m_from_n(3, 10)
    [7, 8, 2]

    >>> sample_m_from_n(3, 10)
    [4, 2, 0]

    """
    ret = []
    values = range(n)
    for i in range(m):
        idx = random.choice(range(len(values)))
        ret.append(values.pop(idx))
    return ret


def player_perform_action(player_id, action):
    # current_cd_time > 0
    # so we can perform some action...
    if action == None:
        return
    if not legal_action(player_id, action):
        return
    if action == 'LAY':
        put_bomb(player_id)
        return
    player = r.hgetall('player:%d' % player_id)
    x = int(player['x'])
    y = int(player['y'])
    speed = int(player['speed'])
    player['target_x'], player['target_y'] = grid_pos_transform[action](x, y)
    player['x'], player['y'] = new_pos(x, y, action, speed)
    player['cd_time'] = SPEED[speed]
    player['direction'] = action
    r.hmset('player:%d' % player_id, player)


def player_update_position(player_id):
    player = r.hgetall('player:%d' % player_id)
    cd_time = int(player['cd_time'])
    speed = int(player['speed'])
    direction = player['direction']
    x = float(player['x'])
    y = float(player['y'])

    cd_time -= 1
    if cd_time > 0:
        x, y = new_pos(x, y, direction, speed)
        r.hset('player:%d' % player_id, 'cd_time', cd_time)
        r.hset('player:%d' % player_id, 'x', x)
        r.hset('player:%d' % player_id, 'y', y)
    else:
        r.hset('player:%d' % player_id, 'cd_time', cd_time)
        r.hset('player:%d' % player_id, 'x', player['target_x'])
        r.hset('player:%d' % player_id, 'y', player['target_y'])
        r.hdel('player:%d' % player_id, 'target_x')
        r.hdel('player:%d' % player_id, 'target_y')


def new_pos(x, y, action, speed):
    increment = 1.0 / SPEED[int(speed)]
    if action == 'UP':
        return (x, y - increment)
    if action == 'DOWN':
        return (x, y + increment)
    if action == 'LEFT':
        return (x - increment, y)
    if action == 'RIGHT':
        return (x + increment, y)

def legal_action(player_id, action):

    if action not in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'LAY']:
        return False

    x, y = player_get_grid_pos(player_id)
    if action == 'LAY':
        if r.hget('player:%d' % player_id, 'n_bomb_left') == 0:
            return False
        elif r.hget('map', '%d,%d' % (x, y)) > 10:
            return False
        else:
            return True

    new_pos = grid_pos_transform[action](x, y)
    if new_pos == None:
        return False

    x, y = new_pos
    if r.hget('map', '%d,%d' % (x, y)) > 10:
        return False
    else:
        return True


def player_get_grid_pos(player_id):
    x, y = r.hmget('player:%d' % player_id, 'x', 'y')
    return int(round(float(x))), int(round(float(y)))


def put_bomb(player_id):
    player = r.hgetall('player:%d' % player_id)
    player['x'] = int(player['x'])
    player['y'] = int(player['y'])
    x, y = player['x'], player['y']
    power = player['bomb_power']
    bomb_id = r.incr('next_bomb_id')
    r.hmset('bomb:%d' % bomb_id, {
            'x': x,
            'y': y,
            'power': power,
            'cd_time': 90,
            'player_id': player_id,
            })
    r.hincrby('player:%d' % player_id, 'n_bomb_left', -1)


def player_eat_item(player_id, x, y, item_id):
    # TODO
    # Remove item on the map
    # Apply effect on the player_id
    pass


def bomb_explode(bomb_id, bomb):
    # TODO
    """
    Start explosion per some frames

    foreach explosion_frame check the gamemap:
        if map has player:
            kill player
        if map has empty:
        elif map has item:
            this.gamemap.remove_item(item.pos)
        elif map has wall:
            stop
        elif map has block:
            change the block to item or empty
            stop
        elif map has bomb:
            if that bomb cd_time > 0:
                change cd_time to 1 or some reasonable value
    """
    # 炸彈 A 引爆炸彈 B 的情況只在 B 的 cd_time > 1 時


grid_pos_transform = {
        'UP':    lambda x, y: (x, y - 1) if y - 1 > 0         else None,
        'DOWN':  lambda x, y: (x, y + 1) if y + 1 < mapsize_y else None,
        'LEFT':  lambda x, y: (x - 1, y) if x - 1 > 0         else None,
        'RIGHT': lambda x, y: (x + 1, y) if x + 1 < mapsize_x else None,
        }

