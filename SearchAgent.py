# Agent.py
#
# This code works only for the testworld that comes with the simulator.

import Action
import Orientation
import Search

class MySearchEngine(Search.SearchEngine):
    def HeuristicFunction(self, state, goalState):
        return 0 # not a good heuristic
    
class Agent:
    def __init__(self):
        self.agentHasGold = False
        self.actionList = []
        self.searchEngine = MySearchEngine()
    
    def __del__(self):
        pass
    
    def Initialize(self):
        # Works only for test world.
        # You won't initially know safe locations or world size.
        for x in range(1,5):
            for y in range(1,5):
                self.searchEngine.AddSafeLocation(x,y)
        self.searchEngine.RemoveSafeLocation(1,3) # wumpus
        self.searchEngine.RemoveSafeLocation(3,1) # pit
        self.searchEngine.RemoveSafeLocation(3,3) # pit
        self.searchEngine.RemoveSafeLocation(4,4) # pit
        self.agentHasGold = False
        self.actionList = []
    
    # Input percept is a dictionary [perceptName: boolean]
    def Process (self, percept):
        if (not self.actionList):
            if (not self.agentHasGold):
                self.actionList += self.searchEngine.FindPath([1,1], Orientation.RIGHT, [2,3], Orientation.RIGHT)
                self.actionList.append(Action.GRAB)
                self.agentHasGold = True
            else:
                self.actionList += self.searchEngine.FindPath([2,3], Orientation.RIGHT, [1,1], Orientation.RIGHT)
                self.actionList.append(Action.CLIMB)
        action = self.actionList.pop(0)
        return action
    
    def GameOver(self, score):
        pass
