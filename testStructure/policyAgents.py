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
 
  def isPolicyHolds(self):
    raiseNotDefined()
    
  def generatePolicy(self):
    raiseNotDefined()
    
  def getActionForPolicy(self):
    raiseNotDefined()
    
class KillPolicy(Policy):
  def __init__(self, index, target, evalFn="scoreEvaluation"):
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.index = index
    self.target = target
    
  def isPolicyHolds(self, gamestate):
    enemypos = gamestate.getAgentPosition(self.target)
    mypos = gamestate.getAgentPosition(self.index)
    enemystate = gamestate.getAgentState(self.target)
    mystate = gamestate.getAgentState(self.index)
    (enemy_x, enemy_y) = nearestPoint(enemypos)
    if gamestate.getMapScore(enemy_x, enemy_y) >= 80: 
      return False 
    legals = gamestate.getLegalActions(self.index)
    scored = [(self.actualDistance(gamestate, gamestate.getAgentPosition(self.index),self.target,Actions.directionToVector(action)), action) for action in legals]
    bestScore = min(scored)[0]
    if bestScore == None: 
     return False
    if mystate.getLeftBombNumber() >= 0 and mystate.getSpeed() >= 0.25:
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
        if (x, y) == nearestPoint(gamestate.getAgentPosition(i)) and i != self.index:
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
    
  def getActionForPolicy(self, gamestate):
    # return LAY or the direction of tracing
    legals = gamestate.getLegalActions(self.index)
    if len(legals) == 1: return legals[0]
    (x, y) = nearestPoint(gamestate.getAgentPosition(self.target))
    (my_x, my_y) = nearestPoint(gamestate.getAgentPosition(self.index))
    
    #scored = [(self.manhattanEval(gamestate.getAgentPosition(self.index),
                                  #gamestate.getAgentPosition(self.target),Actions.directionToVector(action)), action) for action in legals]
    successors = [(gamestate.generateSuccessor(self.index,  action , True), action) for action in legals]
    avoidscored = [(self.evaluationFunction(nstate,(x, y),Actions.directionToVector(action)), action) for nstate, action in successors]
    bestavoidScore = min(avoidscored)[0]
    bestavoidActions = [pair[1] for pair in avoidscored if pair[0] == bestavoidScore]
    
    scored = [(self.actualDistance(gamestate, gamestate.getAgentPosition(self.index),self.target,Actions.directionToVector(action)), action) for action in legals]
    bestScore = min(scored)[0]
    bestActions = [pair[1] for pair in scored if pair[0] == bestScore]

    if bestScore == 0: return random.choice(bestavoidActions)
    
    originScore = gamestate.getBombScore(x,y) + gamestate.getMapScore(x,y)
    if Actions.LAY in legals:
      nstate = gamestate.generateSuccessor(self.index, Actions.LAY, True)
      layScore = self.evaluationFunction(nstate, (x, y), Actions.directionToVector(Actions.LAY))
    else:
      return random.choice(bestActions)
    
    if layScore > originScore and not gamestate.data.map.isBomb((my_x, my_y)):
      return Actions.LAY
      
    return random.choice(bestActions)
      
  def manhattanEval(self, pos1, pos2, vec):
    mypos = pos1[0]+vec[0], pos1[1]+vec[1]
    return manhattanDistance(mypos, pos2)
    
  def actualDistance(self, state, pos , target_index , vec = (0,0)):
    start = int(pos[0]+vec[0]), (pos[1] + vec[1])
    target = nearestPoint(state.getAgentPosition(target_index))
    closedSet = []
    openSet = [[(start,0,Directions.STOP),0]]
    
    g_score = {start:0}
    f_score = {start:(g_score[start]+util.manhattanDistance(start,target))}
    while len(openSet):
      openSet.sort(key=lambda x:x[1])
      cur_node = openSet[0]
      if manhattanDistance(cur_node[0][0],target) <= 0.5:
          return cur_node[0][1:] 
          
      openSet.pop(0)
      closedSet.append(cur_node)
      for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
          x,y = cur_node[0][0]
          vec = Actions.directionToVector(action)
          x, y = int(x+vec[0]),int(y+vec[1])
          if not state.data.map.isBlocked((x,y)):
              scoreChange = 1#+(state.data.MapScore[x][y]+state.data.BombScore[x][y])/20
              if cur_node[0][2] == Directions.STOP:
                  node = ((x,y),cur_node[0][1]+scoreChange,action)
              else:
                  node = ((x,y),cur_node[0][1]+scoreChange,cur_node[0][2])
              tentative_g = g_score[cur_node[0][0]]+scoreChange
              tentative_f = tentative_g + manhattanDistance(node[0],target)
              if node[0] in [x[0][0] for x in closedSet] and tentative_f >=f_score[node[0]]:
                  continue
              if node[0] not in [x[0][0] for x in openSet] or tentative_f < f_score[node[0]]:
                  g_score.update({node[0]:tentative_g})
                  f_score.update({node[0]:tentative_f})
                  if node[0] not in [x[0][0] for x in openSet]:
                      openSet.append([node,tentative_f])
    return None  

class PolicyAgent(Agent):
  def __init__(self, index = 0 , evalFn="scoreEvaluation"):
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.index = index
    assert self.evaluationFunction != None

  def getAction(self, state):
    policy = KillPolicy(self.index, 0)
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
    if not policy.isPolicyHolds(state):
      raise SystemExit
    return policy.getActionForPolicy(state)
    
      
def scoreEvaluation(state,pos,vec):
  x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
  return state.getBombScore(x,y) + state.getMapScore(x,y)