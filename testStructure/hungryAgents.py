# coding: utf-8

import random
from collections import deque
from math import ceil, floor
from game import Agent, AgentState, Actions, Directions
from policyAgents import PolicyAgent, Policy
from bombermanAgents import AvoidBomberman

class HungryBomberman(Agent):
    """
    An agent that perfers to eat items
    """
    def __init__(self, index=0, *_, **__):
        self.index = index

    def getAction(self, state):
        legal_actions = state.getLegalActions(self.index)
        legal_actions = [action for action in legal_actions
                if action is not Actions.LAY and
                action is not Directions.STOP]
        _currpos = state.getAgentPosition(self.index)
        successors = [(
                state.generateSuccessor(self.index, action, True), action
                ) for action in legal_actions]
        if len(successors) is 0: return Directions.STOP
        if len(successors) is 1: return successors[0][1]
        scored = [(
                self.hungryEvaluation(nstate, _currpos, self.index, False), action
                ) for nstate, action in successors]
        print 'scored=',scored,
        bestScore = max(scored)[0]
        bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
        ret = random.choice(bestActions)
        print ' choose ', ret
        # if all score are the same, return None
        differentScores = [act for sc, act in scored if sc != bestScore]
        if len(differentScores) == 0:
            print 'Return None'
            return None
        else:
            return ret

    def hungryEvaluation(self, nstate, oldpos, agentIdx, hasBombLeft=False):
        """
        NOTE: Currently, does not consider enemy's distance to the items
        """
        ox, oy = oldpos
        nx, ny = nstate.getAgentPosition(agentIdx)
        dx, dy = nx - ox, ny - oy

        if dx == 0:
            tx = int(ox)
        else:
            tx = (int(ceil(nx)) if dx > 0 else int(floor(nx)))

        if dy == 0:
            ty = int(oy)
        else:
            ty = (int(ceil(ny)) if dy > 0 else int(floor(ny)))

        # Items are 1 ~ 9
        #   1 - A - Item add Power
        #   2 - S - Item add Speed
        #   3 - N - Item add Bomb_Number
        # Which do I prefer?
        #
        # Here are functions caculating satisfaction degree about each item
        caculator = {
                1: lambda speed: (speed + 1) / 5,
                2: lambda power: (power + 1) / 8,
                3: lambda nbomb: (nbomb    ) / 10 }
        agentState = nstate.getAgentState(agentIdx)
        state = {
                1: agentState.speed,              # speed 0 ~ 4
                2: agentState.Bomb_Power,         # power 0 ~ 7
                3: agentState.Bomb_Total_Number } # nbomb 0 ~ 10
        satisfaction_item_pairs = [(caculator[i](state[i]), i) for i in state]
        satisfaction_order = [item_id for _, item_id in sorted(satisfaction_item_pairs)]

        dont_care_items = []
        if state[1] == len(AgentState.SPEED_TABLE) - 1: dont_care_items.append(1)
        if state[2] == len(AgentState.POWER_TABLE) - 1: dont_care_items.append(2)
        if state[3] == AgentState.BOMB_NUMBER_LIMITATION: dont_care_items.append(3)


        distances_to_item = {i: [] for i in state if i not in dont_care_items}
        print '  state=', state,
        print '  dont_care_items=', dont_care_items,
        print '  distances_to_item=', distances_to_item
        # Perform BFS starts from pos=(tx, ty) within 20 steps
        # to find all reachable items (if exists)
        # and fill their distances into distances_to_item dict
        currmap = nstate.data.map
        startpos = (tx, ty)

        queue = deque()
        visited = set()
        adjacent_positions = lambda x, y: ((x-1, y), (x+1, y), (x, y-1), (x, y+1))

        queue.append((startpos, 0))
        visited.add(startpos)
        ###print 'Start BFS',
        while len(queue) != 0:
            (x, y), this_dist = queue.popleft()
            if this_dist > 20: break
            item_id = currmap[x][y]
            if item_id in distances_to_item:
                distances_to_item[item_id].append(this_dist)
                ###print '(%d, %d)' % (x, y),
            for adjpos in adjacent_positions(x, y):
                if (not currmap.isBlocked(adjpos) and
                        adjpos[0] in range(currmap.width) and
                        adjpos[1] in range(currmap.height) and
                        adjpos not in visited):
                    queue.append((adjpos, this_dist + 1))
                    visited.add(adjpos)
        ###print 'End BFS'

        # Now we have some stuff like these
        #   satisfaction_order = [2, 1, 3]
        #   distances_to_item = { 1: [3, 5], 2: [1], 3: [2, 8] }
        #
        # For this state, how to score?  Sum all items up
        #   Distence  0   1   2   3   4 ... 19  >=20
        #   Score     20  19  18  17  16    1   0
        #   (Three items: The most wanted x1, the 2nd x0.8, the 3rd x0.5)
        score = 0
        weight = [1, 1, 1]
        for item_id in distances_to_item:
            w = weight[satisfaction_order.index(item_id)]
            for _dist in distances_to_item[item_id]:
                if _dist > 20:
                    continue
                dist_score_table = [100, 50, 25, 17, 16, 15,
                 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
                score += w * dist_score_table[_dist]
        ###print 'distances_to_item=', distances_to_item

        overall_ability = sum(state[i] for i in state) # compensation after eating item...
        ret = score + overall_ability * 1000
        print
        print 'score =', score
        print 'overall_ability =', overall_ability
        ###print '(ox,oy)=(%1.1f,%1.1f) (nx,ny)=(%1.1f,%1.1f) (tx,ty)=(%d,%d)'%(ox,oy,nx,ny,tx,ty),
        ###print ' has score=%d'%ret
        return ret

class HungryPutBombPolicy(PolicyAgent):

    def __init__(self, index=0, *_, **__):
        self.index = index
        self.targetPutBombPosition = None
        self.avoidBomberman = AvoidBomberman(index)
        self.hungryBomberman = HungryBomberman()

    def getAction(self, state):
        print 'HungryPutBombPolicy.getAction() is called'
        THRESHOLD_BOMB_DANGER = 8

        # If there is only one legal action, just return it.
        legal_actions = state.getLegalActions(self.index)
        if len(legal_actions) == 1:
            return legal_actions[0]

        # If the current position is dangerous, use the "AVOID" strategy
        x, y = map(int, map(round, state.getAgentState(self.index).getPosition()))
        if state.getBombScore(x, y) > THRESHOLD_BOMB_DANGER:
            return self.avoidBomberman.getAction(state)

        # If there are foods, use the "Hungry" strategy to eat them

        # Try to use Put Bomb policy
        if self.isPolicyHolds(state):
            if self.targetPutBombPosition == None:
                self.targetPutBombPosition = self.hungryWhereToPutBomb(state)
            act = self.getActionForPolicy(state)
            if act != None:
                return act
            # 如果 act == None 的話怎麼辦？
            # 就停下來，或 TODO: 產生新的 targetPutBombPosition 再算一次

            ###print 'The HungryPutBombPolicy.getAction() returns', act
            ###raise SystemExit
        return self.getActionByDecisionTree(state)

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
        curr_map = state.data.map
        curr_pos = state.getAgentPosition(self.index)
        target_pos = map(int, self.targetPutBombPosition)
        if curr_map.isBomb(target_pos):
            print 'There is a bomb at target_pos=', target_pos
            self.targetPutBombPosition = None
            print '~~~ TAT already has bomb... returns Actions.STOP'
            return Directions.STOP

        print ">>>>> target_pos", target_pos,
        print "curr_pos", curr_pos
        if target_pos[0] == curr_pos[0] and target_pos[1] == curr_pos[1]:
            self.targetPutBombPosition = None
            print '~~~ TAT already rreach the location... returns Actions.LAY'
            return Actions.LAY

        print 'getActionForPolicy wants to go to target_pos=',target_pos
        if target_pos == None: return None
        target_x, target_y = target_pos
        queue, visited, SEARCH_DEPTH = deque(), set(), 20
        BOMB_SCORE_SAFE_THRESHOLD = 8

        first_expanded = True
        queue.append((curr_pos, 0, None))
        visited.add(curr_pos)

        print 'BEFORE BFS...'
        while len(queue) != 0:
            (x, y), this_dist, first_action = queue.popleft()
            if this_dist > SEARCH_DEPTH:
                break
            if x == target_x and y == target_y:
                return first_action

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
                            adjpos not in visited and
                            state.getBombScore(x, y) <= BOMB_SCORE_SAFE_THRESHOLD):
                        queue.append((adjpos, this_dist + 1, first_action))
                        visited.add(adjpos)
        print 'AFTER BFS...'
        return None

    def getActionByDecisionTree(self, state):
        # TODO
        return Directions.STOP

    def isPolicyHolds(self, state):
        agentState = state.getAgentState(self.index)

        # 算自己的炸彈是否剩餘, TODO 考慮敵人距離
        if agentState.Bomb_Left_Number == 0:
            return False

        # 算周圍是否夠安全
        x, y = state.getAgentPosition(self.index)
        x, y = int(x), int(y)
        if state.getBombScore(x, y) > 5:
            return False

        # 是否能力值不足
        ability = sum([
                agentState.speed,            # speed 0 ~ 4
                agentState.Bomb_Power,       # power 0 ~ 7
                agentState.Bomb_Total_Number # nbomb 0 ~ 10
                ])
        if ability > 10:
            print 'Ability already enough'
            return False

        return True

    def hungryWhereToPutBomb(self, state):
        """
        Return a postition suitable to put a bomb
        """
        curr_map = state.data.map
        curr_pos = state.getAgentPosition(self.index)
        bomb_power = state.getAgentState(self.index).Bomb_Power + 1
        queue, visited = deque(), set()
        SEARCH_DEPTH = 10
        print 'BFS from curr_pos=', curr_pos

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
            if n_reachable > 0:
                print (x, y), "has n_reachable > 0 !!!"
                score = n_reachable * 3 - this_dist # Configuratble score function
                scored.append((score, (x, y)))

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
            return None
        else:
            scored = sorted(scored, reverse=True)
            print scored
            _score, (x, y) = scored[0]
            return (x, y)


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
    print 'inside check_reachable()',
    print 'pos=', pos, 'bomb_power', bomb_power
    curr_map = state.data.map
    next_pos_functions = [
            lambda x, y: (x - 1, y),
            lambda x, y: (x + 1, y),
            lambda x, y: (x, y - 1),
            lambda x, y: (x, y + 1)]
    reachable = 0
    for fx in next_pos_functions:
        print 'herer!'
        x, y = pos
        x, y = int(x), int(y)
        counter = bomb_power
        while counter > 0:
            print "IN"
            x, y = fx(x, y)
            if x not in range(curr_map.width) or y not in range(curr_map.height):
                break
            print '  ', x, y
            if curr_map.isBlocked((x, y)):
                if curr_map.isBlock((x, y)):
                    reachable += 1
            counter -= 1
    return reachable


"""
NOTE:

def isHungryPutBombPolicyConditionHolds()
    if policy exists: 檢查目標位置是否已經有炸彈
    是否能力值不足
    算自己的炸彈是否剩餘
    周圍夠安全
    return True / False

def generateHungryPutBombPolicy()
    回傳一個坐標


def getActionForHungryPutBombPolicy()
    從現在的位置 BFS 走到目標位置為止
    如果有一條路徑可以 reach target
    就 return 第一步
    如果沒有的話就 return None

"""
