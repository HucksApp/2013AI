from game import Agent
from game import Actions
from game import Directions
from avoidPolicy import *
import random
from util import manhattanDistance
import util
from util import nearestPoint
from collections import deque
import math


class BombermanAgent( Agent ):
  def __init__( self, index ):
    self.index = index

  def getAction( self, state ):
    dist = self.getDistribution(state)
    if len(dist) == 0:
      return Directions.STOP
    else:
      return util.chooseFromDistribution( dist )

  def getDistribution(self,state):
    return util.raiseNotDefined

class RandomBomberman( Agent):
  "A ghost that chooses a legal action uniformly at random."

  def getAction( self, state ):
    dist = self.getDistribution(state)
    if len(dist) == 0:
      return Directions.STOP
    else:
      return util.chooseFromDistribution( dist )

  def getDistribution( self, state ):
    dist = util.Counter()
    for a in state.getLegalActions( self.index ): dist[a] = 1.0
    dist.normalize()
    return dist
    
class KillBomberman(Agent):
  def __init__(self, index = 0 , evalFn="scoreEvaluation"):
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.index = index
    assert self.evaluationFunction != None
    
  def getAction(self, state):
    legals = state.getLegalActions(self.index)
    legal = [action for action in legals if not action is Directions.STOP]
    successors = [(state.generateSuccessor(self.index,  action), action) for action in legals]
    AgentState = state.getAgentState(self.index)
    AgentPos = state.getAgentPosition(self.index)
    OtherAgentPos = [state.getAgentPosition(index) for index in range(state.getNumAgents()) if index != self.index ]
    OtherAgentPosInt = [nearestPoint(pos_other) for pos_other in OtherAgentPos]
    
    OtherDict = []
    for index in range(state.getNumAgents()):
      if index != self.index:
        OtherDict.append([nearestPoint(state.getAgentPosition(index)), state.getAgentState(index).getSpeed()])
    
    # BFS for other agent within the threshold
    ClosestAgent = self.BFSOtherAgent(state, AgentPos, OtherAgentPosInt, OtherDict)
    
    #ScoreEval = [self.evaluationFunction(nstate,AgentPos,Actions.directionToVector(action)) for nstate, action in successors]
    #print 'Map and Bomb: ', ScoreEval 
    
    if ClosestAgent == (-1, -1) or AgentState.getLeftBombNumber() == 0:
      scored = [(self.evaluationFunction(nstate,AgentPos,Actions.directionToVector(action)), action) for nstate, action in successors]
      bestScore = min(scored)[0]
      #print 'No bomb or no target'
    else:
      scored = [(self.killScore(AgentState,state,AgentPos,ClosestAgent,Actions.directionToVector(action), action), action) for state, action in successors]
      bestScore = max(scored)[0]
      #print 'With target'
      if bestScore == 0:
        return random.choice(legals)
    #print bestScore
    bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
    return random.choice(bestActions)
  
  def killScore(self,agentstate,state,pos,otherpos,vec,action):      
    # No target bomberman to attack
    #if otherpos == (-1, -1) or agentstate.getLeftBombNumber() == 0:
      #if action is Actions.LAY:
        #return -1
      #return 0
      
    x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
    Dist = manhattanDistance((x,y), otherpos)

    AttackThreshold = 1
    # Attack or Trace
    if Dist <= AttackThreshold and Dist != 0 and action is Actions.LAY:
      return 1
    return -Dist
         
  def BFSOtherAgent(self, gamestate, pos, otherposint, dict):
    threshold = 10
    currmap = gamestate.data.map
    targets = []
    queue = deque()
    visited = set()
    depth = {}
    adjacent_positions = lambda x, y: ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
    
    queue.append((nearestPoint(pos), 0))
    visited.add(nearestPoint(pos))
    while len(queue) != 0:
      (x, y), this_dist = queue.popleft()
      if this_dist > threshold: break
      if (x, y) in otherposint:
        targets.append((x, y))
        depth[(x, y)] = this_dist
      for adjpos in adjacent_positions(x, y):
        if (not currmap.isBlocked(adjpos) and
            adjpos[0] in range(currmap.width) and
            adjpos[1] in range(currmap.height) and
            adjpos not in visited):
          queue.append((adjpos, this_dist + 1))
          visited.add(adjpos)

    eval = float('inf')
    min = (-1, -1)
    for i in range(len(dict)):
      if dict[i][0] in targets:
        if depth[dict[i][0]]/dict[i][1] < eval:
          eval = depth[dict[i][0]]/dict[i][1]
          min = otherposint[i]
    return min

class AvoidBomberman(Agent):
  def __init__(self, index = 0 , evalFn="scoreEvaluation"):
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.index = index
    assert self.evaluationFunction != None
    self.policy = None

  def getAction(self, state):
    # Generate candidate actions
    if self.policy is None:
        legals = state.getLegalActions(self.index)
        if len(legals) == 1 : return legals[0]
        #if Directions.STOP in legals: legal .remove(Directions.STOP)
        legal = [action for action in legals if not action is Directions.STOP]
    
        pos = state.getAgentPosition(self.index)
        successors = [(state.generateSuccessor(self.index,  action , True), action) for action in legals]
        if len(successors) is 0: return random.choice(legals)
        scored = [(self.evaluationFunction(nstate,pos,Actions.directionToVector(action)), action) for nstate, action in successors]
        self.policy = AvoidPolicy(self.index,legals,scored)
        return self.policy.getActionForPolicy(state)
    else:
        if self.policy.isPolicyHolds(state):
     	    return self.policy.getActionForPolicy(state)

class TerroristBomberman(Agent):
  """
  An agent that perfers to put bombs near blocks
  """
  def __init__(self, index=0, *_, **__):
    self.index = index

  def getAction(self, state):
    # If there is only one legal action, return it.
    legal_actions = state.getLegalActions(self.index)
    if len(legal_actions) == 1:
      return legal_actions[0]

    # If the list of legal actions containing STOP, remove STOP.
    if Directions.STOP in legal_actions:
      legal_actions.remove(Directions.STOP)

    # Generate new states for all legal actions.
    successors = [(
        state.generateSuccessor(self.index, action, True), action
        ) for action in legal_actions]

    # Get scores for all new states.
    currpos = state.getAgentPosition(self.index)
    scored = [(
        terroristEvaluation(newstate, currpos, self.index), action
        ) for newstate, action in successors]

    # Return one action with the highest score
    bestScore = max(scored)[0]
    bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
    ret = random.choice(bestActions)
    return ret

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
        hungryEvaluation(nstate, _currpos, self.index), action
        ) for nstate, action in successors]
    ###print 'scored=',scored,
    bestScore = max(scored)[0]
    bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
    ret = random.choice(bestActions)
    ###print ' choose ', ret
    print
    return ret

def scoreEvaluation(state,pos,vec):
  x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
  return state.getBombScore(x,y) + state.getMapScore(x,y)  
