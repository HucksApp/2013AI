from policyAgents import Policy
from util import *
from game import Agent
from game import Actions
from game import Directions
import random
from collections import deque
import math


class KillPolicy(Policy):

  def __init__(self, index, target, evalFn="scoreEvaluation"):
    self.evaluationFunction = lookup(evalFn, globals())
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
    if mystate.getLeftBombNumber() > 0 and mystate.getSpeed() >= 1:
      return True
    return False  
      
  def getActionForPolicy(self, gamestate):
    print '\033[1;31m  Execution of Kill Policy!!!  \033[0m'
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
    print 'Bomb: ', gamestate.getBombScore(x,y)
    print 'Map: ', gamestate.getMapScore(x,y)
    if Actions.LAY in legals:
      print 'pass Actions.LAY in legals...'
      nextstate = gamestate.generateSuccessor(self.index, Actions.LAY, True)
      layScore = nextstate.getBombScore(x,y) + nextstate.getMapScore(x,y)
      print 'Bomb: ', nextstate.getBombScore(x,y)
      print 'Map: ', nextstate.getMapScore(x,y)
      print 'layScore =', layScore
      #layScore = self.evaluationFunction(nstate, (x, y), Actions.directionToVector(Actions.LAY))
    else:
      return random.choice(bestActions)
    #print '\033[1;31m  Return!!!  \033[0m'
    if layScore > originScore and not gamestate.data.map.isBomb((my_x, my_y)):
      print '\033[1;31m  Lay !!!:  \033[0m', layScore
      print '\033[1;31m  Ori !!!:  \033[0m', originScore
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
    f_score = {start:(g_score[start]+manhattanDistance(start,target))}
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
          if manhattanDistance((x,y),target) <= 0.5:
              return (cur_node[0][1]+1,cur_node[0][2])
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

def scoreEvaluation(state,pos,vec,weight=1):
  x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
  return state.getBombScore(x,y) + weight*state.getMapScore(x,y)