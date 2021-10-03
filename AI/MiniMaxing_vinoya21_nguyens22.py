##
# NotSoRandom Agent for HW 2B
# CS 421
#
# Authors: Geryl Vinoya and Linda Nguyen
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
from math import inf

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
        super(AIPlayer,self).__init__(inputPlayerId, "MiniMaxing")
        
    
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
        # create a node object with a move, current state, eval, parent,
        #   children, minimax value
        #   may need to eventually add in a part for alpha-beta pruning
        root = {
            "move": None,
            "state": currentState,
            "evaluation": self.utility(currentState),
            "parent": None
        }

        return self.getMiniMaxMove(root, 0, True, -inf, inf)

    def getMiniMaxMove (self, currentNode, currentDepth, myTurn, alpha, beta):
        
        maxDepth = 2

        currNodeEval = currentNode.get("evaluation")
        currentState = currentNode.get("state")

        if currentDepth == maxDepth or currNodeEval == -1 or currNodeEval == 1:
            return currNodeEval

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

        children = sorted(children, key=lambda child: child.get("evaluation"), reverse=True)

        #only take the highest 2 nodes
        children = children[:2]

        endNodes = []

        for node in children:
            endNodes.append(self.getEndNode(node))

        #if this is the root node, then it is our turn and we will recursively get the
        #   move with the best eval
        if currentDepth == 0:
            for node in endNodes:
                node["evaluation"] = self.getMiniMaxMove(node, 1, False, -1000, 1000)
        
            best = max(endNodes, key=lambda node: node.get("evaluation"))
            while best.get("parent") is not None:
                best = best.get("parent")
            
            return best.get("move")
        
        else:
            if myTurn:
                maxScore = -inf
                for node in endNodes:
                    miniMaxScore = self.getMiniMaxMove(node, currentDepth + 1, False, alpha, beta)
                    maxScore = max(maxScore, miniMaxScore)

                    alpha = max(alpha, maxScore)

                    if beta <= alpha:
                        break

                return maxScore
            
            else:
                minScore = inf
                for node in endNodes:
                    miniMaxScore = self.getMiniMaxMove(node, currentDepth + 1, True, alpha, beta)
                    minScore = min(minScore, miniMaxScore)

                    beta = min(beta, minScore)

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
        currentMove = currentNode.get("move")
        if currentMove.moveType == END:
            return currentNode

        currentState = currentNode.get("state")

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

        #convert the previous score of [0,1] to [-1, 1]
        toRet = 1 - (1 / (toRet + 1))
        if toRet <= 0:
            toRet = 0.01
        if toRet >= 1:
            toRet = 0.99

        if toRet == 0.5:
            toRet = 0
        elif toRet > 0.5:
            toRet = (2 * toRet) - 1
        elif toRet < 0.5:
            toRet = -(1 - (2 * toRet))

        return toRet

##
############ UNIT TESTS ###########################
##

#test if utility method returns 0.5 at start of a fresh game
test1 = GameState.getBasicState()
testAI = AIPlayer(0)

#set food for both players to 0
test1.inventories[0].foodCount = 0
test1.inventories[1].foodCount = 0

#anthill health are at 3
anthill0 = Construction((0,0), ANTHILL)
anthill0.health = 3
anthill1 = Construction((5,5), ANTHILL)
anthill1.health = 3

#set coords for food
food0 = Construction((6,2), FOOD)
food1 = Construction((6,7), FOOD)
test1.board[3][2].constr = food0
test1.board[6][7].constr = food1
test1.inventories[0].constrs.append(food0)
test1.inventories[1].constrs.append(food1)

#create tunnel for player 0
tunnel0 = Construction((8,6), TUNNEL)

#create tunnel for player 1
tunnel1 = Construction((0,5), TUNNEL)

#create a worker
worker = Ant((7,2), WORKER, 0)
test1.inventories[0].ants.append(worker)
workers = getAntList(test1, 0, (WORKER,))

#create enemy worker
worker = Ant((3,3), WORKER, 1)
test1.inventories[1].ants.append(worker)
enemyWorkers = getAntList(test1, 1, (WORKER,))

#create a drone
drone = Ant((0,3), DRONE, 0)
test1.inventories[0].ants.append(drone)
drones = getAntList(test1, 0, (DRONE,))

#set queen health to 10
queen0 = Ant((0,0), QUEEN, 0)
queen0.health = 10
queen1 = Ant((5,5), QUEEN, 1)
queen1.health = 10

test1.board[0][0].ant = queen0
test1.board[5][5].ant = queen1

#test if utility is 0.5 at the start of a game
if(testAI.utility(test1) != -0.6653322658126501):
    print("Utility is", testAI.utility(test1), "when should be 0.5 at the start of the game")




