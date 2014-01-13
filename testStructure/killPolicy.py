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
    scored = [(score, action) for score, action in scored if score != None]
    if len(scored) == 0: return False
    self.bestScore = min(scored)[0]
    if self.bestScore == None: 
      return False
    if mystate.getLeftBombNumber() > 0 and mystate.getSpeed() >= 0.25:
      self.bestActions = [pair[1] for pair in scored if pair[0] == self.bestScore]
      successors = [(gamestate.generateSuccessor(self.index,  action , True), action) for action in legals]
      avoidscored = [(self.evaluationFunction(nstate,nearestPoint(mypos),Actions.directionToVector(action)), action) for nstate, action in successors]
      print 'KillPolicy.isPolicyHolds:  avoidscored=', avoidscored
      bestavoidScore = min(avoidscored)[0]
      print 'BestAvoidScore: ', bestavoidScore
      if bestavoidScore > 15:
        return False
      self.bestavoidActions = [pair[1] for pair in avoidscored if pair[0] == bestavoidScore]
      return True
    return False  
      
  def getActionForPolicy(self, gamestate):
    print '\033[1;31m  Execution of Kill Policy!!!  \033[0m'
    # return LAY or the direction of tracing
    legals = gamestate.getLegalActions(self.index)
    if len(legals) == 1: return legals[0]
    (x, y) = nearestPoint(gamestate.getAgentPosition(self.target))
    (my_x, my_y) = nearestPoint(gamestate.getAgentPosition(self.index))
    
    #if bestScore == None: return random.choice(self.bestActions)
    if self.bestScore[0] == 0 and Actions.LAY not in legals:
      ok_legals = []
      for action in legals:
        vec = Actions.directionToVector(action)
        if not gamestate.getMapScore(int(my_x+vec[0]),int(my_y+vec[1])) >= 80:
          ok_legals.append(action)
      if len(ok_legals) == 0: return random.choice(legals)
      return random.choice(ok_legals)
    
    originScore = gamestate.getBombScore(x,y) + gamestate.getMapScore(x,y)
    if Actions.LAY in legals:
      nextstate = gamestate.generateSuccessor(self.index, Actions.LAY, True)
      layScore = nextstate.getBombScore(x,y) + nextstate.getMapScore(x,y)
      #layScore = self.evaluationFunction(nstate, (x, y), Actions.directionToVector(Actions.LAY))
    else:
      print 'Lay not in legal!!'
      ok_legals = []
      for action in self.bestActions:
        vec = Actions.directionToVector(action)
        if not gamestate.getBombScore(int(my_x+vec[0]),int(my_y+vec[1])) >= 30:
          ok_legals.append(action)
      if len(ok_legals) == 0:
        print 'len(ok_legals) == 0'
        return random.choice(legals)
      else:
        print 'len(ok_legals) > 0'
        return random.choice(ok_legals)

    #if layScore > originScore and not gamestate.data.map.isBomb((my_x, my_y)):
    if abs(my_x - x) <= 2 and abs(my_y - y) <= 2 and not gamestate.data.map.isBomb((my_x, my_y)):
      print 'Lay in legal!!'
      return Actions.LAY

    print 'Approach'
    ok_legals = []
    for action in self.bestActions:
      vec = Actions.directionToVector(action)
      if not gamestate.getBombScore(int(my_x+vec[0]),int(my_y+vec[1])) >= 30:
        ok_legals.append(action)
    if len(ok_legals) == 0:
      print 'len(ok_legals) == 0'
      return random.choice(legals)
    else:
      print 'len(ok_legals) > 0'
      return random.choice(ok_legals)
      
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
