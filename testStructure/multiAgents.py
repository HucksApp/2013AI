# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """


  def getAction(self, gameState):
    """
    You do not need to change this method, but you're welcome to.

    getAction chooses among the best options according to the evaluation function.

    Just like in the previous project, getAction takes a GameState and returns
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    "Add more of your code here if you want to"

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design a better evaluation function here.

    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (oldFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    oldFood = currentGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    "*** YOUR CODE HERE ***"
    score = successorGameState.getScore()
    for ghost in newGhostStates:
        if ghost.scaredTimer <= 0:
            d = manhattanDistance(newPos,ghost.getPosition())
            if d < 5:
                score += d*2
    min = 300
    for capsule in currentGameState.getCapsules():
        d = manhattanDistance(newPos,capsule)
        if d < min:
            min = d
    if min < 0.5:
        score += 50
    else:
        score -= min
    min = 300
    foods = oldFood.asList(True)
    for pos in foods:
        d = manhattanDistance(newPos,pos)
        if d < min:
            min = d
    if min > 0.5:
        if len(foods) > 5:
            score -= min*2
        else:
            score -= min*5

    return score

def scoreEvaluationFunction(currentGameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)


def getMinSuccessor(gameState,N_ghost,iter):
  legal = gameState.getLegalActions(1)
  if len(legal) <= iter%4:
    return None
  successor = gameState.generateSuccessor(1,legal[iter%4])
  if N_ghost>1:
    for ghost in range(2,N_ghost+1):
        if successor.isLose():
            return successor
        legal = successor.getLegalActions(ghost)
        if len(legal) <= iter/(4**(ghost-1))%4:
            return None
        successor = successor.generateSuccessor(ghost,legal[iter/(4**(ghost-1))%4])
  return successor


class MinimaxAgent(MultiAgentSearchAgent):
  """
    Your minimax agent (question 2)
  """

  def miniMax(self,gameState, depth, Maxplayer):
    if depth == 0 or gameState.isWin() or gameState.isLose():
        return self.evaluationFunction(gameState)
    #cnt = 0
    if Maxplayer == 1:
        bestScore = -100000
        legal = gameState.getLegalActions(0)
        for action in [x for x in legal if x != Directions.STOP]:
            successor = gameState.generateSuccessor(0, action)
            score = self.miniMax(successor,depth,0)
            self.cnt = self.cnt +1
            if score > bestScore:
                bestScore = score
                bestAction = action
        if depth == self.depth:
            return bestScore,bestAction
        else:
            return bestScore
    else:
        bestScore = 100000
        n_ghost = gameState.getNumAgents()-1
        for iter in range(0,4**n_ghost):
            successor = getMinSuccessor(gameState,n_ghost,iter)
            if successor is not None:
                score = self.miniMax(successor,depth-1,1)
                self.cnt = self.cnt +1
                if score < bestScore:
                    bestScore = score
        return bestScore

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    "*** YOUR CODE HERE ***"
    self.cnt = 0
    score, action = self.miniMax(gameState,self.depth,1)
    return action


class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """

  def alphaBeta(self,gameState, depth,alpha,beta, Maxplayer):
    if depth == 0 or gameState.isWin() or gameState.isLose():
        return self.evaluationFunction(gameState)
    #cnt = 0
    if Maxplayer == 1:
        legal = gameState.getLegalActions(0)
        for action in [x for x in legal if x != Directions.STOP]:
            successor = gameState.generateSuccessor(0, action)
            score = self.alphaBeta(successor,depth,alpha,beta,0)
            self.cnt = self.cnt +1
            if score > alpha:
                bestAction = action
                alpha = score
                if alpha >= beta:
                    break

        if depth == self.depth:
            return alpha,bestAction
        else:
            return alpha
    else:
        n_ghost = gameState.getNumAgents()-1
        for iter in range(0,4**n_ghost):
            successor = getMinSuccessor(gameState,n_ghost,iter)
            if successor is not None:
                score = self.alphaBeta(successor,depth-1,alpha,beta,1)
                self.cnt = self.cnt +1
                if score < beta:
                    beta = score
                    if beta <= alpha:
                        break

        return beta

  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    self.cnt = 0
    score, action = self.alphaBeta(gameState,self.depth,float("-infinity"),float("infinity"),1)
    return action

