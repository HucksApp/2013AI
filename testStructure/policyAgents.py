from game import Agent


class PolicyAgent(Agent):

  def __init__(self,index = 0):
    Agent.__init__(self,index)
    self.policy = None
  
  def getAction(self, state): raiseNotDefined()
  def getActionByDecisionTree(self, state, legal): raiseNotDefined()

class Policy():
  def isPolicyHolds(self, state): raiseNotDefined()
  def generatePolicy(self, state): raiseNotDefined()
  def getActionForPolicy(self, state): raiseNotDefined()


class BasicPolicyAgent(PolicyAgent):

  def getAction(self,state):
   
    # in the movement or legals is only one : dont waste time to calculate
    legals = state.getLegalActions(self.index)
    if len(legals) == 1 : return legals[0]

    if not self.policy is None:
        print 'Agent Mode!!!!!!!!!!!!!!!!:  ', self.policy.__class__
        if self.policy.isPolicyHolds(state):
            return self.policy.getActionForPolicy(state)
        else:
            print 'policy unhold'
            self.policy = None
            return self.getActionByDecisionTree(state,legals)
    else:
        return self.getActionByDecisionTree(state,legals)
