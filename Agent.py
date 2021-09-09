# Agent.py

from mmap import ACCESS_COPY
from Percept import Percept
import Action, random

class Agent:
    def __init__(self):

        # Create a dictionary to map cardinal directions to their effect on position.
        self.orientationMovementTransform = {'N':[0,1], 'E':[1,0], 'S':[0,-1], 'W':[-1,0]}

        # Create dictionaries to determine the new orientation after turning.
        self.turnRightTransform = {'N':'E', 'E':'S', 'S':'W', 'W':'N'}
        self.turnLeftTransform = {'N':'W', 'W':'S', 'S':'E', 'E':'N'}

        # The size of the grid (known for now).
        self.gridSize = 4


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
        If a forward movement extends into an invalid position, reset the position.
        Returns the GOFORWARD action as well.
        """

        # Perform the forward movement based on current orientation.
        positionTransform = self.orientationMovementTransform[self.orientation]
        self.position = [self.position[0] + positionTransform[0], self.position[1] + positionTransform[1]]

        # Check for invalid position, resetting if necessary.
        for i in range(len(self.position)):
            if self.position[i] < 1: self.position[i] = 1
            elif self.position[i] > self.gridSize: self.position[i] = self.gridSize

        return Action.GOFORWARD


    def __del__(self):
        pass
    
    def Initialize(self):
        self.hasGold = False # Whether or not the agent has picked up the gold
        self.hasArrow = True # Whether or not the agent still has an arrow that can be shot.
        self.position = [1,1] # A two-item list representing the x and y coordinates of the agent's position.
        self.orientation = 'E' # The cardinal direction that the agent is facing.
    
    def Process(self, percept: Percept):
        """
        Given a Percept option, determine what action to take, and return it.
        """

        print("Perceived position:",self.position)

        # Grab the gold if a glitter is perceived.
        if percept.glitter: self.hasGold = True; return Action.GRAB

        # Climb out if the gold is in hand and the agent is at the exit.
        if self.hasGold and self.position == [1,1]: return Action.CLIMB

        # Shoot the arrow if a stench is perceived and there is still an arrow to shoot.
        if self.hasArrow and percept.stench: self.hasArrow = False; return Action.SHOOT

        # Otherwise, choose a random movement/rotation action.
        return random.choice([self.turnLeft, self.turnRight, self.moveForward])()


    def GameOver(self, score):
        pass
