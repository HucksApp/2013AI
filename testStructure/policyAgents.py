from util import *
from game import Agent

class PolicyAgent(Agent):
  def getAction(self, state): raiseNotDefined()
  def getActionByDecisionTree(self, state): raiseNotDefined()

class Policy():
  def isPolicyHolds(self, state): raiseNotDefined()
  def generatePolicy(self, state): raiseNotDefined()
  def getActionForPolicy(self, state): raiseNotDefined()

