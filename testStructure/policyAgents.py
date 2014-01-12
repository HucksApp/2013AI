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
    
class KillPolicy(Policy):
  def __init__(self, index, evalFn="scoreEvaluation"):
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.index = index
    self.target = 0
    
  def isPolicyConditionHolds(self, gamestate):
    enemypos = gamestate.getAgentPosition(self.target)
    mypos = gamestate.getAgentPosition(self.index)
    enemystate = gamestate.getAgentState(self.target)
    mystate = gamestate.getAgentState(self.index)
    #if self.enemyBlocked(enemypos, mypos): return False
    if mystate.getLeftBombNumber() >= 2 and mystate.getSpeed() >= 0.33:
      return True
    return False  
  
  def generatePolicy(self, gamestate):
    # return an enemy's agentindex
    threshold = 10
    currmap = gamestate.data.map
    targets = []
    queue = deque()
    visited = set()
    depth = {}
    adjacent_positions = lambda x, y: ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
    
    queue.append((nearestPoint(gamestate.getAgentPosition(self.index)), 0))
    visited.add(nearestPoint(gamestate.getAgentPosition(self.index)))

    while len(queue) != 0:
      (x, y), this_dist = queue.popleft()
      if this_dist > threshold: break
      for i in range(gamestate.getNumAgents()):
        if (x, y) == gamestate.getAgentPosition(i) and i != self.index:
          targets.append(i)
          depth[i] = this_dist    
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
      if depth[targets[i]]/gamestate.getAgentState(targets[i]).getSpeed() < eval:
        eval = depth[targets[i]]/gamestate.getAgentState(targets[i]).getSpeed()
        min = targets[i]
        
    self.target = min   
    return min 
    
  def getAction(self, gamestate):
    # return LAY or the direction of tracing
    legals = gamestate.getLegalActions(self.index)
    if len(legals) == 1: return legals[0]
    (x, y) = nearestPoint(gamestate.getAgentPosition(self.target))
    (my_x, my_y) = nearestPoint(gamestate.getAgentPosition(self.index))
    scored = [(self.manhattanEval(gamestate.getAgentPosition(self.index),
                                  gamestate.getAgentPosition(self.target),Actions.directionToVector(action)), action) for action in legals]
    bestScore = min(scored)[0]
    bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
    originScore = gamestate.getBombScore(x,y) + gamestate.getMapScore(x,y)
    
    if Actions.LAY in legals:
      nstate = gamestate.generateSuccessor(self.index, Actions.LAY, True)
      layScore = self.evaluationFunction(nstate, (x, y), Actions.directionToVector(Actions.LAY))
    else:
      return random.choice(bestActions)
    
    if layScore > originScore:
      if not gamestate.data.map.isBomb((my_x, my_y)):
        return Actions.LAY
      else:
        return random.choice(legals)
    else:
      return random.choice(bestActions)
      
  def manhattanEval(self, pos1, pos2, vec):
    mypos = pos1[0]+vec[0], pos1[1]+vec[1]
    return manhattanDistance(mypos, pos2)
    

class PolicyBomberman(Agent):
  def __init__(self, index = 0 , evalFn="scoreEvaluation"):
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.index = index
    assert self.evaluationFunction != None

  def getAction(self, state):
    policy = KillPolicy(self.index)
    """
    if policy.generatePolicy(state) == -1:
      legals = state.getLegalActions(self.index)
      #if Directions.STOP in legals: legal .remove(Directions.STOP)
      legal = [action for action in legals if not action is Directions.STOP]

      pos = state.getAgentPosition(self.index)
      successors = [(state.generateSuccessor(self.index,  action , True), action) for action in legal]
      if len(successors) is 0: return random.choice(legals)
      scored = [(self.evaluationFunction(nstate,pos,Actions.directionToVector(action)), action) for nstate, action in successors]
      bestScore = min(scored)[0]
      bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
      return random.choice(bestActions)
    """  
    #print policy.isPolicyConditionHolds(state)
    return policy.getAction(state)
    
      
def scoreEvaluation(state,pos,vec):
  x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
  return state.getBombScore(x,y) + state.getMapScore(x,y)