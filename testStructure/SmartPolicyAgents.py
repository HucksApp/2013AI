from util import *
from game import Agent
from game import Actions
from game import Directions
from policyAgents import *
from hungryPolicy import HungryPutBombPolicy
from killPolicy import KillPolicy
from avoidPolicy import AvoidPolicy
import operator

class SmartPolicyAgent(BasicPolicyAgent):

  THRESHOLD_TABLE = [12,6,3,2]
  
  ABILITY_THRESHOLD = [4.0,0.5,5.0]  # (1~8),(0.25~1),(3~10)
  
  DANGER_BOMB_SCORE_THRESHOLD = 36

  def getActionByDecisionTree(self,state,legals):
    print blue('\n============ ENTER getActionByDecisionTree: agent #%d =============='% self.index)
	# BFS for the closest enemy [record the steps and the position index]
    pos = state.getAgentPosition(self.index)
    print 'agent pos =', pos
    if state.data.BombScore[int(pos[0])][int(pos[1])] > self.DANGER_BOMB_SCORE_THRESHOLD + (state.getAgentState(self.index).getSpeed()-0.25)*5:
        print red('>>>>>>> Current situation contains the danger of bomb explosion')
        legal = [l for l in legals if l not in [Actions.LAY]]
        successors = [(state.generateSuccessor(self.index,  action , True), action) for action in legal] 
        if len(successors) is 0:
            ret = random.choice(legals)		
            print cyan('RET1 randomly returns %s' % ret)
            return ret
        scored = [(scoreEvaluation(nstate,pos,Actions.directionToVector(action), 0.4) + 100*(state.data._eaten[self.index] - nstate.data._eaten[self.index]), action
            ) for nstate, action in successors]
        bestScore = min(scored)[0]
        if bestScore > self.DANGER_BOMB_SCORE_THRESHOLD :
            print 'Execute Emergency Avoid Policy'
            self.policy = AvoidPolicy(self.index, legals, scored)
            return self.policy.getActionForPolicy(state)
			
        bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
        ret = random.choice(bestActions)		
        print cyan('RET2 randomly returns %s' % ret)
        return ret

    print green('>>>>>>> Current position is safe without danger')
    threshold = self.THRESHOLD_TABLE[state.getAgentState(self.index).speed]
    res = BFSForClosestEnemy(state,self.index,threshold)

    if res is None or res[2] > threshold:
    # no visable enemies  	
        print 'Safe mode'
        ability = [state.getAgentState(self.index).getBombPower(),state.getAgentState(self.index).getSpeed(),state.getAgentState(self.index).Bomb_Total_Number]
        ishungry = [ (ability[i]-self.ABILITY_THRESHOLD[i])/self.ABILITY_THRESHOLD[i] for i in range(len(self.ABILITY_THRESHOLD))]
        steps = [(lambda x: None if x < 0 else False)(x) for x in ishungry]
        print steps
      	BFSForClosestItems(state,self.index,steps,threshold)
        if any(steps) :
		# there is a path to the wanted items
            target = 0
            minCost = 0
            for i in range(len(ishungry)):
                if not steps[i] in [None, False]:
                    if minCost > ishungry[i]/steps[i][2]: # min(ishungry / steps)
                        target = i 
                        minCost = ishungry[i]/steps[i][2]
            print 'Chase item:',steps[target],'ishungry:',ishungry
            self.policy = EatItemPolicy(steps[target][1],self.index,steps[target][0])
            ret = self.policy.getActionForPolicy(state)
            print cyan('RET3 By EatItemPolicy, returns %s' % ret)
            return ret
        elif not ( None in steps or res is None ):
        # ability is full and want to get close to the enemy
            ret = res[1]
            print cyan('RET4 returns %s' % ret)
            return ret
        else:
        # there is no path to any items and ability is low or no reachable enemies, need to find a box to lay a bomb (policy)
            print 'should apply Find box policy'
            self.policy = HungryPutBombPolicy(self.index)
            self.policy.generatePolicy(state)
            if self.policy.isPolicyHolds(state):
                ret = self.policy.getActionForPolicy(state)
                print cyan('RET5 returns %s' % ret)
                return ret
            else:
                self.policy = None
                print 'Hungry mode not hold condition'
                legal = [l for l in legals if l not in [Actions.LAY]]
                successors = [(state.generateSuccessor(self.index,  action , True), action) for action in legal] 
                if len(successors) is 0:
                    ret = random.choice(legals)
                    print cyan('RET6 returns %s' % ret)
                    return ret
                scored = [(scoreEvaluation(nstate,pos,Actions.directionToVector(action),1) + 100*(state.data._eaten[self.index] - nstate.data._eaten[self.index]), action
                    ) for nstate, action in successors]
                bestScore = min(scored)[0]
                bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
                ret = random.choice(bestActions)
                print cyan('RET7 returns %s' % ret)
                return ret
            

    else:
    # in first danger mode 
        target, action, distance = res
        print 'in first danger mode: dis=',distance
        if state.getAgentState(self.index).getSpeed() >= state.getAgentState(target).getSpeed() - 0.05 and state.getAgentState(self.index).hasBomb():
            # can battle!!
            print 'apply battle mode : KillPolicy'
            self.policy = KillPolicy(self.index,target)
            ret = self.policy.getActionForPolicy(state)
            print cyan('RET9 returns %s' % ret)
            return ret
        else:
            print 'just avoid the danger or run away!!'
            # run away or avoid!!!!
            rev_action = Actions.reverseDirection(action)
            #if rev_action in legals:
            #    return rev_action
            successors = [(state.generateSuccessor(self.index,  action , True), action) for action in legals] 
            if len(successors) is 0:
                ret = random.choice(legals)
                print cyan('RET10 returns %s' % ret)
                return ret
            scored = [(scoreEvaluation(nstate,pos,Actions.directionToVector(action),1) + 100*(state.data._eaten[self.index] - nstate.data._eaten[self.index]), action
                ) for nstate, action in successors]
            bestScore = min(scored)[0]
            bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
            if rev_action in bestActions:
                ret = rev_action
                print cyan('RET11 returns %s' % ret)
                return ret
            ret = random.choice(bestActions)        
            print cyan('RET12 returns %s' % ret)
            return ret
	
	
	
