import numpy as np
import math
import time
from misc import winningTest, legalMove
from gomokuAgent import GomokuAgent

### Alpha beta, cost algorithm
class Player(GomokuAgent):
    start = 0 ## Time at start of round to know when to end recursions

    def move(self, board):
        self.start = time.time()

        ##If board is empty (you are first move) place in center of board
        if self.empty_squares(board) ==  math.pow(self.BOARD_SIZE, 2):
            c = math.floor(self.BOARD_SIZE/2)
            return (c, c)
            #while True:
            #    moveLoc = tuple(np.random.randint(self.BOARD_SIZE, size=2))
            #    if legalMove(board, moveLoc):
            #        return moveLoc
        
        ##Start minimax algorith to find best move
        out = self.minimax_ab(board, self.ID, 99, -999999, 999999, np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int), None, 0)[1]
        print("player " + str(self.ID) + " turn time: " + str(self.check_timer()))
        return out


    def minimax_ab(self, board, player_id, depth, alpha, beta, prev_state, prev_move, prev_score):
        max_player = self.ID
        other_player = -player_id

        empty_squares = self.empty_squares(board)
        #Cost function for board when time limit reached
        if prev_move!= None:
             if (time.time() - self.start > 2.65):
             #if depth == 0:
                if other_player == max_player:
                    return [prev_score + ((self.score_state(board, other_player, prev_move) - self.score_state(prev_state, other_player, prev_move))* ((empty_squares + 1)/100)), None, alpha, beta]
                else:
                    return [prev_score - ((self.score_state(board, other_player, prev_move) - self.score_state(prev_state, other_player, prev_move) )* ((empty_squares + 1)/100)), None, alpha, beta]


        #Check if board state wins
        if (winningTest(other_player, board, self.X_IN_A_LINE)):
            if other_player == max_player:
                return [(9999999)*(empty_squares+1), None, alpha, beta]
            else:
                return [(-9999999)*(empty_squares+1), None, alpha, beta]
        elif empty_squares == 0:
            return [0, None, alpha, beta]

        #Set best to worst values
        if player_id == max_player:
            best = [-math.inf, None, alpha, beta]
        else:
            best = [math.inf, None, alpha, beta]

        #Generate moves then iterate
        #Create new board score board using minimax
        legal_moves = self.gen_moves(board)

        for move in legal_moves:
            row, col = move
            board_copy = board.copy()
            board[row][col] = player_id
            new_score = self.minimax_ab(board, other_player, depth-1, alpha, beta, board_copy, move, prev_score+ (self.score_state(board, player_id, move) - self.score_state(board_copy, player_id, move)))

            board[row][col] = 0
            new_score[1] = move

            #Alpha beta pruning
            if player_id == max_player:
                if (new_score[0] > best[0]):
                    best = new_score
                if best[0] >= beta:
                    return best
                if best[0] > alpha:
                    alpha = best[0]
            else:
                if (new_score[0] < best[0]):
                    best = new_score
                if (best[0] <= alpha):
                    return best
                if (best[0] < beta):
                    beta = best[0]
        return best

    #How many empty squares on board
    def empty_squares(self, board):
        return (board == 0).sum()

    #Generates potential moves for board
    def gen_moves(self, board):
        legal_moves = []
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                move = (row, col)
                if (legalMove(board, move) and self.check_nearby(board, move)):
                    legal_moves.append(move)
        return legal_moves

    #Check 5x5 with move as center if a move has been played in area
    def check_nearby(self, board, move):
        if (self.empty_squares(board) == math.pow(self.BOARD_SIZE, 2)):
            return True
        row, col = move
        start_row = row-2 if row > 2 else 0
        start_col = col-2 if col > 2 else 0
        end_row = row+2 if row < self.BOARD_SIZE-2 else self.BOARD_SIZE
        end_col = col+2 if col < self.BOARD_SIZE-2 else self.BOARD_SIZE

        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                if (board[r][c] != 0):
                    return True
        return False

    #Score state by performing row and diag tests, rotating move and board 90
    #Then performing tests again.
    def score_state(self, board, player_id, move):
        score = 0
        score += (self.rowTest(player_id, board, move) + self.diagTest(player_id, board, move))
        score -= (self.rowTest(-player_id, board, move) + self.diagTest(-player_id, board, move))
        boardPrime = np.rot90(board)
        row, col = move
        movePrime = (self.BOARD_SIZE-col-1, row)
        score += (self.rowTest(player_id, boardPrime, movePrime) + self.diagTest(player_id, boardPrime, movePrime))
        score -= (self.rowTest(-player_id, boardPrime, movePrime) + self.diagTest(-player_id, boardPrime, movePrime))
        return score
    
    #Score row of move
    def rowTest(self, player_id, board, move):
        row, col = move
        out = 0
        c = 0
        while c <= self.BOARD_SIZE - self.X_IN_A_LINE:
            id_count = 0
            id_streak = 0
            max_streak = 0
            flag = True
            for i in range(self.X_IN_A_LINE):
                if board[row, c + i] == -player_id:
                    flag = False
                    c+=i
                    break
                if board[row, c + i] == player_id:
                    id_streak += 1
                    id_count += 1
                    if (id_streak > max_streak):
                        max_streak = id_streak
            if flag and id_count > 0:
                if player_id == self.ID:
                    if max_streak == 5:
                        out += 99999999
                    else:
                        out += math.pow(max_streak, 3) + math.pow(id_count, 2)
                else:
                    if max_streak == 5:
                        out += 99999999
                    else:
                        out += math.pow(1 + max_streak, 3) + math.pow(1 + id_count, 2)
            c+=1
        return out

    #Score diagonal of move
    def diagTest(self, player_id, board, move):
        row, col = move
        out = 0

        if row > col:
            start_row = row-col
            start_col = 0
        else:
            start_col = col-row
            start_row = 0


        while (start_row <= self.BOARD_SIZE-self.X_IN_A_LINE and start_col <= self.BOARD_SIZE-self.X_IN_A_LINE):
            id_count = 0
            id_streak = 0
            max_streak = 0
            flag = True
            for i in range(self.X_IN_A_LINE):
                square = board[start_row+i, start_col + i]
                if square == -player_id:
                    flag = False
                    start_col += i
                    start_row += i
                    break
                if square == player_id:
                    id_streak += 1
                    id_count += 1
                    if (id_streak > max_streak):
                        max_streak = id_streak
            if flag and id_count > 0:
                if player_id == self.ID:
                    if max_streak == 5:
                        out += 99999999
                    else:
                        out += math.pow(max_streak, 3) + math.pow(id_count, 2)
                else:
                    if max_streak == 5:
                        out += 99999999
                    else:
                        out += math.pow(1 + max_streak, 3) + math.pow(1 + id_count, 2)
            start_row += 1
            start_col += 1


        return out

    def check_timer(self):
        return time.time()-self.start

