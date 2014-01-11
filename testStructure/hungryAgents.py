# coding: utf-8

import math
import random
from collections import deque
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
      tx = (int(math.ceil(nx)) if dx > 0 else int(math.floor(nx)))

    if dy == 0:
      ty = int(oy)
    else:
      ty = (int(math.ceil(ny)) if dy > 0 else int(math.floor(ny)))

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

class HungryPutBomb(Agent):

  def __init__(self, index=0, *_, **__):
    self.index = index

  def getAction(self, state):
    if self.isHungryPutBombConditionHolds():
      if self.targetPutBombPosition != None:
        # 嘗試去接近那個位置
        pass
      else:
        # 呼叫 hungryWhereToPutBomb() 找一個適合放炸彈的位置
        # 然後
        pass
    else:
        pass

  def isHungryPutBombConditionHolds(self):
    """
    Return True or False
    """
    return False

  def hungryWhereToPutBomb(self):
    """
    Return a postition
    """
    pass

  def actionToReachPos(self, targetPos):
    """
    Return an action that is the shortest path to targetPos
    by BFS from current pos to targetPos
    """
    pass


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
