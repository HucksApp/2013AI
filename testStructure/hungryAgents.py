# coding: utf-8

import random
from collections import deque
from math import ceil, floor
from game import Agent, Actions, Directions
from policyAgents import PolicyAgent, Policy

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
    ###print 'scored=',scored,
    bestScore = max(scored)[0]
    bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
    ret = random.choice(bestActions)
    ###print ' choose ', ret
    print
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


    distances_to_item = { 1: [], 2: [], 3: [] }
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
        if _dist == 0:
          score += 100
        else:
          score += w * (20 - _dist)
    ###print 'distances_to_item=', distances_to_item

    overall_ability = sum(state[i] for i in state) # compensation after eating item...
    ret = score + overall_ability * 1000
    ###print '(ox,oy)=(%1.1f,%1.1f) (nx,ny)=(%1.1f,%1.1f) (tx,ty)=(%d,%d)'%(ox,oy,nx,ny,tx,ty),
    ###print ' has score=%d'%ret
    return ret

class HungryPutBombPolicy(Policy):
  def isPolicyHolds(self, state): raiseNotDefined()
  def generatePolicy(self, state): raiseNotDefined()
  def getActionForPolicy(self, state): raiseNotDefined()

class HungryPutBombPolicyAgent(PolicyAgent):

  def __init__(self, index=0, *_, **__):
    self.index = index
    self.put_bomb_policy = HungryPutBombPolicy()
    self.targetPutBombPosition = None

  def getAction(self, state):
    if self.isHungryPutBombConditionHolds(state):
      # FIXME 在哪裡檢查正在執行的 policy 是否已經執行完成了？
      # eg: 檢查目標位置是否已經有炸彈
      if self.targetPutBombPosition == None:
        self.targetPutBombPosition = self.hungryWhereToPutBomb(state)
      act = self.getActionToPerformPolicy(state)
      if act == None: # 無法走到目標位置
        act = Directions.STOP # 就停下來，或 TODO: 產生新的 targetPutBombPosition 再算一次
      print 'The HungryPutBombPolicyAgent.getAction() returns', act
      raise SystemExit
    else:
      return self.getActionByDecisionTree(state)

  def getActionToPerformPolicy(self, state):
    """
    Return an action that is the first action of shortest path to targetPos by
    BFS from current pos to targetPos
    """
    curr_map = state.data.map
    curr_pos = state.getAgentPosition(self.index)
    target_pos = self.targetPutBombPosition
    if target_pos == None: return None
    target_x, target_y = target_pos
    queue, visited, SEARCH_DEPTH = deque(), set(), 20
    BOMB_SCORE_SAFE_THRESHOLD = 8

    first_expanded = True
    queue.append((curr_pos, 0, None))
    visited.add(curr_pos)

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
    return None

  def getActionByDecisionTree(self, state):
    # TODO
    return Directions.STOP

  def isHungryPutBombConditionHolds(self, state):
    agentState = nstate.getAgentState(self.index)

    # 算自己的炸彈是否剩餘, TODO 考慮敵人距離
    if agentState.Bomb_Left_Number == 0:
      return False

    # 算周圍是否夠安全
    if state.getBombScore(x, y) > 5:
      return False

    # 是否能力值不足
    ability = sum(
        agentState.speed,            # speed 0 ~ 4
        agentState.Bomb_Power,       # power 0 ~ 7
        agentState.Bomb_Total_Number # nbomb 0 ~ 10
        )
    if ability > 10:
      return False

    return True

  def hungryWhereToPutBomb(self, state):
    """
    Return a postition suitable to put a bomb
    """
    curr_map = state.data.map
    curr_pos = state.getAgentPosition(self.index)
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
      n_reachable = check_reachable(curr_map, bomb_power, (x, y)) # larger is better
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
      scored = sorted(scored, reversed=True)
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
  elif len(x_new_vals) == 1 and len(y_new_vals) == 1:
    x_new_vals = [int(x) - 1, int(x) + 1]
    y_new_vals = [int(y) - 1, int(y) + 1]
  return [(x, y) for x in x_new_vals for y in y_new_vals]

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
