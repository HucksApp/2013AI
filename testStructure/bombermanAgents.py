from game import Agent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util
import math
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

class HungryBomberman(Agent):
  """
  An agent that perfers to eat items
  """
  def __init__(self, index=0, *_, **__):
    self.index = index

  def getAction(self, state):
    legals = state.getLegalActions(self.index)
    legal = [action for action in legals if action is not Actions.LAY and action is not Directions.STOP]
    pos = state.getAgentPosition(self.index)
    successors = [(state.generateSuccessor(self.index, action, True), action) for action in legal]
    if len(successors) is 0: return Directions.STOP
    if len(successors) is 1: return successors[0][1]
    scored = [(
        hungryEvaluation(nstate, pos, self.index), action
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

def hungryEvaluation(nstate, oldpos, agentIdx):
  """
  NOTE: Currently, does not consider enemy's distance to the items
  """
  # Caculate the difference between new and old positions
  # And then caculate the target position
  ox, oy = oldpos
  # FIXME Bug? getAgentPosition() returns grid position, not float ones...
  nx, ny = nstate.getAgentPosition(agentIdx)
  dx, dy = nx - ox, ny - oy

  #tx = int(ox) if dx == 0 else (int(math.ceil(nx)) if dx > 0 else int(math.floor(nx)))
  #ty = int(oy) if dy == 0 else (int(math.ceil(ny)) if dx > 0 else int(math.floor(ny)))
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

