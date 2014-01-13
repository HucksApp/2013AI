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
        print util.blue('>>>>>>> Agent #%d Agent Mode!!!!!!!!!!!!!!!!:  %s <<<<<<<' % (self.index, self.policy.__class__))
        print 'Pos!!!!!!!!: ', state.getAgentPosition(self.index)
        if self.policy.isPolicyHolds(state):
            ret = self.policy.getActionForPolicy(state)
            print "Returned action!!!!!!!: ", ret
            return ret 
        else:
            print 'policy unhold'
            self.policy = None
            return self.getActionByDecisionTree(state,legals)
    else:
        return self.getActionByDecisionTree(state,legals)
