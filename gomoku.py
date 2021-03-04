#######################################################
# Gomoku Platform (single game)
# Version 0.5
# 
# Xiuyi Fan, Matt Bastiman, Edward Wall, Joe Panes
# Swansea University
# Feb 2020
#

import sys, time, signal
import numpy as np
import os

import concurrent.futures

from time import time
from random import randint

from misc import winningTest, legalMove

BOARD_SIZE = 11  # size of the board is 11-by-11
X_IN_A_LINE = 5   # play the standard game with 5 stones in a line
TIME_OUT = 500    # player must return a move within 5 seconds

# an empty class to host the time-out exception
class TimeOutException(Exception):
    pass

# handler for time out
def handler(signum, frame):
    print("Player timeout - signal -")
    raise TimeOutException()

"""
CHANGE:
Added turn_id to the turn function to replace the player.ID calls
This protects against ID spoofing
"""
# turn taking function
def turn(board, player, turn_id):

    # make a copy of the board, which is passed to the agent
    tempBoard = np.array(board)

    # TIME_OUT seconds Timer
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            playerThread = executor.submit(player.move, tempBoard)
            moveLoc = playerThread.result(TIME_OUT+1)
    except TimeOutException:        
        # Caught the signal timeout exception
        print("before pass")
        pass
    except concurrent.futures.TimeoutError:
        print("Player" + str(turn_id) + " time out.")
        return turn_id*1, board        

    # test if the move is legal - on the original board
    if legalMove(board, moveLoc):
        board[moveLoc] = player.ID
    else:
        print("Player " + str(player.ID) + " illegal move at " + str(moveLoc))
        return turn_id*-1, board

    # test if any player wins the game
    if winningTest(player.ID, board, X_IN_A_LINE):
        return turn_id, board

    # move to the next turn
    return 0, board

def main():
    if len(sys.argv) < 3:
        print("Error. To use: python gomoku.py PLAYER1 PLAYER2");
        print("Example: python gomoku.py GomokuAgentRand GomokuAgentRand");
        return -1;

    rounds = 5

    player1wins_f = 0
    player2wins_f = 0
    player1wins_s = 0
    player2wins_s = 0
    player1draw_s = 0
    player1draw_f = 0

    # two directory names
    p1Dir, p2Dir = sys.argv[1], sys.argv[2]

    for swap in range(2):

        if swap == 0:
            # creating the two players
            P1 = getattr(__import__(p1Dir, fromlist=["player"]), "player")
            P2 = getattr(__import__(p2Dir, fromlist=["player"]), "player")
        else:
            P1 = getattr(__import__(p2Dir, fromlist=["player"]), "player")
            P2 = getattr(__import__(p1Dir, fromlist=["player"]), "player")

        player1 = P1.Player(1, BOARD_SIZE, X_IN_A_LINE)
        player2 = P2.Player(-1, BOARD_SIZE, X_IN_A_LINE)

        for r in range(rounds):
            print("round: " + str(r))

            # initialize the board
            board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

            # connect the alarm signal with the handler
            #signal.signal(signal.SIGALRM, handler)

            # play the game
            winner = 0
            while True:
                end = False
                """
                CAHNGE:
                Added turn_id to the loop, this keeps the turn id separate from the 
                <GomokuAgent>.ID which is accessable and writeable from inside GomokuAgent
                """
                for player, turn_id in [(player1, 1), (player2, -1)]:
                    id, board = turn(board, player, turn_id)
                    print(board)
                    """
                    CHANGE:
                    Move draw check to inside play loop. A draw will always be decided after player 1's turn and so
                    insisting player 2 must always make a move after player 1 will lead to a loss for player 2 where
                    a draw was possible
                    """
                    if not 0 in board:
                        print("Draw.")
                        end = True
                        if swap == 0:
                            player1draw_f += 1
                        else:
                            player1draw_s += 1
                        break
                    if id != 0:
                        print("Winner: " + str(id))
                        end = True
                        if(id == 1):
                            if swap == 0:
                                player1wins_f +=1
                            else:
                                player2wins_f += 1
                        else:
                            if swap ==0:
                                player2wins_s +=1
                            else:
                                player1wins_s += 1
                        break
                if end:
                    break
    print("rounds: " + str(rounds))
    print("player 1: " + p1Dir + " first:")
    print("player " + p1Dir + " first wins: " + str(player1wins_f) + "player " + p2Dir + " second wins: " + str(player2wins_s) + " draws : " + str(player1draw_f))
    print("player 2: " + p2Dir + " first:")
    print("player " + p2Dir + " first wins: " + str(player2wins_f) + "player " + p1Dir + " second wins: " + str(player1wins_s) + " draws : " + str(player1draw_s))

if __name__ == '__main__':
    sys.exit(main());
