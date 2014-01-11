from game import Agent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util
from util import nearestPoint
from collections import deque
import math

class Policy:
  def __init__(self, target):
    self.target = target
 
  def isPolicyConditionHolds(self):
    raiseNotDefined()
    
  def generatePolicy(self):
    raiseNotDefined()
    
  def getAction(self):
    raiseNotDefined()

"""
class HungryPolicy(Policy):
  def __init__(self, target, state):
    self.target = target
    self.state = state

  def isPolicyConditionHolds(self):
    if isBomb(self.target): return False
"""
    
class KillPolicy(Policy):
  def __init__(self, index, gamestate):
    self.index = index
    self.gamestate = gamestate
    self.target = 0
    
  def isPolicyConditionHolds(self):
    enemypos = gamestate.getAgentPosition(self.target)
    mypos = gamestate.getAgentPosition(self.index)
    enemystate = gamestate.getAgentState(self.target)
    mystate = gamestate.getAgentState(self.index)
    if self.enemyBlocked(enemypos, mypos): return False
    if mystate.getLeftBombNumber() >= 2 and mystate.getSpeed() >= 0.33:
      return True
    return False  
  
  def generatePolicy(self):
    # return an enemy's agentindex
    threshold = 5
    currmap = self.gamestate.data.map
    targets = []
    queue = deque()
    visited = set()
    depth = {}
    adjacent_positions = lambda x, y: ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
    
    queue.append((nearestPoint(self.gamestate.getAgentPosition(self.index)), 0))
    visited.add(nearestPoint(self.gamestate.getAgentPosition(self.index)))

    while len(queue) != 0:
      (x, y), this_dist = queue.popleft()
      if this_dist > threshold: break
      for i in range(self.gamestate.getNumAgents()) and i != self.index:
        if (x, y) == self.gamestate.getAgentPosition(i):
          targets.append(i)
          depth[i] = this_dict    
      for adjpos in adjacent_positions(x, y):
        if (not currmap.isBlocked(adjpos) and
            adjpos[0] in range(currmap.width) and
            adjpos[1] in range(currmap.height) and
            adjpos not in visited):
          queue.append((adjpos, this_dist + 1))
          visited.add(adjpos)

    eval = float('inf')
    min = -1
    for i in range(len(targets)):
      if depth[targets[i]]/self.gamestate.getAgentState(targets[i]).getSpeed() < eval:
        eval = depth[targets[i]]/self.gamestate.getAgentState(targets[i]).getSpeed()
        min = targets[i]
        
    self.target = min    
    return min 
    
  def getAction(self):
    # return LAY or the direction of tracing
    (x, y) = nearestPoint(self.gamestate.getAgentPosition(self.target))
    (my_x, my_y) = nearestPoint(self.gamestate.getAgentPosition(self.index))
    originScore = self.gamestate.getBombScore(x,y) + self.gamestate.getMapScore(x,y)
    
    nstate = self.gamestate.generateSuccessor(self.index, Actions.LAY, True)
    layScore = self.evaluationFunction(nstate, (x, y), Actions.directionToVector(Actions.LAY))
    if layScore > originScore:
      return Actions.LAY
    else:
      legals = self.gamestate.getLegalActions(self.index)
      successors = [(self.gamestate.generateSuccessor(self.index,  action , True), action) for action in legals]
      if len(successors) is 0: return random.choice(legals)
      scored = [(self.evaluationFunction(nstate,(x, y),Actions.directionToVector(action)), action) for nstate, action in successors]
      bestScore = min(scored)[0]
      bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
      return random.choice(bestActions)


class PolicyBomberman(Agent):
  def __init__(self, index = 0 , evalFn="scoreEvaluation"):
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.index = index
    assert self.evaluationFunction != None

  def getAction(self, state):
    if len(policies) == 0:
      # try to generate policies
      print '=='
    else: 
      # execute policies
      print '=='
      
def scoreEvaluation(state,pos,vec):
  x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
  return state.getBombScore(x,y) + state.getMapScore(x,y)