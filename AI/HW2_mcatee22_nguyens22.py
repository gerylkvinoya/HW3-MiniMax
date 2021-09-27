#Authors: Samuel Nquyen & Maxwell McAtee
import random
import sys
import unittest
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import *
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Harrison")

    # utility
    # Description: Returns a number from 0 to 1 based on the current state of a game.
    #
    # Parameters:
    #   currentState: the state of the game.
    ##
    def utility(self, currentState):
        moves = 0  # Start with "neutral" value

        # Get inventories.
        myInv = getCurrPlayerInventory(currentState)

        if myInv.player == 0:
            enemyInv = currentState.inventories[1]
        else:
            enemyInv = currentState.inventories[0]

        # Get important pieces.
        myFood = myInv.foodCount
        myFoodPlacement = getCurrPlayerFood(self, currentState)
        enemyFood = enemyInv.foodCount
        myAnts = myInv.ants
        enemyAnts = enemyInv.ants
        myCombatAnts = getAntList(currentState, myInv.player, (DRONE, SOLDIER, R_SOLDIER))
        enemyCombatAnts = getAntList(currentState, enemyInv.player, (DRONE, SOLDIER, R_SOLDIER))
        myWorkerAnts = getAntList(currentState, myInv.player, (WORKER,))
        enemyWorkerAnts = getAntList(currentState, enemyInv.player, (WORKER,))
        myQueen = myInv.getQueen()
        enemyQueen = enemyInv.getQueen()
        myAnthill = myInv.getAnthill()
        myTunnel = myInv.getTunnels()[0]
        enemyAnthill = enemyInv.getAnthill()

        # Adjust weight based on various factors.
        moves += self.getFoodWeightAdjustment(myFood, enemyFood, myAnts, myWorkerAnts, myAnthill, myTunnel, myFoodPlacement)
        moves += self.getAntWeightAdjustment(myAnts, myCombatAnts, enemyAnts, enemyCombatAnts)
        moves += self.getCombatDistanceWeightAdjustment(myCombatAnts, enemyWorkerAnts, enemyQueen)

        # Automatically set good or bad weights depending on certain conditions.
        if len(myWorkerAnts) > 2:
            moves = 100000000000

        if enemyQueen is None:
            moves = 0

        if len(myCombatAnts) > 2:
            moves = 100000000000

        if myQueen.coords == myAnthill.coords or approxDist(myQueen.coords, myAnthill.coords) > 1:
            moves = 100000000000

        for enemyAnt in enemyCombatAnts:
            if approxDist(myQueen.coords, enemyAnt.coords) == 1:
                moves = 1000000000000

        return moves

    # getCombatDistanceWeightAdjustment
    # Adjusts weight for utility() based on distance of combat ants from enemy units.
    #
    # Parameters:
    #   myCombatAnts: the amount of combat ants this player has.
    #   enemyWorkerAnts: the enemy workers.
    #   enemyQueen: the enemy queen.
    #
    # Return: amount to adjust weight by.
    ##
    def getCombatDistanceWeightAdjustment(self, myCombatAnts, enemyWorkerAnts, enemyQueen):
        moves = 0
        enemyWorkerMoves = 0
        enemyQueenMoves = 0

        if len(myCombatAnts) > 0:
            for combatant in myCombatAnts:
                if enemyWorkerAnts is not None:
                    for worker in enemyWorkerAnts:
                        distToWorker = approxDist(combatant.coords, worker.coords)
                        if combatant.type == 2:  # Drone
                            distToWorker /= 3
                        elif combatant.type == 3:  # Soldier
                            distToWorker /= 2
                        moves += distToWorker

                if enemyQueen is not None:
                    distToQueen = approxDist(combatant.coords, enemyQueen.coords)
                    if combatant.type == 2:  # Drone
                        distToQueen /= 3
                    elif combatant.type == 3:  # Soldier
                        distToQueen /= 2
                    moves += distToQueen

            # if enemyWorkerMoves != None:
            #     moves += enemyWorkerMoves
            # else:
            #     moves += enemyQueenMoves
        return moves

    # getFoodWeightAdjustment
    # Adjusts weight for utility() based on food factors.
    #
    # Parameters:
    #   myFood: the amount of food this player has.
    #   enemyFood: the amount of food the opponent has.
    #
    # Return: amount to adjust weight by.
    ##
    def getFoodWeightAdjustment(self, myFood, enemyFood, ants, workers, myAnthill, myTunnel, myFoodPlacement):
        moves = 0
        hillCovered = False

        foodOne = myFoodPlacement[0]
        foodTwo = myFoodPlacement[1]

        tunnelToFOne = approxDist(myTunnel.coords, foodOne.coords)
        tunnelToFTwo = approxDist(myTunnel.coords, foodTwo.coords)
        hillToFOne = approxDist(myAnthill.coords, foodOne.coords)
        hillToFTwo = approxDist(myAnthill.coords, foodTwo.coords)
        maxDist = min([tunnelToFOne, tunnelToFTwo, hillToFOne, hillToFTwo])

        difference = (11 - myFood)
        movesToWin = difference * (maxDist)

        for ant in ants:
            if ant.coords == myAnthill.coords:
                hillCovered = True

        for worker in workers:
            tunnelDist = approxDist(worker.coords, myTunnel.coords)
            anthillDist = approxDist(worker.coords, myAnthill.coords)
            foodOneDist = approxDist(worker.coords, foodOne.coords)
            foodTwoDist = approxDist(worker.coords, foodTwo.coords)

            if worker.carrying:  
                if tunnelDist < anthillDist or hillCovered:
                    if(foodOneDist > foodTwoDist):
                        moves += - tunnelToFTwo/2 - (tunnelToFTwo - tunnelDist)/2
                    else:
                        moves += - tunnelToFOne/2 - (tunnelToFOne - tunnelDist)/2
                else:
                    if(foodOneDist > foodTwoDist):
                        moves += - hillToFTwo/2 - (hillToFTwo - anthillDist)/2
                    else:
                        moves +=  - hillToFTwo/2 - (hillToFTwo - anthillDist)/2

            elif not worker.carrying:
                if foodOneDist < foodTwoDist:
                    if(tunnelDist > anthillDist):
                        moves += - (hillToFOne - foodOneDist)/2
                    else:
                        moves += - (tunnelToFOne - foodOneDist)/2

                else:
                    if(tunnelDist > anthillDist):
                        moves += - (hillToFTwo - foodTwoDist)/2
                    else:
                        moves += - (tunnelToFTwo - foodTwoDist)/2
        if len(workers) != 0:
            moves = (movesToWin + (moves - (myFood * (maxDist)))/len(workers))

        return moves

    # getAntWeightAdjustment
    # Adjusts weight for utility() based on ant factors.
    #
    # Parameters:
    #   myAnts: the amount of ants this player has.
    #   myCombatAnts: the amount of ants this player has for combat.
    #   enemyAnts: the amount of ants the opponent has.
    #   enemyCombatAnts: the amount of ants the opponent has for combat.
    #
    # Return: amount to adjust weight by.
    ##
    def getAntWeightAdjustment(self, myAnts, myCombatAnts, enemyAnts, enemyCombatAnts):
        adjustment = (len(enemyAnts) - len(myCombatAnts))*5

        

        return adjustment

    # bestMove
    # Description: Returns a best node.
    #
    # Parameters:
    #   list: the list of nodes.
    ##
    def bestMove(self, nodeList):
        evalList = []
        nodesWithMinEvals = []

        #print (nodeList[0], "\n\n")
        for node in nodeList:
            nodeEval = node['evaluation']
            evalList.append(nodeEval)

        minValue = min(evalList)

        index = 0

        for i in evalList:
            if i == minValue:
                nodesWithMinEvals.append(nodeList[index])
            index += 1

        return nodesWithMinEvals[random.randint(0, len(nodesWithMinEvals) - 1)]

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        root = {
            "moveToReach": None,
            "state": currentState,
            "depth": 0,  
            "evaluation": self.utility(currentState),
            "parent": None
        }

        depth1Nodes = []
        depth2Nodes = []
        depth3Nodes = []

        # Get all possible first moves.
        firstPossibleMoves = listAllLegalMoves(root["state"])

        # Add all moves to the tree.
        for move in firstPossibleMoves:
            depth1State = getNextStateAdversarial(currentState, move)
            depth1Node = self.createNode(move, depth1State, root)
            depth1Nodes.append(depth1Node)
            depth2Moves = listAllLegalMoves(depth1Node["state"])

            # Add all second moves.
            for move2 in depth2Moves:
                depth2State = getNextStateAdversarial(depth1State, move2)
                depth2Node = self.createNode(move2, depth2State, depth1State)
                depth2Nodes.append(depth2Node)
                depth3Moves = listAllLegalMoves(depth2Node["state"])

                # Add all second moves.
                for move3 in depth3Moves:
                    depth3State = getNextStateAdversarial(depth1State, move3)
                    depth3Node = self.createNode(move3, depth3State, depth1State)
                    depth3Nodes.append(depth3Node)

        return None

    def expandNode(self, node):
        moves = listAllLegalMoves(node["state"])
        states = []
        nodes = []

        for move in moves:
            states.append(getNextState(node['state'], move))

        i = 0  # Keep track of index.
        for move in moves:
            newDepth = 1 + node["depth"]
            newNode = {
                "moveToReach": move,
                "state": states[i],
                "depth": newDepth,
                "evaluation": self.utility(states[i]) + newDepth,
                "parent": node
            }
            nodes.append(newNode)
            i += 1

        maxNode = max()
        return nodes

    ##
    # createNode
    # Description: Creates a node with 5 values.
    #
    # Parameters:
    #   move: the move to get to the state.
    #   gameState: the current state.
    #   parent: the parent of the node.
    #
    # Return: the completed node.
    ##
    def createNode(self, move, gameState, parent):
        # Represents a node.
        node = {
            "moveToReach": move,
            "state": gameState,
            "depth": 1 + parent["depth"],  # Arbitrary value, for part A.
            "evaluation": self.utility(gameState) + 1,
            "parent": parent  # Arbitrary value, not used for now.
        }

        return node
    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass



