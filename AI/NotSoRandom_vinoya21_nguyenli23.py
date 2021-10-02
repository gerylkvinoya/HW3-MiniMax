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
        super(AIPlayer,self).__init__(inputPlayerId, "NotSoRandom")
        
    
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
            "moveToReach": None,
            "state": currentState,
            "evaluation": self.utility(currentState),
            "parent": None
        }

        return self.getMiniMaxMove(root, 0, True, -1000, 1000)

    def getMiniMaxMove (self, currentNode, currentDepth, myTurn, alpha, beta):
        maxDepth = 2

        currNodeEval = currentNode.get("evaluation")
        currentState = currentNode.get("state")

        if currentDepth == maxDepth or currNodeEval == 0 or currNodeEval == 1:
            return currNodeEval

        children = []
        legalMoves = listAllLegalMoves(currentState)
        for move in legalMoves:
            newState = getNextStateAdversarial(currentState, move)

            node = {
                "moveToReach": move,
                "state": newState,
                "evaluation": self.utility(newState),
                "parent": currentNode,
            }
            children.append(node)

        #sort by evaluation descending
        #children = sorted(children, key=lambda node: node.get("evalutation"), reverse=True)

        endNodes = []

        for node in children:
            endNodes.append(self.getEndNode(node))

        #if this is the root node, then it is our turn
        if currentDepth == 0:
            for node in endNodes:
                node["evaluation"] = self.getMiniMaxMove(node, 1, False, -1000, 1000)
        
                best = max(endNodes, key=lambda node: node.get("evaluation"))
            
            while best.get("parent") is not None:
                best = best.get("parent")
            
            return best.get("moveToReach")
        
        else:
            if myTurn:
                maxScore = -1000
                for node in endNodes:
                    miniMaxScore = self.getMiniMaxMove(node, currentDepth + 1, False)
                    maxScore = max(maxScore, miniMaxScore)

                return maxScore
            
            else:
                minScore = 1000
                for node in endNodes:
                    miniMaxScore = self.getMiniMaxMove(node, currentDepth + 1, True)
                    minScore = min(minScore, miniMaxScore)

                return minScore





    def getEndNode(self, currentNode):
        if currentNode.get("moveToReach").moveType == END:
            return currentNode

        currentState = currentNode.get("state")

        children = []
        legalMoves = listAllLegalMoves(currentState)
        for move in legalMoves:
            newState = getNextStateAdversarial(currentState, move)

            node = {
                "moveToReach": move,
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
    def utility(self, currentState) -> float:

        #get my id and enemy id
        myId = currentState.whoseTurn
        enemyId = 1 - myId

        #get the my inventory and the enemy inventory
        myInv = currentState.inventories[myId]
        enemyInv = currentState.inventories[enemyId]

        #get the values of the queen, anthill, and foodcount
        myQueen = myInv.getQueen()
        myAntHill = myInv.getAnthill()
        myTunnel = getConstrList(currentState, myId, (TUNNEL,))[0]
        myFoodCount = myInv.foodCount
        enemyQueen = enemyInv.getQueen()
        enemyAntHill = enemyInv.getAnthill()
        enemyTunnel = getConstrList(currentState, enemyId, (TUNNEL,))[0]
        enemyFoodCount = enemyInv.foodCount

        #get the closest food to my tunnel
        foods = getConstrList(currentState, None, (FOOD,))           
        foods.sort(key=lambda food: stepsToReach(currentState, myTunnel.coords, food.coords))
        closestFood = foods[0] 

        #check for the start of game
        #foodCount should be 0, queen should have full health (10),
        #anthill should have full capture health(3)
        if (myFoodCount == 0 and enemyFoodCount == 0 and
            myAntHill.captureHealth == 3 and enemyAntHill.captureHealth == 3 and
            myQueen.health == 10 and enemyQueen.health == 10):
            return 0.5

        #get the lists of all the different types of ants
        workerList = getAntList(currentState, myId, (WORKER,))
        droneList = getAntList(currentState, myId, (DRONE,))
        soldierList = getAntList(currentState, myId, (SOLDIER,))
        rangedSoldierList = getAntList(currentState, myId, (R_SOLDIER,))
        enemyWorkerList = getAntList(currentState, enemyId, (WORKER,))

        #want to make sure there is only 1 worker and 1 drone
        if len(droneList) != 1 and myFoodCount > 2:
            return 0.0
        if len(droneList) > 1:
            return 0.0
        if len(workerList) != 1:
            return 0.0
        if len(soldierList) != 0:
            return 0.0
        if len(rangedSoldierList) != 0:
            return 0.0


        #will modify this toRet value based off of gamestate
        toRet = 0.5

        #will use this to estimate the number of "moves"
        #the number of moves is connected to approxDist
        #The lower the approxDist, the lower number
        #of "moves" needed to get to an optimal gamestate
        utilityEstimate = {
            0: 1.0,
            1: 0.88,
            2: 0.77,
            3: 0.66,
            4: 0.55,
            5: 0.44,
            6: 0.33,
            7: 0.22,
            8: 0.11,
            9: 0.0
        }


        #get the worker to move between the food and the tunnel
        toRet += utilityEstimate.get(self.workerUtility(workerList, myTunnel, closestFood), 0.0)/9

        #get the drone to sit on the enemy tunnel
        toRet += utilityEstimate.get(self.droneUtility(droneList, enemyWorkerList, enemyTunnel), 0.0)/9

        # modifying the toRet to be within the range [-1, 1]
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

    #bestMove
    #
    #Description: goes through each node in a list and finds the one with the 
    #highest evaluation
    #
    #Parameters: nodeList - the list of nodes you want to find the best eval for
    #
    #return: the node with the best eval
    def bestMove(self, nodeList):
        bestNode = nodeList[0]
        for node in nodeList:
            if (node['eval'] > bestNode['eval']):
                bestNode = node

        return bestNode


    #expandNode
    #
    #Description: generate a list of all valid moves from the gamestate
    #             in the given node
    #
    #             create a list of 
    #
    #Parameters: node - an existing node
    #
    #return: list of nodes
    def expandNode(self, node):

        #list of nodes to return
        nodeList = []
        
        #get current state
        currentState = node.get('state')

        #list all valid moves from the current state of the node
        allMoves = listAllLegalMoves(currentState)

        for move in allMoves:

            
            newState = self.getNextState(currentState, move)
            newDepth = node.get('depth') + 1
            newNode = {
                'move' : move,
                'state' : newState,
                'depth' : newDepth,
                'eval' : self.utility(newState),
                'parent': node
            }

            nodeList.append(newNode)

            
        return nodeList

    #scoreUtility
    #
    #Description: return an evaluation based off of the current score of the game       
    #              for food, queen health, anthill health
    #
    #Parameters: 
    #   myFoodCount
    #   enemyFoodCount
    #   myQueenHealth
    #   enemyQueenHealth
    #   myAntHillHealth
    #   enemyAntHillHealth
    #
    #return: utility number of the evaluation of the game
    def scoreUtility(self, myFoodCount, enemyFoodCount, myQueenHealth, enemyQueenHealth,
                     myAntHillHealth, enemyAntHillHealth) -> float:
        toRet = 0

        #food count
        myFoodCountScale = myFoodCount/11
        enemyFoodCountScale = enemyFoodCount/11
        foodCountDiff = myFoodCountScale - enemyFoodCountScale
        toRet += foodCountDiff/3

        #queen health
        myQueenHealthScale = 1 - (myQueenHealth/10)
        enemyQueenHealthScale = 1 - (enemyQueenHealth/10)
        queenHealthDiff = enemyQueenHealthScale - myQueenHealthScale

        #scaling down the diff because the numbers were unrealistic at first
        toRet += queenHealthDiff/3

        #anthill capture health
        myCapHealthScale = 1 - (myAntHillHealth/3)
        enemyCapHealthScale = 1 - (enemyAntHillHealth/3)
        capHealthDiff = enemyCapHealthScale - myCapHealthScale

        #scaling down the diff because the numbers were unrealistic at first
        toRet += capHealthDiff/3

        return toRet
        
    #workerUtility
    #
    #Description: return an evaluation based off of the move of a worker       
    #
    #Parameters:
    #   workerList - list of workers
    #   myTunnel - to get coords of tunnel
    #   closestFood - to get coords of closest food
    #
    #return: utility number of the evaluation of the game
    def workerUtility(self, workerList, myTunnel, closestFood) -> int:
        if workerList:
            for worker in workerList:
                if worker.carrying:
                    tunnelDist = approxDist(worker.coords, myTunnel.coords)
                    return tunnelDist
                
                else:
                    foodDist = approxDist(worker.coords, closestFood.coords)
                    return foodDist

        return 9

    #droneUtility
    #
    #Description: return an evaluation based off of the move of a drone       
    #
    #Parameters:
    #   droneList - list of my drones
    #   enemyWorkerList - list of enemy workers
    #   enemyTunnel - to get coords of enemy tunnel
    #
    #return: utility number of the evaluation of the game
    def droneUtility(self, droneList, enemyWorkerList, enemyTunnel) -> int:
        
        if len(enemyWorkerList) == 0:
            return 0

        #a little buggy when the drone chases after an enemy worker, but works fine vs the other AI as the drone can just sit on the enemy tunnel
        if droneList:
            for drone in droneList:
                droneDist = approxDist(drone.coords, enemyTunnel.coords)
                #droneAward += 1 - droneDist/9
                #droneAward += utilityEstimate.get(droneDist, 0)\
                return droneDist

        #toRet += droneAward/9 #used to be 9

        return 9

    #I found this online that had a getNextState working better than the one in AIPlayerUtils
    def getNextState(self, currentState, move):
        """
        Revised version of getNextState from AIPlayerUtils.
        Copied from Nux's email to the class.
        :param currentState: The current GameState.
        :param move: The move to be performed.
        :return: The next GameState from the specified move.
        """

        # variables I will need
        myGameState = currentState.fastclone()
        myInv = getCurrPlayerInventory(myGameState)
        me = myGameState.whoseTurn
        myAnts = myInv.ants
        myTunnels = myInv.getTunnels()
        myAntHill = myInv.getAnthill()

        # If enemy ant is on my anthill or tunnel update capture health
        ant = getAntAt(myGameState, myAntHill.coords)
        if ant is not None:
            if ant.player != me:
                myAntHill.captureHealth -= 1

        # If an ant is built update list of ants
        antTypes = [WORKER, DRONE, SOLDIER, R_SOLDIER]
        if move.moveType == BUILD:
            if move.buildType in antTypes:
                ant = Ant(myInv.getAnthill().coords, move.buildType, me)
                myInv.ants.append(ant)
                # Update food count depending on ant built
                if move.buildType == WORKER:
                    myInv.foodCount -= 1
                elif move.buildType == DRONE or move.buildType == R_SOLDIER:
                    myInv.foodCount -= 2
                elif move.buildType == SOLDIER:
                    myInv.foodCount -= 3
            # ants are no longer allowed to build tunnels, so this is an error
            elif move.buildType == TUNNEL:
                print("Attempted tunnel build in getNextState()")
                return currentState

        # If an ant is moved update their coordinates and has moved
        elif move.moveType == MOVE_ANT:
            newCoord = move.coordList[-1]
            startingCoord = move.coordList[0]
            for ant in myAnts:
                if ant.coords == startingCoord:
                    ant.coords = newCoord
                    # TODO: should this be set true? Design decision
                    ant.hasMoved = False
                    attackable = listAttackable(ant.coords, UNIT_STATS[ant.type][RANGE])
                    for coord in attackable:
                        foundAnt = getAntAt(myGameState, coord)
                        if foundAnt is not None:  # If ant is adjacent my ant
                            if foundAnt.player != me:  # if the ant is not me
                                foundAnt.health = foundAnt.health - UNIT_STATS[ant.type][
                                    ATTACK]  # attack
                                # If an enemy is attacked and loses all its health
                                # remove it from the other players
                                # inventory
                                if foundAnt.health <= 0:
                                    myGameState.inventories[1 - me].ants.remove(foundAnt)
                                # If attacked an ant already don't attack any more
                                break
        return myGameState



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
if(testAI.utility(test1) != 0.5):
    print("Utility is", testAI.utility(test1), "when should be 0.5 at the start of the game")
else:
    print("Utility test for game start passed.")

#test if score utility is 0 at the start of a game
if(testAI.scoreUtility(0, 0, 10, 10, 3, 3) != 0):
    print("Score utility is ", testAI.scoreUtility(test1), "when it should be 0")
else:
    print("Utility test for game score passed.")

#distance from worker to food is 1 so it should return 1
if(testAI.workerUtility(workers, tunnel0, food0) != 1):
    print("Worker utility is", testAI.workerUtility(workers, tunnel0, food0), 
        "when it should be 1")
else:
    print("Utility test for workerUtility passed.")

#distance from drone to enemy tunnel is 2 so should return 2
if(testAI.droneUtility(drones, enemyWorkers, tunnel1) != 2):
    print("Drone utility is", testAI.droneUtility(drones, enemyWorkers, tunnel1), 
        "when it should be 2")
else:
    print("Utility test for droneUtility passed")