def scoreEvaluation(state,pos,vec,weight=1):
  x,y = int(pos[0]+vec[0]),int(pos[1]+vec[1])
  return state.getBombScore(x,y) + weight*state.getMapScore(x,y)

	
class EatItemPolicy(Policy):

  DANGER_BOMB_SCORE_THRESHOLD = 28

  def __init__(self,route,index,target):
    if route is None or len(route) == 0 :
	    raise Exception('Cannot construct a EatItemPolicy with null route')
    self.route  = route
    self.progress = 0
    self.index = index
    self.target = target
    

  def isPolicyHolds(self, state):
    if self.route is None or len(self.route) == 0 or len(self.route) == self.progress: return False # policy end
    if not state.data.map.isItem(self.target) : return False  # target missing
    pos = nearestPoint(state.getAgentPosition(self.index))
    vec = Actions.directionToVector(self.route[self.progress])
    if state.data.BombScore[int(pos[0]+vec[0])][int(pos[1]+vec[1])] > self.DANGER_BOMB_SCORE_THRESHOLD:
        if state.data.BombScore[pos[0]][pos[1]] > self.DANGER_BOMB_SCORE_THRESHOLD: # cannot stop here, too danger
            return False
        self.route.insert(self.progress,Directions.STOP)
    return True

  def getActionForPolicy(self, state):
    self.progress += 1
    return self.route[self.progress-1]
    
	
	
	
