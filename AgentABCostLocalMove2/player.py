import numpy as np
import math
import time
from misc import winningTest, legalMove
from gomokuAgent import GomokuAgent

### Alpha beta, cost algorithm
class Player(GomokuAgent):
    start = 0
    prev_state = None
    prev_score = 0
    last_player_move = None

    def move(self, board):
        self.start = time.time()

        empty_board = math.pow(self.BOARD_SIZE, 2)
        board_count = self.empty_squares(board)
        if board_count == empty_board or board_count == empty_board-1:
            self.prev_state = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
            self.last_player_move = None
            self.prev_score = 0

        if board_count == empty_board:
            #c = math.floor(self.BOARD_SIZE/2)
            #return (c, c)
            while True:
                moveLoc = tuple(np.random.randint(self.BOARD_SIZE, size=2))
                if legalMove(board, moveLoc):
                    return moveLoc

        out = self.minimax_ab(board, self.ID, 99, -999999, 999999, self.prev_state, None, self.prev_score)[1]
        row, col = out
        print("time: "+ str(time.time() - self.start))
        self.prev_score -= self.score_state(board, self.ID, out)
        board[row][col] = self.ID
        self.prev_state = board
        self.prev_score += self.score_state(board, self.ID, out)
        print("new score: " + str(self.prev_score))
        print("player " + str(self.ID) + " turn time: " + str(self.check_timer()))
        return out

    def get_last_move(self, board):
        if (board == self.prev_state).all():
            return None
        for r in range(len(board)):
            for c in range(len(board[r])):
                if(board[r][c] != self.prev_state[r][c]):
                    return (r, c)

    def minimax_ab(self, board, player_id, depth, alpha, beta, prev_state, prev_move, prev_score):
        max_player = self.ID
        other_player = -player_id

        empty_squares = self.empty_squares(board)
        if prev_move!= None:
             if (time.time() - self.start > 3):
             #if depth == 0:
                if other_player == max_player:
                    return [prev_score + ((self.score_state(board, other_player, prev_move) - self.score_state(prev_state, other_player, prev_move))* ((empty_squares + 1)/100)), None, alpha, beta]
                else:
                    return [prev_score - ((self.score_state(board, other_player, prev_move) - self.score_state(prev_state, other_player, prev_move) )* ((empty_squares + 1)/100)), None, alpha, beta]



        if (winningTest(other_player, board, self.X_IN_A_LINE)):
            if other_player == max_player:
                #return [(999999999)*(empty_squares+1), None, alpha, beta]
                return [99999999999, None, alpha, beta]
            else:
                #return [(-999999999)*(empty_squares+1), None, alpha, beta]
                return [-99999999999, None, alpha, beta]
        elif empty_squares == 0:
            return [0, None, alpha, beta]

        if player_id == max_player:
            best = [-math.inf, None, alpha, beta]
        else:
            best = [math.inf, None, alpha, beta]

        legal_moves = self.gen_moves(board)

        for move in legal_moves:
            row, col = move
            board_copy = board.copy()
            board[row][col] = player_id
            new_score = self.minimax_ab(board, other_player, depth-1, alpha, beta, board_copy, move, prev_score+ (self.score_state(board, player_id, move) - self.score_state(board_copy, player_id, move)))

            board[row][col] = 0
            new_score[1] = move

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
        #print("best: " + str(best))
        return best

    def empty_squares(self, board):
        return (board == 0).sum()

    def gen_moves(self, board):
        legal_moves = []
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                move = (row, col)
                if (legalMove(board, move) and self.check_nearby(board, move)):
                    legal_moves.append(move)
        return legal_moves

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

    def score_state(self, board, player_id, move):
        score = 0
        score += (self.rowTest(player_id, board, move) + self.diagTest(player_id, board, move))
        score -= (self.rowTest(-player_id, board, move) + self.diagTest(-player_id, board, move))
        boardPrime = np.rot90(board)
        row, col = move
        new_move = (self.BOARD_SIZE-col-1, row)
        score += (self.rowTest(player_id, boardPrime, new_move) + self.diagTest(player_id, boardPrime, new_move))
        score -= (self.rowTest(-player_id, boardPrime, new_move) + self.diagTest(-player_id, boardPrime, new_move))
        #print("score: " + str(score))
        return score

    def rowTest(self, player_id, board, move):
        row, col = move
        out = 0
        for c in range(self.BOARD_SIZE - self.X_IN_A_LINE + 1):
            id_count = 0
            id_streak = 0
            max_streak = 0
            flag = True
            for i in range(self.X_IN_A_LINE):
                if board[row, c + i] == -player_id:
                    flag = False
                    id_streak = 0
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
        return out

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
                    id_streak = 0
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


        #print("diag array: " + str(diag))
        return out



    def check_timer(self):
        return time.time()-self.start