##
# MiniMaxing Agent for HW 3
# CS 421
#
# Authors: Geryl Vinoya and Samuel Nguyen
##
import random
import sys
import time
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
from typing import Dict, List
import unittest

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
        super(AIPlayer,self).__init__(inputPlayerId, "MiniMaxing_vinoya21_nguyens22")
        
    
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

        # create a root node object with a move, current state, eval, parent
        root = {
            "move": None,
            "state": currentState,
            "evaluation": self.utility(currentState),
            "parent": None
        }

        return self.getMiniMaxMove(root, 0, True, -100, 100)

    ##
    #getMiniMaxMove
    #Description: Recursively gets the best minimax move at depth 2
    #
    #Parameters:
    #   currentNode - the current node being worked on
    #   currentDepth - the current depth 
    #   myTurn - boolean if it is the AIPlayer's turn or not
    #   alpha - alpha value for pruning
    #   beta - beta value for pruning
    #
    #Return: The Move to be made
    ##
    def getMiniMaxMove (self, currentNode, currentDepth, myTurn, alpha, beta):
        maxDepth = 2 #the max depth for the minimax tree

        #get the current node's eval and state to be used later
        currNodeEval = currentNode.get("evaluation")
        currentState = currentNode.get("state")

        #if we are at max depth or at a win/loss, return the eval number
        if currentDepth == maxDepth or currNodeEval == -1 or currNodeEval == 1:
            return currNodeEval

        #create a list of children nodes for the current node
        children = []
        legalMoves = listAllLegalMoves(currentState)
        for move in legalMoves:
            newState = getNextStateAdversarial(currentState, move)
            node = {
                "move": move,
                "state": newState,
                "evaluation": self.utility(newState),
                "parent": None,
            }
            children.append(node)

        #sort the children in descending order and only pick the highest 2
        children = sorted(children, key=lambda child: child.get("evaluation"), reverse=True)
        children = children[:2]

        #create a list of nodes that have an end move type
        endNodes = []
        for node in children:
            endNodes.append(self.getEndNode(node))

        #now we have all the information we need, recursion will start below    
        #   if this is the root node, then it is our turn and we will recursively get the
        #   move with the best eval
        if currentDepth == 0:
            for node in endNodes:
                node["evaluation"] = self.getMiniMaxMove(node, 1, False, -10, 10)
        
            best = max(endNodes, key=lambda node: node.get("evaluation"))
            while best.get("parent"):
                best = best.get("parent")
            
            return best.get("move")
        
        #if this is not the root node, then we travel through the tree
        #   and evaluate the values while performing alpha-beta pruning
        else:
            if myTurn:
                #set to an arbitrary "low" number to compare the high score to get the highest score
                maxScore = -10

                #continue to recurse through the endNodes to find the best move and change playerturn
                for node in endNodes:
                    miniMaxScore = self.getMiniMaxMove(node, currentDepth + 1, False, alpha, beta)
                    if miniMaxScore > maxScore: 
                        maxScore = miniMaxScore
                    if maxScore > alpha:
                        alpha = maxScore

                    #check if we can prune
                    if beta <= alpha:
                        break
                return maxScore
            
            else:
                #set to an arbitrary "high" number to compare the high score to get the lowest score
                minScore = 10

                #continue to recurse through the endNodes to find the best move and change playerturn
                for node in endNodes:
                    miniMaxScore = self.getMiniMaxMove(node, currentDepth + 1, True, alpha, beta)
                    if miniMaxScore < minScore:
                        minScore = miniMaxScore
                    if minScore < beta:
                        beta = minScore
                
                    #check if we can prune
                    if beta <= alpha:
                        break

                return minScore

    ##
    #getEndNode
    #Description: Recursively finds the highest scoring end node
    #
    #Parameters:
    #   currentNode - node to find
    #
    #Return: The Move to be made
    ##
    def getEndNode(self, currentNode):

        #base case
        #   if we find a node that is an end type return that node
        currentMove = currentNode.get("move")
        if currentMove.moveType == END:
            return currentNode

        currentState = currentNode.get("state")

        #create list of children of the current node
        children = []
        legalMoves = listAllLegalMoves(currentState)
        for move in legalMoves:
            newState = getNextStateAdversarial(currentState, move)
            node = {
                "move": move,
                "state": newState,
                "evaluation": self.utility(newState),
                "parent": currentNode,
            }
            children.append(node)
        #find the best child and return it
        bestChild = max(children, key=lambda node: node.get("evaluation"))
        return self.getEndNode(bestChild)

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
        #method template, not implemented
        pass

    ##
    #utility
    #Description: examines GameState object and returns a heuristic guess of how
    #               "good" that game state is on a scale of 0 to 1
    #
    #               a player will win if his opponent’s queen is killed, his opponent's
    #               anthill is captured, or if the player collects 11 units of food
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: the "guess" of how good the game state is
    ##
    def utility(self, currentState):
        WEIGHT = 10 #weight value for moves

        #will modify this toRet value based off of gamestate
        toRet = 0

        #get my id and enemy id
        me = currentState.whoseTurn
        enemy = 1 - me

        #get the values of the anthill, tunnel, and foodcount
        myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        myAnthill = getConstrList(currentState, me, (ANTHILL,))[0]
        myFoodList = getConstrList(currentState, 2, (FOOD,))
        enemyTunnel = getConstrList(currentState, enemy, (TUNNEL,))[0]

        #get my soldiers and workers
        mySoldiers = getAntList(currentState, me, (SOLDIER,))
        myWorkerList = getAntList(currentState, me, (WORKER,))

        #get enemy worker and queen
        enemyWorkerList = getAntList(currentState, enemy, (WORKER,))
        enemyQueenList = getAntList(currentState, enemy, (QUEEN,))

        for worker in myWorkerList:

            #if a worker is carrying food, go to tunnel
            if worker.carrying:
                tunnelDist = stepsToReach(currentState, worker.coords, myTunnel.coords)
                #anthillDist = stepsToReach(currentState, worker.coords, myAnthill.coords)

                #if tunnelDist <= anthillDist:
                toRet = toRet + (1 / (tunnelDist + (4 * WEIGHT)))
                #else:
                    #toRet = toRet + (1 / (anthillDist + (4 * WEIGHT)))

                #add to the eval if a worker is carrying food
                toRet = toRet + (1 / WEIGHT)

            #if a worker isn't carrying food, get to the food
            else:
                foodDist = 1000
                for food in myFoodList:
                    # Updates the distance if its less than the current distance
                    dist = stepsToReach(currentState, worker.coords, food.coords)
                    if (dist < foodDist):
                        foodDist = dist
                toRet = toRet + (1 / (foodDist + (4 * WEIGHT)))
        
        #try to get only 1 worker
        if len(myWorkerList) == 1:
            toRet = toRet + (2 / WEIGHT)
        

        #try to get only one soldier
        if len(mySoldiers) == 1:
            toRet = toRet + (WEIGHT * 0.2)
            enemyWorkerLength = len(enemyWorkerList)
            enemyQueenLength = len(enemyQueenList)
            
            #we want the soldier to go twoards the enemy tunnel/workers
            if enemyWorkerList:
                distToEnemyWorker = stepsToReach(currentState, mySoldiers[0].coords, enemyWorkerList[0].coords)
                distToEnemyTunnel = stepsToReach(currentState, mySoldiers[0].coords, enemyTunnel.coords)
                toRet = toRet + (1 / (distToEnemyWorker + (WEIGHT * 0.2))) + (1 / (distToEnemyTunnel + (WEIGHT * 0.5)))
            
            #reward the agent for killing enemy workers
            #try to kill the queen if enemy workers dead
            else:
                toRet = toRet + (2 * WEIGHT)
                if enemyQueenLength > 0:
                    enemyQueenDist = stepsToReach(currentState, mySoldiers[0].coords, enemyQueenList[0].coords)
                    toRet = toRet + (1 / (1 + enemyQueenDist))
            

            toRet = toRet + (1 / (enemyWorkerLength + 1)) + (1 / (enemyQueenLength + 1))

        #try to get higher food score
        foodCount = currentState.inventories[me].foodCount
        toRet = toRet + foodCount

        #set the correct bounds for the toRet
        toRet = 1 - (1 / (toRet + 1))
        if toRet <= 0:
            toRet = 0.01
        if toRet >= 1:
            toRet = 0.99

        #convert the previous score of [0,1] to [-1, 1]
        if toRet == 0.5:
            toRet = 0
        elif toRet > 0.5:
            toRet = (2 * toRet) - 1
        elif toRet < 0.5:
            toRet = -(1 - (2 * toRet))

        return toRet

