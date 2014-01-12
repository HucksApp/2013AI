from policyAgents import Policy
from util import *
import random
from collections import deque
from game import Agent, AgentState, Actions, Directions

class AvoidPolicy(Policy):

  SAFE_THRESHOLD = 20

  def __init__(self,index,legals,scored):
    self.index = index
    self.legals = legals
    self.scored = scored

  def isPolicyHolds(self, state):

    legal = [l for l in self.legals if l not in [Actions.LAY]]
    successors = [(state.generateSuccessor(self.index,  action , True), action) for action in legal] 
    if len(successors) is 0: 
        print 'WARNING: This situation should not occur!'
        return True
    pos = state.getAgentPosition(self.index)
    self.scored = [(scoreEvaluation(nstate,pos,Actions.directionToVector(action),0.4) + 100*(state.data._eaten[self.index] - nstate.data._eaten[self.index]), action
        ) for nstate, action in successors]
    bestScore = min(self.scored)[0]
    if bestScore > self.SAFE_THRESHOLD:
        return True
    return False

  def getActionForPolicy(self, state):
    action = None
    step = 1.0
    while action is None and step <= 3:
        action = self.BFSforSafeState(state,self.index,self.SAFE_THRESHOLD*step)
        step+=0.5

    if action is not None:
        print 'BFS found first route by first action:', action
        return action
    else:
        print 'BFS cannot find path to reduce '
        legal = [l for l in self.legals if l not in [Actions.LAY]]
        bestScore = min(self.scored)[0]
        bestActions = [pair[1] for pair in self.scored if pair[0] == bestScore]
        ret = random.choice(bestActions)
        print cyan('RETNN randomly returns %s' % ret)
        return ret        
	
  def BFSforSafeState(self,state,index,th = 25, layer = 8):
  
    start = state  
    queue, visited = deque(), set()
    queue.append([(start,None),0])
    visited.add(start)
    res = []
    while not len(queue) == 0:
      node = queue.popleft()

      if node[1] > layer : continue
      elif node[1] == layer :
        res.append((scoreEvaluation(node[0][0],node[0][0].getAgentPosition(index),(0,0),0.4),node[0][1]))
	  
      for action in [l for l in node[0][0].getLegalActions(index) if l is not Actions.LAY]:
        nstate = node[0][0].generateSuccessor(index,action,True)
        if ( not nstate.data._eaten[index] < node[0][0].data._eaten[index] ) and ( nstate not in visited ):
          visited.add(nstate)
          if node[0][1] is None:
           	queue.append([(nstate,action),node[1]+1])
          else :
            queue.append([(nstate,node[0][1]),node[1]+1])
    
    if len(res) == 0 : return None
    best = min(res)[0]
    bestActions = [pair[1] for pair in res if pair[0] == best]
    print  bestActions
    return random.choice(bestActions)

def scoreEvaluation(state,pos,vec,weight=1):
  x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
  return state.getBombScore(x,y) + weight*state.getMapScore(x,y)	