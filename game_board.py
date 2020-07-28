import pygame as pg
import numpy as np
from math import *
import random


class Board(object):

    def __init__(self, display_size, board_size):
        self.board_size = board_size
        self.display_size = display_size
        self.square_size = display_size/board_size
        self.piece_radius = floor(self.square_size/2 - 10) #20 pixel buffer

        self.screen = pg.display.set_mode((display_size, display_size))

        #board starting configuration
        self.board =   np.array([['', '', '', '', '', '', '', ''],
                                ['', '', '', '', '', '', '', ''],
                                ['', '', '', '', '', '', '', ''],
                                ['', '', '', 'white', 'black', '', '', ''],
                                ['', '', '', 'black', 'white', '', '', ''],
                                ['', '', '', '', '', '', '', ''],
                                ['', '', '', '', '', '', '', ''],
                                ['', '', '', '', '', '', '', '']])

        self.board_copy = self.board.copy()

        #used for evaluating the strength of moves in the minimax algorithm
        self.valuesB =  np.array([[500,  25,  50,  50,  50,  50,  25, 500],
                                [ 25, -10,  -5,  -5,  -5,  -5, -10,  25],
                                [ 50,  -5,   1,   1,   1,   1,  -5,  50],
                                [ 50,  -5,   1,   1,   1,   1,  -5,  50],
                                [ 50,  -5,   1,   1,   1,   1,  -5,  50],
                                [ 50,  -5,   1,   1,   1,   1,  -5,  50],
                                [ 25, -10,  -5,  -5,  -5,  -5, -10,  25],
                                [500,  25,  50,  50,  50,  50,  25, 500]])

        self.valuesW = self.valuesB.copy()


    def initial_display(self):
        '''Displays the board background and the lines.'''

        self.screen.fill((50, 100, 73)) #board colour (green)
        colour = (68, 112, 82)     #line colour (light green)

        #draw the grid lines
        for i in range(self.board_size):
            pg.draw.line(self.screen, colour, ((i*self.square_size), 0),((i*self.square_size), self.display_size))
            pg.draw.line(self.screen, colour, (0, (i*self.square_size)),(self.display_size, (i*self.square_size)))

        pg.display.flip()


    def display(self):
        '''Displays the pieces that are on the game board.'''

        black = (4, 3, 3)
        white = (248, 247, 255)

        #draw each of the pieces that are on the board
        for row in range(self.board_size):
            for column in range(self.board_size):
                if self.board[row][column]:

                    centre = (floor(row*(self.square_size)+(self.square_size/2)),
                            floor(column*(self.square_size)+(self.square_size/2)))

                    if self.board[row][column] == 'black':
                        colour = black
                    else:
                        colour = white

                    pg.draw.circle(self.screen, colour, centre, self.piece_radius)

        pg.display.flip()

    def place(self, row, column, piece):
        '''Places a piece on the board at the provided index.'''
        self.board[row][column] = piece


    def isOnBoard(self, row, column):
        '''Returns True if the index exists on the game board, and False otherwise.'''
        return(row>=0 and row<self.board_size and column>=0 and column<self.board_size)


    def isValidMove(self, row, column, piece):
        '''Returns False if the move is invalid and returns a list of the pieces
        that need to be flipped if the move is valid.'''

        #if the space is already filled or if it is not on the game board it
        #isn't valid
        if self.board[row][column]!='' or not self.isOnBoard(row, column):
            return False

        #place the piece on the board temporarily
        self.place(row, column, piece)

        if piece == 'white':
            otherPiece = 'black'
        else:
            otherPiece = 'white'

        piecesToFlip = [] #this list will keep track of pieces to be flipped
        #move in every possible direction
        for xdir, ydir in [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]:
            x, y = row, column
            #take one step forward
            x += xdir
            y += ydir
            if self.isOnBoard(x, y) and self.board[x][y]==otherPiece:
                #there is an opponent's piece next to our piece, so we can keep moving
                x += xdir
                y += ydir
                if not self.isOnBoard(x, y):
                    #we have moved off the board, continue and search through
                    #the next direction in the list
                    continue

                while self.board[x][y]==otherPiece:
                    #keep moving in the same direction
                    x += xdir
                    y += ydir
                    if not self.isOnBoard(x, y):
                        #STOP! we have reached the edge of the board
                        break

                if not self.isOnBoard(x, y):
                    #we have moved off the board without hitting another one
                    #of our pieces, continue and each through the next direction
                    continue

                if self.board[x][y]==piece:
                    #we have reached one of our own pieces and so the move is
                    #valid and there are pieces to flip over

                    #move backwards in the same direction and record the pieces
                    #to be flipped until reaching starting position
                    while True:
                        x -= xdir
                        y -= ydir
                        piecesToFlip.append((x, y))
                        if x==row and y==column:
                            break


        #undo the temporary piece placement
        self.place(row, column, '')

        if len(piecesToFlip) == 0:
            #it is an invalid move if no pieces can be flipped
            return False

        return piecesToFlip


    def findAvailable(self, piece):
        '''Returns a list of lists of available moves and the pieces that need
        to be flipped for that move. If no moves are available, return False.'''

        available = []  #list that contains lists of available moves and their
                        #respective pieces that need to be flipped
        for row in range(self.board_size):
            for column in range(self.board_size):
                piecesToFlip = self.isValidMove(row, column, piece)
                if piecesToFlip:
                    piecesToFlip.append((row, column))
                    available.append(piecesToFlip)
        if len(available)==0:
            return False
        return available


    def checkFinished(self):
        '''Returns True if no more moves can be made, and returns False otherwise.'''

        if self.isFull():
            #if the board is full, the game is over
            return True
        elif not self.findAvailable('black') and not self.findAvailable('white'):
            #if both players have no available moves left, the game is over
            return True

        #game still has available moves left
        return False


    def isFull(self):
        '''Returns True if the board is full, and False otherwise.'''

        for row in range(self.board_size):
            for column in range(self.board_size):
                if self.board[row][column] == '':
                    return False
        return True

    def findWinner(self):
        '''Returns a tuple containing the black player's score and the white
        player's score respectively.'''

        #find the scores of each player
        blackScore = 0
        whiteScore = 0
        for row in range(self.board_size):
            for column in range(self.board_size):
                if self.board[row][column] == 'black':
                    blackScore += 1
                elif self.board[row][column] == 'white':
                    whiteScore += 1

        #show the winner along with the scores
        if blackScore > whiteScore:
            print(f'Congratulations, you win!\nPlayer: {blackScore} tiles\nComputer: {whiteScore} tiles')
        elif whiteScore > blackScore:
            print(f'Unlucky, computer wins.\nPlayer: {blackScore} tiles\nComputer: {whiteScore} tiles')
        else:
            print(f'The game is a tie.\nPlayer: {blackScore} tiles\nComputer: {whiteScore} tiles')


    def randomMove(self, piece):
        '''Returns the index of a random available move.'''

        available_moves = self.findAvailable(piece)
        return random.choice(available_moves)[-1]
        #the move is always the last index pair in the pieces to be flipped list


    def bestMove(self, piece):
        '''Returns the index of the best available move. Evaluated using a
        minimax algorithm.'''

        if piece == 'white':
            #maximising
            bestValue = -inf
            otherPiece = 'black'
        else:
            #minimising
            bestValue = inf
            otherPiece = 'white'

        availableMoves = self.findAvailable(piece)
        move = []
        for piecesToFlip in availableMoves:

            #temporarily place/flip all the pieces
            for (row, column) in piecesToFlip:
                self.place(row, column, piece)

            #check that the other player has valid moves available and does not
            #forfeit their next turn
            if self.findAvailable(otherPiece):
                next_turn = otherPiece
            else:
                next_turn = piece

            #update point value grids
            self.updatePointValues()

            #calculate the value of the board
            alpha = -inf
            beta = inf
            value = self.minimax(0, next_turn, alpha, beta)

            #undo the temporary placements/flips
            for (row, column) in piecesToFlip:
                self.place(row, column, otherPiece)
            #new piece that was placed (not flipped) is always at the end of the list
            (x, y) = piecesToFlip[-1]
            self.place(x, y, '')

            #update the best value if value is better
            if piece == 'white':
                #maximising
                if value >= bestValue:
                    if value == bestValue:
                        move.append((x, y))
                    else:
                        move = [(x, y)]
                    bestValue = value
            else:
                #minimising
                if value <= bestValue:
                    if value == bestValue:
                        move.append((x, y))
                    else:
                        move = [(x, y)]
                    bestValue = value

        return random.choice(move)


    def minimax(self, depth, whose_turn, alpha, beta):
        '''Minimax algorithm with alpha beta pruning.'''

        availableMoves = self.findAvailable(whose_turn)

        #difficulty level
        if (not availableMoves or depth > 5):
            return self.boardScore()

        if whose_turn == 'white':
            #Computer's turn (Maximising)
            bestValue = -inf
            otherPiece = 'black'
        else:
            #Player's turn (Minimising)
            bestValue = inf
            otherPiece = 'white'


        for piecesToFlip in availableMoves:

            #temporarily place/flip all the pieces
            for (row, column) in piecesToFlip:
                self.place(row, column, whose_turn)

            #check that the other player has valid moves available and does not
            #forfeit their next turn
            if self.findAvailable(otherPiece):
                next_turn = otherPiece  #other player's turn
            else:
                next_turn = whose_turn  #same player's turn

            #update point value grids
            self.updatePointValues()

            #calculate board value
            value = self.minimax(depth+1, next_turn, alpha, beta)

            #undo the temporary placements/flips
            for (row, column) in piecesToFlip:
                self.place(row, column, otherPiece)
            #new piece that was placed (not flipped) is always at the end of the list
            (x, y) = piecesToFlip[-1]
            self.place(x, y, '')

            if whose_turn == 'white':
                #maximising
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
                bestValue = max(value, bestValue)
            else:
                #minimising
                beta = min(beta, value)
                if beta <= alpha:
                    break
                bestValue = min(value, bestValue)

        return bestValue


    def updatePointValues(self):
        '''Updates the two point value grids used for the evaluation function
        in the minimax algorithm.'''

        self.updateCorners()
        self.updateRowsandColumns()

    def updateCorners(self):
        '''Updates the point values around the corner pieces for both grids.'''

        #Top Left Corner
        if self.board[0][0] == 'black':
            self.valuesW[0][1] = -25
            self.valuesW[1][0] = -100
            self.valuesW[1][1] = -25
            self.valuesB[0][1] = 50
            self.valuesB[1][0] = 50
            self.valuesB[1][1] = 50
        elif self.board[0][0] == 'white':
            self.valuesW[0][1] = 50
            self.valuesW[1][0] = 50
            self.valuesW[1][1] = 50
            self.valuesB[0][1] = -25
            self.valuesB[1][0] = -100
            self.valuesB[1][1] = -25

        #Top Right Corner
        if self.board[0][7] == 'black':
            self.valuesW[0][6] = -25
            self.valuesW[1][7] = -100
            self.valuesW[1][6] = -25
            self.valuesB[0][6] = 50
            self.valuesB[1][7] = 50
            self.valuesB[1][6] = 50
        elif self.board[0][7] == 'white':
            self.valuesW[0][6] = 50
            self.valuesW[1][7] = 50
            self.valuesW[1][6] = 50
            self.valuesB[0][6] = -25
            self.valuesB[1][7] = -100
            self.valuesB[1][6] = -25

        #Bottom Left Corner
        if self.board[7][0] == 'black':
            self.valuesW[6][0] = -25
            self.valuesW[6][1] = -100
            self.valuesW[7][1] = -25
            self.valuesB[6][0] = 50
            self.valuesB[6][1] = 50
            self.valuesB[7][1] = 50
        elif self.board[7][0] == 'white':
            self.valuesW[6][0] = 50
            self.valuesW[6][1] = 50
            self.valuesW[7][1] = 50
            self.valuesB[6][0] = -25
            self.valuesB[6][1] = -100
            self.valuesB[7][1] = -25

        #Bottom Right Corner
        if self.board[7][7] == 'black':
            self.valuesW[7][6] = -25
            self.valuesW[6][7] = -100
            self.valuesW[6][6] = -25
            self.valuesB[7][6] = 50
            self.valuesB[6][7] = 50
            self.valuesB[6][6] = 50
        elif self.board[7][7] == 'white':
            self.valuesW[7][6] = 50
            self.valuesW[6][7] = 50
            self.valuesW[6][6] = 50
            self.valuesB[7][6] = -25
            self.valuesB[6][7] = -100
            self.valuesB[6][6] = -25

    def updateRowsandColumns(self):
        '''Updates the point values for the middle rows and columns.'''

        for n in range(2, 6):
            #Top Row
            if self.board[0][n] == 'black':
                self.valuesW[1][n] = -5
                self.valuesB[1][n] = 10
            elif self.board[0][n] == 'white':
                self.valuesW[1][n] = 10
                self.valuesB[1][n] = -5

            #Bottom Row
            if self.board[7][n] == 'black':
                self.valuesW[6][n] = -5
                self.valuesB[6][n] = 10
            elif self.board[7][n] == 'white':
                self.valuesW[6][n] = 10
                self.valuesB[6][n] = -5

            #Left Column
            if self.board[n][0] == 'black':
                self.valuesW[n][1] = -5
                self.valuesB[n][1] = 10
            elif self.board[n][0] == 'white':
                self.valuesW[n][1] = 10
                self.valuesB[n][1] = -5

            #Right Column
            if self.board[n][7] == 'black':
                self.valuesW[n][6] = -5
                self.valuesB[n][6] = 10
            elif self.board[n][7] == 'white':
                self.valuesW[n][6] = 10
                self.valuesB[n][6] = -5


    def boardScore(self):
        '''Returns the score of the board state, Computer (White) is maximising
        so a higher score is better.'''

        computer = 0
        human = 0
        for row in range(self.board_size):
            for column in range(self.board_size):
                if self.board[row][column] == 'white':
                    computer += 1
                elif self.board[row][column] == 'black':
                    human += 1

        return computer - human