class TestCreateNode(unittest.TestCase):
    # Queens, anthills, and tunnels only.
    def test_utility(self):
        player = AIPlayer(0)

        # Create game state with food.
        gameState = GameState.getBasicState()
        p1Food1 = Building((1, 1), FOOD, 0)
        p1Food2 = Building((2, 2), FOOD, 0)
        gameState.board[1][1] = p1Food1
        gameState.board[2][2] = p1Food2
        gameState.inventories[2].constrs += [p1Food1, p1Food2]
        p1Food1 = Building((7, 7), FOOD, 1)
        p1Food2 = Building((8, 8), FOOD, 1)
        gameState.board[7][7] = p1Food1
        gameState.board[8][8] = p1Food2
        gameState.inventories[2].constrs += [p1Food1, p1Food2]

        # Calculations below.

        # toRet = 0
        # toRet = 1 - (1 / (toRet + 1)) = 1
        # if toRet <= 0:
        #     toRet = 0.01 = 0.01
        # if toRet >= 1:
        #     toRet = 0.99
        #
        # if toRet == 0.5:
        #     toRet = 0
        # elif toRet > 0.5:
        #     toRet = (2 * toRet) - 1
        # elif toRet < 0.5:
        #     toRet = -(1 - (2 * toRet)) = -0.98
        self.assertEqual(player.utility(gameState), -0.98)

    # Same as above, but with workers.
    def test_utility2(self):
        player = AIPlayer(0)

        # Create game state with food.
        gameState = GameState.getBasicState()
        p1Food1 = Building((1, 1), FOOD, 0)
        p1Food2 = Building((2, 2), FOOD, 0)
        gameState.board[1][1] = p1Food1
        gameState.board[2][2] = p1Food2
        gameState.inventories[2].constrs += [p1Food1, p1Food2]
        p1Food1 = Building((7, 7), FOOD, 1)
        p1Food2 = Building((8, 8), FOOD, 1)
        gameState.board[7][7] = p1Food1
        gameState.board[8][8] = p1Food2
        gameState.inventories[2].constrs += [p1Food1, p1Food2]

        # Add worker.
        worker = Ant((1, 0), WORKER, 0)
        gameState.board[1][0] = worker
        gameState.inventories[0].ants.append(worker)

        # Calculations below.

        # toRet = 0
        # Dist from closer food is 1, toRet = toRet + (1 / (foodDist + (4 * WEIGHT))) = 1/41.
        # toRet = toRet + (2 / WEIGHT) = 46/205

        # toRet = 1 - (1 / (toRet + 1)) = 46/251
        # if toRet <= 0:
        #     toRet = 0.01
        # if toRet >= 1:
        #     toRet = 0.99
        #
        # if toRet == 0.5:
        #     toRet = 0
        # elif toRet > 0.5:
        #     toRet = (2 * toRet) - 1
        # elif toRet < 0.5:
        #     toRet = -(1 - (2 * toRet)) = -159/251

        # Help from https://stackoverflow.com/questions/33199548/how-to-perform-unittest-for-floating-point-outputs-python
        # assertAlmostEqual exists.
        self.assertAlmostEqual(player.utility(gameState), -159/251)

    # Testing soldier parts.
    def test_utility3(self):
        player = AIPlayer(0)

        # Create game state with food.
        gameState = GameState.getBasicState()
        p1Food1 = Building((1, 1), FOOD, 0)
        p1Food2 = Building((2, 2), FOOD, 0)
        gameState.board[1][1] = p1Food1
        gameState.board[2][2] = p1Food2
        gameState.inventories[2].constrs += [p1Food1, p1Food2]
        p1Food1 = Building((7, 7), FOOD, 1)
        p1Food2 = Building((8, 8), FOOD, 1)
        gameState.board[7][7] = p1Food1
        gameState.board[8][8] = p1Food2
        gameState.inventories[2].constrs += [p1Food1, p1Food2]

        # Add soldier.
        soldier = Ant((1, 0), SOLDIER, 0)
        gameState.board[1][0] = soldier
        gameState.inventories[0].ants.append(soldier)

        # Calculations below.

        # toRet = 0
        # toRet = toRet + (WEIGHT * 0.2) = .2
        # No workers, toRet = toRet + (2 * WEIGHT) = 22.
        # Dist to enemy queen is 17, toRet = toRet + (1 / (1 + 17)) = 397/18.
        # No enemy workers, toRet = toRet + (1 / (0 + 1)) + (1 / (1 + 1)) = 212/9.

        # toRet = 1 - (1 / (toRet + 1)) = 212/221
        # if toRet <= 0:
        #     toRet = 0.01
        # if toRet >= 1:
        #     toRet = 0.99
        #
        # if toRet == 0.5:
        #     toRet = 0
        # elif toRet > 0.5:
        #     toRet = (2 * toRet) - 1 = 203/221
        # elif toRet < 0.5:
        #     toRet = -(1 - (2 * toRet))
        self.assertAlmostEqual(player.utility(gameState), 203/221)


if __name__ == '__main__':
    unittest.main()