# Agent.py
#
# This code works only for the testworld that comes with the simulator.

from Percept import Percept
import Action
import Orientation
import Search

class MySearchEngine(Search.SearchEngine):
    def HeuristicFunction(self, state: Search.SearchState, goalState: Search.SearchState):
        # Compute and return city block distance.
        return(abs(state.location[0]-goalState.location[0]) + abs(state.location[1]-goalState.location[1]))
    
class Agent:
    def __init__(self):
        # These two lines are already in Initialize(), so are they unnecessary?
        #self.agentHasGold = False
        #self.actionList = []
        self.location = [1,1] # A two-item list representing the x and y coordinates of the agent's position.
        self.searchEngine = MySearchEngine()
        self.goldLocation = None # The location of the gold.  NoneType if unknown.
    
        # Create a dictionary to map orientations to their effect on position.
        self.orientationMovementTransform = {Orientation.UP:[0,1], Orientation.RIGHT:[1,0],
                                             Orientation.DOWN:[0,-1], Orientation.LEFT:[-1,0]}

        # Create dictionaries to determine the new orientation after turning.
        self.turnRightTransform = {Orientation.UP:Orientation.RIGHT, Orientation.RIGHT:Orientation.DOWN,
                                   Orientation.DOWN:Orientation.LEFT, Orientation.LEFT:Orientation.UP}
        self.turnLeftTransform = {Orientation.UP:Orientation.LEFT, Orientation.LEFT:Orientation.DOWN,
                                  Orientation.DOWN:Orientation.RIGHT, Orientation.RIGHT:Orientation.UP}

        # Assume that the world is the max size to begin.
        self.worldSize = 9

        # Create a set of locations which have already been visited.
        # Add the starting location to this dictionary
        self.visitedLocations = set()
        self.visitedLocations.add((1,1))

        # Create a set of locations that are known to be safe
        # Add the starting location as a safe location.
        self.knownSafeLocations = set()
        self.knownSafeLocations.add((1,1))

        # Also let the search engine know that the starting point is safe.
        self.searchEngine.AddSafeLocation(1,1)

        # Create a set of locations that are known to be unsafe
        self.knownUnsafeLocations = set()

        # Create a set of locations that are adjacent to visited locations but have yet to be visited.
        # Add the 2 spaces adjacent to the starting location as spaces to visit.
        self.locationsToVisit = set()
        self.locationsToVisit.add((1,2))
        self.locationsToVisit.add((2,1))


    def __del__(self):
        pass
    
    def Initialize(self):

        # Check the agent's location.  If it is not [1,1], then the agent encountered an unsafe spot at the end of the
        # last try.  Update the agent's knowledge accordingly.  Then, reset the location to [1,1]
        if self.location != [1,1]:
            self.locationsToVisit.remove(tuple(self.location))
            self.knownUnsafeLocations.add(tuple(self.location))
            self.searchEngine.RemoveSafeLocation(self.location[0],self.location[1])
            self.location = [1,1]

        self.orientation = Orientation.RIGHT # The agent's current orientation.
        self.agentHasGold = False # Whether or not the agent has the gold
        self.actionList = [] # The list of actions (Movement or turning ONLY) the agent is planning on making.
    

    def turnRight(self):
        """
        Turns the agent to the right, altering its orientation.
        Returns the TURNRIGHT action as well.
        """

        self.orientation = self.turnRightTransform[self.orientation]
        return Action.TURNRIGHT


    def turnLeft(self):
        """
        Turns the agent to the left, altering its orientation.
        Returns the TURNLEFT action as well.
        """

        self.orientation = self.turnLeftTransform[self.orientation]
        return Action.TURNLEFT


    def moveForward(self):
        """
        Moves the agent forward relative to its current orientation, altering its position.
        Returns the GOFORWARD action as well.
        """

        # Perform the forward movement based on current orientation.
        positionTransform = self.orientationMovementTransform[self.orientation]
        self.location = [self.location[0] + positionTransform[0], self.location[1] + positionTransform[1]]

        # Agent should never try to move into an x or y position of 0
        assert self.location[0] > 0 and self.location[1] > 0, "Attempted to move out of bounds at bottom or left border."

        return Action.GOFORWARD


    # Input percept is a dictionary [perceptName: boolean]
    def Process (self, percept: Percept):

        # Did the agent bump?  If so, we now know the world size and should reset our position
        # and update our unvisited locations and actionList to make sure we don't try to go out of bounds again.
        if percept.bump:
            self.worldSize = max(self.location)-1
            self.location[self.location.index(self.worldSize+1)] = self.worldSize
            self.locationsToVisit = {location for location in self.locationsToVisit if max(location) <= self.worldSize}
            self.actionList.clear()

        # Check to see if this is a new location.  If it is, we have some new knowledge about the world!
        if not tuple(self.location) in self.visitedLocations:
            
            # This space has now been visited and is known to be safe.
            self.visitedLocations.add(tuple(self.location))
            self.locationsToVisit.remove(tuple(self.location))
            self.knownSafeLocations.add(tuple(self.location))

            # If there is no breeze or stench, all adjacent spaces are safe too!
            if not percept.stench and not percept.breeze:
                for x in (-1,1):
                    for y in (-1,1):
                        self.knownSafeLocations.add((self.location[0]+x,self.location+y))

            # Check for any unvisited adjacent locations and mark them to be visited.
            for x in (-1,1):
                for y in (-1,1):
                    location = (self.location[0]+x,self.location+y)
                    if not location in self.visitedLocations: self.locationsToVisit.add(location)

        # Did the agent perceive a glitter?  If so, grab it!.
        # Also, update the known gold position.
        if percept.glitter:
            self.actionList.clear()
            self.agentHasGold = True
            self.goldLocation = self.location
            return Action.GRAB

        # Do we have the gold and 

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
