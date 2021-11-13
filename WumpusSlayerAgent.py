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

        self.location = [1,1] # A two-item list representing the x and y coordinates of the agent's position.
        self.searchEngine = MySearchEngine() # Initialize the search engine.
        self.goldLocation = None # The location of the gold.  NoneType if unknown.

        # Dictionary to convert action objects to the related function.
        self.actionToFunction = {Action.TURNRIGHT:self.turnRight, Action.TURNLEFT:self.turnLeft, 
                                 Action.GOFORWARD:self.moveForward}
    
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
        self.visitedLocations = set()

        # Create a set of locations that are known to be safe
        self.knownSafeLocations = set()

        # Create a set of locations which have stenches
        self.stenchLocations = set()

        # Create a variable to keep track of the wumpus location.
        # An unknown wumpus location is represented by "None"
        self.wumpusLocation = None

        # Create a set of locations that are adjacent to visited locations but have yet to be visited.
        # Also, add the starting location here as, well, a starting point!
        self.locationsToVisit = set()
        self.locationsToVisit.add((1,1))

        for x in range(1,10):
            for y in range(1,10):
                pass
                #self.searchEngine.AddSafeLocation(x,y)


    def __del__(self):
        pass
    
    def Initialize(self):

        # Check the agent's location.  If it is not [1,1], then the agent encountered an unsafe spot at the end of the
        # last try.  Update the agent's knowledge accordingly.  Then, reset the location to [1,1]
        if self.location != [1,1]:
            print("Agent met its demise at:",self.location,'\n')
            self.locationsToVisit.remove(tuple(self.location))
            self.visitedLocations.add(tuple(self.location))
            self.searchEngine.RemoveSafeLocation(self.location[0],self.location[1])
            self.location = [1,1]

        self.orientation = Orientation.RIGHT # The agent's current orientation.
        self.hasGold = False # Whether or not the agent has the gold
        self.actionList = list() # The list of actions (Movement or turning ONLY) the agent is planning on making.
        self.isWumpusAlive = True # Whether or not the wumpus is still alive.
    

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
        self.location = self.getMovementResult()

        # Agent should never try to move into an x or y position of 0
        assert self.location[0] > 0 and self.location[1] > 0, "Attempted to move out of bounds at bottom or left border."

        return Action.GOFORWARD


    def getMovementResult(self):
        """
        Returns the location of the agent if they were to move forward.
        """
        positionTransform = self.orientationMovementTransform[self.orientation]
        return [self.location[0] + positionTransform[0], self.location[1] + positionTransform[1]]


    def getValidAdjacentLocations(self, location):
        """
        Returns a list of all locations adjacent to the given location that aren't out of bounds.
        """
        adjacentLocations = list()
        for x,y in ((-1,0),(1,0),(0,-1),(0,1)):
            adjacentLocation = (location[0]+x,location[1]+y)
            if min(adjacentLocation) > 0 and max(adjacentLocation) <= self.worldSize:
                adjacentLocations.append(adjacentLocation)

        return adjacentLocations



    # Input percept is a dictionary [perceptName: boolean]
    def Process (self, percept: Percept):

        print("Agent is at:",self.location)

        # First thing's first: If we have gold and are at the exit, get out of there!
        if self.hasGold and self.location == [1,1]: return Action.CLIMB

        # Did the agent bump?  If so, we now know the world size and should reset our position
        # and update our unvisited locations and actionList to make sure we don't try to go out of bounds again.
        if percept.bump:
            self.worldSize = max(self.location)-1
            self.location[self.location.index(self.worldSize+1)] = self.worldSize
            self.locationsToVisit = {location for location in self.locationsToVisit if max(location) <= self.worldSize}
            self.actionList.clear()

        # Did we hear a scream?  If so, the wumpus is dead!
        if percept.scream: self.isWumpusAlive = False

        # Check to see if this is a new location.  If it is, we have some new knowledge about the world!
        if not tuple(self.location) in self.visitedLocations:
            
            # Clear out the current action, as it should only contain rotation actions now anyway.
            self.actionList.clear()

            # This space has now been visited and is known to be safe.
            self.visitedLocations.add(tuple(self.location))
            self.searchEngine.AddSafeLocation(self.location[0],self.location[1])
            self.locationsToVisit.remove(tuple(self.location))
            self.knownSafeLocations.add(tuple(self.location))

            # Determine which adjacent spaces are actually valid.
            adjacentLocations = self.getValidAdjacentLocations(self.location)

            # If there is no breeze or stench, all adjacent spaces are safe too!
            # Don't forget about the edge case where perceiving a stench while on top of the wumpus's corpse doesn't indicate adjacent danger.
            if not percept.breeze and (not percept.stench or tuple(self.location) == self.wumpusLocation):
                for location in adjacentLocations: self.knownSafeLocations.add(location)

            # Otherwise, if there is a stench, add it to the set of known stench locations.
            elif percept.stench: self.stenchLocations.add(tuple(self.location))

            # Check for any unvisited adjacent locations and mark them to be visited.
            for location in adjacentLocations:
                if not location in self.visitedLocations: self.locationsToVisit.add(location)

        # Did the agent perceive a glitter?  If so, grab it, and plan to go back to [1,1]
        # Also, update the known gold position.
        if percept.glitter:
            print("Found gold! Routing back to [1,1]")
            self.actionList = self.searchEngine.FindPath(self.location, self.orientation, [1,1], Orientation.LEFT)
            self.actionList.reverse()
            self.hasGold = True
            self.goldLocation = self.location
            return Action.GRAB

        # If there are not actions planned at the moment, we need to choose a location to travel to.
        if not self.actionList:

            # If we know the location of the gold, go there!
            if self.goldLocation is not None:
                print("Routing to gold at",self.goldLocation)
                self.actionList = self.searchEngine.FindPath(self.location, self.orientation, 
                                                             self.goldLocation, Orientation.RIGHT)

            # Otherwise, check for areas marked for exploration that are guaranteed to be safe.
            else:
                for location in self.locationsToVisit:
                    if location in self.knownSafeLocations:
                        print("Routing to known safe location at",location)
                        self.searchEngine.AddSafeLocation(location[0],location[1])
                        self.actionList = self.searchEngine.FindPath(self.location, self.orientation, 
                                                                     list(location), Orientation.RIGHT)
                        break
            
                # If there aren't any known safe locations, can we kill the wumpus to establish a new safe location?
                if not self.actionList:

                    # (First, check to see if we actually know the wumpus's location or can determine it.)
                    if self.wumpusLocation is None:
                        for stenchLocation1 in self.stenchLocations:
                            for stenchLocation2 in self.stenchLocations:

                                # Can we find a pair of diagonal stenches?
                                if abs(stenchLocation1[0]-stenchLocation2[0]) == 1 and abs(stenchLocation1[1]-stenchLocation2[1]) == 1:
                                    # Is one of the spaces between the diagonals known to be safe?  If so, the wumpus must be in the other space!
                                    if (stenchLocation1[0],stenchLocation2[1]) in self.knownSafeLocations:
                                        self.wumpusLocation = (stenchLocation2[0],stenchLocation1[1])
                                    elif (stenchLocation2[0],stenchLocation1[1]) in self.knownSafeLocations:
                                        self.wumpusLocation  = (stenchLocation1[0],stenchLocation2[1])

                    # If we know the wumpus location now and haven't been there before, route to it!
                    if self.wumpusLocation is not None and not self.wumpusLocation in self.visitedLocations:
                        print("Routing to wumpus at",self.wumpusLocation)
                        self.searchEngine.AddSafeLocation(self.wumpusLocation[0],self.wumpusLocation[1])
                        self.actionList = self.searchEngine.FindPath(self.location, self.orientation, 
                                                                    list(self.wumpusLocation), Orientation.RIGHT)

                    # If we still haven't decided on a location, just pick one that needs to be visited!
                    else: 
                        location = tuple(self.locationsToVisit)[0]
                        print("Routing to possibly safe location at",location)
                        self.searchEngine.AddSafeLocation(location[0],location[1])
                        self.actionList = self.searchEngine.FindPath(self.location, self.orientation, 
                                                                    list(location), Orientation.RIGHT)

            # Reverse the action list so we can pop items off the end, which is more efficient.
            self.actionList.reverse()

        # If we have information about the wumpus, make sure we aren't about to run into him!
        # If we are, it means we plotted a path to or through him and we need to shoot him first.
        if (self.wumpusLocation is not None and self.isWumpusAlive and 
            self.actionList[-1] == Action.GOFORWARD and tuple(self.getMovementResult()) == self.wumpusLocation):
            return Action.SHOOT

        # If we've reached this point, we should have a list of movement actions to work with.  Pop one off and handle it!
        action = self.actionList.pop()
        return self.actionToFunction[action]()
    
    def GameOver(self, score):
        pass
