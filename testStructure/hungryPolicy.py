# coding: utf-8
from policyAgents import Policy
import random
from collections import deque
from math import ceil, floor
from game import Agent, AgentState, Actions, Directions


class HungryPutBombPolicy(Policy):

    def __init__(self,index, *_, **__):
        self.index = index
        self.targetPutBombPosition = None

    def isPolicyHolds(self, state):
        if self.targetPutBombPosition is None:
            print 'self.targetPutBombPosition is None, hungry policy end'
            return False
		
        agentState = state.getAgentState(self.index)

        if state.getBombScore(*map(int, agentState.getPosition())) > 30:
            return False

        if agentState.Bomb_Left_Number == 0:
            return False

        ability = sum([
                agentState.speed,            # speed 0 ~ 4
                agentState.Bomb_Power,       # power 0 ~ 7
                agentState.Bomb_Total_Number # nbomb 0 ~ 10
                ])
        if ability > 10:
            return False

        return True

    def generatePolicy(self, state):
        """
        Return a postition suitable to put a bomb
        """
        curr_map = state.data.map
        curr_pos = state.getAgentPosition(self.index)
        bomb_power = state.getAgentState(self.index).Bomb_Power + 1
        queue, visited = deque(), set()
        SEARCH_DEPTH = 10

        first_expanded = True
        queue.append((curr_pos, 0))
        visited.add(curr_pos)
        scored = []

        while len(queue) != 0:
            (x, y), this_dist = queue.popleft()
            if this_dist > SEARCH_DEPTH: break

            # FIXME Check the node here
            # -------------------
            this_dist = this_dist # smaller is better
            n_reachable = check_reachable(state, curr_map, bomb_power, (x, y)) # larger is better
            if state.data.map.isBomb(map(int,(x,y))): pass
            elif n_reachable > 0:
                score = n_reachable * 3 - this_dist # Configuratble score function
                if state.data.MapScore[int(x)][int(y)] < 80 :
                    scored.append((score, (x, y)))
                else:
                    print 'AVOID!!!'

            for adjpos in adjacentCoordinates((x, y)):
                if (adjpos[0] in range(curr_map.width) and
                        adjpos[1] in range(curr_map.height) and
                        not curr_map.isBlocked(adjpos) and
                        adjpos not in visited):
                    queue.append((adjpos, this_dist + 1))
                    visited.add(adjpos)

        # FIXME Compute result here..
        # -------------------
        if len(scored) == 0:
            self.targetPutBombPosition = None
        else:
            scored = sorted(scored, reverse=True)
            _score, (x, y) = scored[0]
            self.targetPutBombPosition = (x, y)
        print 'generate Policy:',self.targetPutBombPosition

    def getActionForPolicy(self, state):
        """
        1.
        Return an action that is the first action of shortest path to targetPos by
        BFS from current pos to targetPos

        2.
        IF the agent is already at targetPos, then put a bomb there if there is not
        one, and end this policy by setting self.targetPutBombPosition to None.
        """
        # TODO finish the above feature #2
        if self.targetPutBombPosition is None:
            return None
        curr_map = state.data.map
        curr_pos = state.getAgentPosition(self.index)
        target_pos = map(int, self.targetPutBombPosition)
        if curr_map.isBomb(target_pos):
            self.targetPutBombPosition = None
            return Directions.STOP

        if target_pos[0] == curr_pos[0] and target_pos[1] == curr_pos[1]:
            self.targetPutBombPosition = None
            return Actions.LAY

        if target_pos == None:
            return None
        target_x, target_y = target_pos
        queue, visited, SEARCH_DEPTH = deque(), set(), 20
        BOMB_SCORE_SAFE_THRESHOLD = 18

        first_expanded = True
        queue.append((curr_pos, 0, None))
        visited.add(curr_pos)

        ret_action = None
        while len(queue) != 0:
            (x, y), this_dist, first_action = queue.popleft()
            if this_dist >= SEARCH_DEPTH:
                break
            if x == target_x and y == target_y:
                ret_action = first_action
                break

            adj_positions = adjacentCoordinates((x, y))
            adj_actions = []
            if first_expanded:
                for (nx, ny) in adj_positions:
                    if nx != x:
                        if nx < x:  adj_actions.append(Directions.WEST)
                        else:       adj_actions.append(Directions.EAST)
                    elif ny != y:
                        if ny < y:  adj_actions.append(Directions.SOUTH)
                        else:       adj_actions.append(Directions.NORTH)
                for adjpos, act in zip(adj_positions, adj_actions):
                    if (adjpos[0] in range(curr_map.width) and
                            adjpos[1] in range(curr_map.height) and
                            not curr_map.isBlocked(adjpos) and
                            adjpos not in visited):
                        queue.append((adjpos, this_dist + 1, act))
                        visited.add(adjpos)
                first_expanded = False
            else:
                for adjpos in adj_positions:
                    if (adjpos[0] in range(curr_map.width) and
                            adjpos[1] in range(curr_map.height) and
                            not curr_map.isBlocked(adjpos) and
                            adjpos not in visited):
                        queue.append((adjpos, this_dist + 1, first_action))
                        visited.add(adjpos)
        def get_next_pos(curr_pos, ret_action):
            x, y = map(int, curr_pos)
            if ret_action == Directions.WEST:
                return (x-1, y)
            elif ret_action == Directions.EAST:
                return (x+1, y)
            elif ret_action == Directions.NORTH:
                return (x, y+1)
            elif ret_action == Directions.SOUTH:
                return (x, y-1)
        next_pos = get_next_pos(curr_pos, ret_action)
        if state.getBombScore(*next_pos) > 30:
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> STOP'
            return Directions.STOP
        else:
            return ret_action