class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Your expectimax agent (question 4)
  """

  def ExpectminiMax(self,gameState, depth, Maxplayer):
    if depth == 0 or gameState.isWin() or gameState.isLose():
        return self.evaluationFunction(gameState)
    if Maxplayer == 1:
        bestScore = -100000
        legal = gameState.getLegalActions(0)
        bestAction = Directions.STOP
        for action in [x for x in legal if x != Directions.STOP]:
            successor = gameState.generateSuccessor(0, action)
            score = self.ExpectminiMax(successor,depth,0)
            self.cnt = self.cnt +1
            if score > bestScore:
                bestScore = score
                bestAction = action
        if depth == self.depth:
            return bestScore,bestAction
        else:
            return bestScore
    else:
        bestScore = 0
        ave = 0
        n_ghost = gameState.getNumAgents()-1
        for iter in range(0,4**n_ghost):
            successor = getMinSuccessor(gameState,n_ghost,iter)
            if successor is not None:
                score = self.ExpectminiMax(successor,depth-1,1)
                self.cnt = self.cnt +1
                ave = ave + 1
                bestScore = bestScore + score
        bestScore = bestScore/ave
        return bestScore

  def getAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    "*** YOUR CODE HERE ***"
    self.cnt = 0
    score, action = self.ExpectminiMax(gameState,self.depth,1)
    return action

def disCmp(x,y,newPos):
  if (util.manhattanDistance(newPos, x)-util.manhattanDistance(newPos, y))<0: return -1
  else:
      if (util.manhattanDistance(newPos, x)-util.manhattanDistance(newPos, y))>0: return 1
      else:
          return 0

def actualDistance(gameState, target):
  from game import Directions
  from game import Actions

  walls = gameState.getWalls()
  start = gameState.getPacmanPosition()
  closedSet = []
  openSet = [[(start,0),0]]

  g_score = {start:0}
  f_score = {start:(g_score[start]+util.manhattanDistance(start,target))}
  while len(openSet):
    openSet.sort(key=lambda x:x[1])
    cur_node = openSet[0]
    if util.manhattanDistance(cur_node[0][0],target) < 0.8:
        return cur_node[0][1]

    openSet.pop(0)
    closedSet.append(cur_node)
    for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        x,y = cur_node[0][0]
        dx,dy = Actions.directionToVector(action)
        if not walls[int(x+dx)][int(y+dy)]:
            node = ((int(x+dx),int(y+dy)),cur_node[0][1]+1)
            tentative_g = g_score[cur_node[0][0]]+1
            tentative_f = tentative_g + util.manhattanDistance(node[0],target)
            if node[0] in [x[0][0] for x in closedSet] and tentative_f >=f_score[node[0]]:
                continue
            if node[0] not in [x[0][0] for x in openSet] or tentative_f < f_score[node[0]]:
                g_score.update({node[0]:tentative_g})
                f_score.update({node[0]:tentative_f})
                if node[0] not in [x[0][0] for x in openSet]:
                    openSet.append([node,tentative_f])
  return None

def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
  """
  "*** YOUR CODE HERE ***"
  if currentGameState.isLose():
      return -1e307
  if currentGameState.isWin() :
      return 1e307
  returnScore= 0.0
  newPos = currentGameState.getPacmanPosition()

  # Obtain all ghost positions on the board
  GhostStates = currentGameState.getGhostStates()
  GhostStates.sort(lambda x,y: disCmp(x.getPosition(),y.getPosition(),newPos))
  GhostPositions = [Ghost.getPosition() for Ghost in GhostStates]

  # Obtain scared Ghosts informations
  newScaredTimes = [ghostState.scaredTimer for ghostState in GhostStates]
  closestGhost=GhostStates[0]

  # Sort the food list and find the closest food to Pacman
  FoodList = currentGameState.getFood().asList()
  minPos = FoodList[0]
  minDist = util.manhattanDistance(minPos, newPos)
  for food in FoodList:
      curDist = util.manhattanDistance(food, newPos)
      if curDist==1 :
          minPos=food
          minDist=curDist
          break
      if (curDist < minDist):
          minDist = curDist
          minPos = food

  # Find the actual distance to the estimated nearest food
  closestFoodDistance = actualDistance(currentGameState, minPos)

  # Find the actual distance to the closest Scared Ghost and the closest Normal Ghost
  closestScaredGhostDist=1e307
  closestScaredGhost=None
  closestNormalGhostDist=1e307
  closestNormalGhost=None

  allScaredGhost=[Ghost for Ghost in GhostStates if Ghost.scaredTimer>0]
  allRealScaredGhostDistance=[actualDistance(currentGameState,Pos) for Pos in [ScaredGhost.getPosition() for ScaredGhost in allScaredGhost]]
  allDistScaredGhosts=allRealScaredGhostDistance
  if len(allDistScaredGhosts)!=0:
      closestScaredGhostDist=min(allDistScaredGhosts)
      closestScaredGhost=allScaredGhost[allDistScaredGhosts.index(closestScaredGhostDist)]
      #print 'ScardGhost:',closestScaredGhostDist,' in:',allDistScaredGhosts,' for :',[Pos for Pos in [ScaredGhost.getPosition() for ScaredGhost in allScaredGhost]],' when pacman in:',newPos

  allNormalGhost=[Ghost for Ghost in GhostStates if Ghost.scaredTimer<=0]
  allRealNormalGhostDistance=[actualDistance(currentGameState,Pos) for Pos in [NormalGhost.getPosition() for NormalGhost in allNormalGhost]]
  allDistNormalGhosts=allRealNormalGhostDistance
  if len(allDistNormalGhosts)!=0:
      closestNormalGhostDist=min(allDistNormalGhosts)
      closestNormalGhost=allNormalGhost[allDistNormalGhosts.index(closestNormalGhostDist)]

  # Default weights for food, normalghost, scaredghost
  wFood, wGhost, wScaredGhost       = [2.0, -6.0, 5.0];

  # if the closest ghost ate Pacman
  if (closestNormalGhostDist==0):
      return -1e307
  if (closestScaredGhostDist==0):
      closestScaredGhostDist=0.1

  # assign weight for food, normalghost, scaredghost in different conditions
  if (closestNormalGhostDist > 2):
      if closestScaredGhost!=None:
          if (closestScaredGhostDist<closestScaredGhost.scaredTimer):
              if(closestScaredGhostDist<7):
                  wFood, wGhost, wScaredGhost= [0.0, -0.0,10.0];
              else:
                  if(closestScaredGhostDist<12):
                      wFood, wGhost, wScaredGhost= [3.0, 0.0, 9.0];
                  else :
                      wFood, wGhost, wScaredGhost= [3.0, 0.0, 2.0];
          else:
              wFood, wGhost, wScaredGhost = [4.0, -0.0, 1.0];
      else :
          wFood, wGhost, wScaredGhost = [4.0, -0.0, 0.0];
  else:
      if (closestScaredGhostDist<5):
          if (closestScaredGhost.scaredTimer>5):
              wFood, wGhost, wScaredGhost= [1.0, -6.0, 4.0];
          else:
              wFood, wGhost, wScaredGhost= [1.0, -6.0, 1.5];
      else:
          wFood, wGhost, wScaredGhost= [1.0, -6.0, 1.0];

  """if len(FoodList) < 3   :
      wFood, wGhost, wScaredGhost= [6.0, -8.0, 5.0];
  else:
     if len(FoodList) < 2:
         wFood, wGhost, wScaredGhost= [8.0, -8.0, 5.0];"""
  #print 'FoodDistance:',closestFoodDistance,'  closestNormalGhostDist:',closestNormalGhostDist,' closestScaredGhostDist:',closestScaredGhostDist
  returnScore=(wFood/(closestFoodDistance)+(wGhost)/closestNormalGhostDist+(wScaredGhost)/(closestScaredGhostDist))+currentGameState.getScore()

  return returnScore

# Abbreviation
better = betterEvaluationFunction

