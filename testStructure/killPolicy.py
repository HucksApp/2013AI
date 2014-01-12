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
    
  def isPolicyConditionHolds(self, gamestate):
    enemypos = gamestate.getAgentPosition(self.target)
    mypos = gamestate.getAgentPosition(self.index)
    enemystate = gamestate.getAgentState(self.target)
    mystate = gamestate.getAgentState(self.index)
    if mystate.getLeftBombNumber() >= 2 and mystate.getSpeed() >= 0.33:
      return True
    return False  
      
  def getActionForPolicy(self, gamestate):
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

def scoreEvaluation(state,pos,vec,weight=1):
  x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
  return state.getBombScore(x,y) + weight*state.getMapScore(x,y)