# Many versions of agents have been produced and tested for this coursework.
# A basic 3x3 tic-tac-toe AI was initially implemented, when the maximum depth
# of the game state tree can be explored this was perfect as it returned 1 for a win
# or -1 for a loss and optimized upon this. However when it is not possible to reach
# the maximum depth such as when the size of the board was increased and a turn timer
# of 5 secs a cost algorithm must be implemented. This needs to score the boards state
# and return a value. Threat space-search was implemented with a bank of saved
# arrays of threats with a cost attatched to them. In reality the board needed to be
# chopped up too many times with varying sizes of threat patterns and took too long
# to be efficient with 5 second timer. I created an algorithm that searches a
# 5 long array of board and gives a value (if there is no blocking enemy piece)
# of the (amount of friendly pieces)^2 + (highest streak of friendly pieces)^3.
# Enemy costs are weighted slightly higher as when evalutating an enemy piece,
# it would have already been played and therefore when the algorithm tried to mirror
# piece placement to neutralize it, it now looks to block enemy pieces.
# Instead of searching the whole board, to maximize depth the algorithm only looks
# at the weighting of where the move you are going to make's rows and diagonals.
# In the minimax method this is passed forward as current score. Valid moves are
# only selected if they are within a 5x5 of another piece, this cuts down the amount
# of child nodes spawned by the tree significantly.