def adjacentCoordinates(current_position):
    """
    Let's see its effect in examples
    >>> adjacentCoordinates((3.0, 4))
    [(2, 3), (2, 5), (4, 3), (4, 5)]

    >>> adjacentCoordinates((3.0, 4.7))
    [(3, 4), (3, 5)]

    >>> adjacentCoordinates((4.2, 4.0))
    [(3, 4), (4, 4)]

    """
    x, y = current_position
    x1, x2 = int(ceil(x)), int(floor(x))
    y1, y2 = int(ceil(y)), int(floor(y))
    x_new_vals = set([x1, x2])
    y_new_vals = set([y1, y2])
    if len(x_new_vals) == 2 and len(y_new_vals) == 2:
        raise Exception('Impossible current_position=%s' % str(current_position))
    elif len(x_new_vals) == 2 and len(y_new_vals) == 1:
        return [(x1, int(y)),
                (x2, int(y))]
    elif len(x_new_vals) == 1 and len(y_new_vals) == 2:
        return [(int(x), y1),
                (int(x), y2)]
    elif len(x_new_vals) == 1 and len(y_new_vals) == 1:
        return [(int(x), int(y) - 1),
                (int(x), int(y) + 1),
                (int(x) - 1, int(y)),
                (int(x) + 1, int(y))]

def check_reachable(state, curr_map, bomb_power, pos):
    curr_map = state.data.map
    next_pos_functions = [
            lambda x, y: (x - 1, y),
            lambda x, y: (x + 1, y),
            lambda x, y: (x, y - 1),
            lambda x, y: (x, y + 1)]
    reachable = 0
    for fx in next_pos_functions:
        x, y = pos
        x, y = int(x), int(y)
        counter = bomb_power
        while counter > 0:
            x, y = fx(x, y)
            if x not in range(curr_map.width) or y not in range(curr_map.height):
                break
            if curr_map.isBlocked((x, y)):
                if curr_map.isBlock((x, y)):
                    reachable += 1
            counter -= 1
    return reachable