def BFSForClosestEnemy(state,index,th= 10):

  start = state.getAgentPosition(index)
  start = nearestPoint(start)

  targets = []
  for i in range(state.getNumAgents()):
    if i != index and state.data._eaten[i] != 0:
        targets.append((nearestPoint(state.getAgentPosition(i)),i))
  frontier = [[(start,Directions.STOP),0]]
  _vertex = []
  while not len(frontier) == 0:
    frontier.sort(key=lambda x:x[1])
    node = frontier.pop(0)
    #for t,i in targets:
        #if node[0][0] == t:
            #return (i,node[0][1])
        
    _vertex.append(node[0][0])

    for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        x,y = node[0][0]
        vec = Actions.directionToVector(action)
        x,y = int(x+vec[0]),int(y+vec[1])
        if not state.data.map.isBlocked((x,y)) and (x,y) not in _vertex:
            scoreChange = 1 #+ (state.data.MapScore[x][y]+state.data.BombScore[x][y])/20
            #if node[1] + scoreChange > th : continue
            if (x,y) not in [n[0] for n in frontier]:
                for t,i in targets:
                    if (x,y) == t:
                        return (i,node[0][1],node[1]+1)
                if node[0][1] == Directions.STOP:
                 	frontier.append([((x,y),action),node[1]+scoreChange])
                else :
                    frontier.append([((x,y),node[0][1]),node[1]+scoreChange])
            else:
                a = filter(lambda x:frontier[x][0][0] is (x,y) and frontier[x][1] > (scoreChange+node[1]),xrange(len(frontier)))
                if len(a) > 0:
                    frontier[a[0]] = [((x,y),node[0][1]),(scoreChange+node[1])]
        elif state.data.map.isBomb((x,y)) and (x,y) not in _vertex:
            if node[1] + 1 > th : continue
            for t,i in targets:
                if (x,y) == t:
                    return (i,node[0][1],node[1]+1)
            
  return None

def BFSForClosestItems(state,index,steps,th= 10):

  start = state.getAgentPosition(index)
  start = nearestPoint(start)
  
  frontier = [[(start,[]),0]]
  _vertex = []
  while not len(frontier) == 0:
    frontier.sort(key=lambda x:x[1])
    node = frontier.pop(0)
    if (steps[0] is None) and state.data.map[node[0][0][0]][node[0][0][1]] == 1 : # find closest POWER UP
        if state.data.MapScore[node[0][0][0]][node[0][0][1]] < 80:
            steps[0] = (node[0][0],node[0][1],node[1])
    elif (steps[1] is None) and state.data.map[node[0][0][0]][node[0][0][1]] == 2: # find closest SPEED UP
        if state.data.MapScore[node[0][0][0]][node[0][0][1]] < 80:
            steps[1] = (node[0][0],node[0][1],node[1])
    elif (steps[2] is None) and state.data.map[node[0][0][0]][node[0][0][1]] == 3: # find closest NUMBER UP
        if state.data.MapScore[node[0][0][0]][node[0][0][1]] < 80:
            steps[2] = (node[0][0],node[0][1],node[1])
    elif not None in steps:
        return steps
		
    _vertex.append(node[0][0])

    for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        x,y = node[0][0]
        vec = Actions.directionToVector(action)
        x,y = int(x+vec[0]),int(y+vec[1])
        if not state.data.map.isBlocked((x,y)) and (x,y) not in _vertex:
            scoreChange = 1 #+ (state.data.MapScore[x][y]+state.data.BombScore[x][y])/20
            if node[1] + scoreChange > th : continue
            if (x,y) not in [n[0] for n in frontier]:
              	frontier.append([((x,y),node[0][1]+[action]),node[1]+scoreChange])
            else:
                a = filter(lambda x:frontier[x][0][0] is (x,y) and frontier[x][1] > (scoreChange+node[1]),xrange(len(frontier)))
                if len(a) > 0:
                    frontier[a[0]] = [((x,y),node[0][1]),(scoreChange+node[1])]
  return steps
  
def actualDistance(state, pos , target_index , vec = (0,0)):
 
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
            scoreChange = 1+(state.data.MapScore[x][y]+state.data.BombScore[x][y])/20
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
