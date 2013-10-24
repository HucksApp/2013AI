# search.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
In search.py, you will implement generic search algorithms which are called 
by Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
  """
  This class outlines the structure of a search problem, but doesn't implement
  any of the methods (in object-oriented terminology: an abstract class).
  
  You do not need to change anything in this class, ever.
  """
  
  def getStartState(self):
     """
     Returns the start state for the search problem 
     """
     util.raiseNotDefined()
    
  def isGoalState(self, state):
     """
       state: Search state
    
     Returns True if and only if the state is a valid goal state
     """
     util.raiseNotDefined()

  def getSuccessors(self, state):
     """
       state: Search state
     
     For a given state, this should return a list of triples, 
     (successor, action, stepCost), where 'successor' is a 
     successor to the current state, 'action' is the action
     required to get there, and 'stepCost' is the incremental 
     cost of expanding to that successor
     """
     util.raiseNotDefined()

  def getCostOfActions(self, actions):
     """
      actions: A list of actions to take
 
     This method returns the total cost of a particular sequence of actions.  The sequence must
     be composed of legal moves
     """
     util.raiseNotDefined()
           

def tinyMazeSearch(problem):
  """
  Returns a sequence of moves that solves tinyMaze.  For any other
  maze, the sequence of moves will be incorrect, so only use this for tinyMaze
  """
  from game import Directions
  s = Directions.SOUTH
  w = Directions.WEST
  return  [s,s,w,s,w,w,s,w]

def depthFirstSearch(problem):
  """
  Search the deepest nodes in the search tree first [p 74].
  
  Your search algorithm needs to return a list of actions that reaches
  the goal.  Make sure to implement a graph search algorithm [Fig. 3.18].
  
  To get started, you might want to try some of these simple commands to
  understand the search problem that is being passed in:
  
  print "Start:", problem.getStartState()
  print "Is the start a goal?", problem.isGoalState(problem.getStartState())
  print "Start's successors:", problem.getSuccessors(problem.getStartState())
  """
  "*** YOUR CODE HERE ***"
  start = problem.getStartState()

  stack = util.Stack()
  _explored = [start]
  stack.push((start,0,0))
  successors = {}
  res = []
  while not stack.isEmpty():
	flag = 0
	cur_node = stack.pop()
	if problem.isGoalState(cur_node[0]):
		break;
	if cur_node[0] not in successors:
		successors.update({cur_node[0]:problem.getSuccessors(cur_node[0])})

	for node in successors[cur_node[0]]:
		if node[0] not in _explored:
			stack.push(cur_node)
			stack.push(node)
			_explored.append(node[0])
			res.append(node[1])
			flag = 1
			break
	
	if flag == 0:
		_explored.append(cur_node[0])
		if len(res)>0:
			res.pop()
	
  return res
  
def breadthFirstSearch(problem):
	"Search the shallowest nodes in the search tree first. [p 74]"
	"*** YOUR CODE HERE ***"
	start = problem.getStartState()
  
	queue = util.Queue()
	_visited = []
	queue.push((start,0,0))
	_visited.append(start)
	pa = {start:-1}
	while not queue.isEmpty():
		node = queue.pop()
		if problem.isGoalState(node[0]):
			parent = node
			break
		for n in problem.getSuccessors(node[0]):
			if (n[0]) not in _visited:
				_visited.append((n[0]))
				queue.push(n)
				pa.update({n[0]:node})
			
	
	path = [parent[1]]
	while pa[parent[0]]!=-1 and pa[parent[0]][1]!=0:
		parent = pa[parent[0]]
		path.append(parent[1])
	path.reverse()
	
	return path

def uniformCostSearch(problem):
  "Search the node of least total cost first. "
  "*** YOUR CODE HERE ***"
  start = problem.getStartState()
  
  frontier = [[(start,0,0),0]]
  _vertex = []
  pa = {start:-1};
  while not len(frontier) == 0:
	frontier.sort(key=lambda x:x[1])
	node = frontier.pop(0)
	if problem.isGoalState(node[0][0]):
		parent = node[0]
		break
	_vertex.append(node[0][0])

	for successor in sorted(problem.getSuccessors(node[0][0]),key=lambda x:x[2]):
		if successor[0] not in _vertex:
			if successor[0] not in [n[0][0] for n in frontier]:
				frontier.append([successor,(successor[2]+node[1])])
				pa.update({successor[0]:node[0]})
			else:
				a = filter(lambda x:frontier[x][0][0] == successor[0] and frontier[x][1] > (successor[2]+node[1]),xrange(len(frontier)))
				if len(a) > 0:
					frontier[a[0]] = [successor,(successor[2]+node[1])]
				
  
  res = [parent[1]]
  while pa[parent[0]] != -1 and pa[parent[0]][1]!=0:
	parent = pa[parent[0]]
	res.append(parent[1])
  res.reverse()

  return res
  

def nullHeuristic(state, problem=None):
  """
  A heuristic function estimates the cost from the current state to the nearest
  goal in the provided SearchProblem.  This heuristic is trivial.
  """
  return 0

def aStarSearch(problem, heuristic=nullHeuristic):
  "Search the node that has the lowest combined cost and heuristic first."
  "*** YOUR CODE HERE ***"
  start = problem.getStartState()
  closedSet = []
  openSet = [[(start,0,0),0]]
  pa = {start:-1}
  
  g_score = {start:0}
  f_score = {start:(g_score[start]+heuristic(start,problem))}
  while len(openSet):
	openSet.sort(key=lambda x:x[1])
	cur_node = openSet[0]
	if problem.isGoalState(cur_node[0][0]):
		parent = cur_node[0]
		break
	
	openSet.pop(0)
	closedSet.append(cur_node)
	for node in problem.getSuccessors(cur_node[0][0]):
		tentative_g = g_score[cur_node[0][0]]+node[2]
		tentative_f = tentative_g + heuristic(node[0],problem)
		if node[0] in [x[0][0] for x in closedSet] and tentative_f >=f_score[node[0]]:
			continue
		if node[0] not in [x[0][0] for x in openSet] or tentative_f < f_score[node[0]]:
			pa.update({node[0]:cur_node[0]})
			g_score.update({node[0]:tentative_g})
			f_score.update({node[0]:tentative_f})
			if node[0] not in [x[0][0] for x in openSet]:
				openSet.append([node,tentative_f])
	
  res = [parent[1]]
  while pa[parent[0]] != -1 and pa[parent[0]][1]!=0:
	parent = pa[parent[0]]
	res.append(parent[1])
  res.reverse()

  return res
    
  
# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
