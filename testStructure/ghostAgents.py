from game import Agent
from game import TeamManagerAgent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util

class IndependentTeamManager( TeamManagerAgent ):

  def __init__(self, team_index , agents, index):
    print 'team:',team_index,' agents:',index
    TeamManagerAgent.__init__(self, team_index, agents, index)

  def getActions(self, state):
    actions = {}
    for index, agentIndex in enumerate(self.agentIndex):
      agent = self.agents[index]
      action = Directions.STOP
      if state.data._eaten[agentIndex] > 0:
        action = agent.getAction(state)
      actions[agentIndex] = action
	
    return actions
