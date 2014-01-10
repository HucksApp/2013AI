from game import Agent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util
from util import nearestPoint
from collections import deque


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
    
    scored = [(self.killScore(AgentState,state,AgentPos,ClosestAgent,Actions.directionToVector(action), action), action) for state, action in successors]
    bestScore = max(scored)[0]
    if bestScore == 0:
      return random.choice(legals)
    bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
    return random.choice(bestActions)
  
  def killScore(self,agentstate,state,pos,otherpos,vec,action):      
    # No target bomberman to attack
    if otherpos == (-1, -1) or agentstate.getLeftBombNumber() == 0:
      if action is Actions.LAY:
        return -1
      return 0
      
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
        
  def getAction(self, state):
    # Generate candidate actions
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
  

def scoreEvaluation(state,pos,vec):
  x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
  return state.getBombScore(x,y) + state.getMapScore(x,y)  