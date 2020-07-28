from game_board import Board
from functions import *
import pygame as pg
import sys
from time import *

pg.init()

#constants
DISPLAY_SIZE = 800
BOARD_SIZE = 8

#initisalise the game board
board = Board(DISPLAY_SIZE, BOARD_SIZE)
board.initial_display()
board.display()

playersTurn = True  #human player goes first
gameFinished = False


while not gameFinished:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            pg.quit()
            sys.exit()


    if playersTurn:

        # PLAYER'S TURN #

        if pg.mouse.get_pressed()[0]:

            #check if a valid square is clicked
            (row, column) = getIndex(board.square_size)
            piecesToFlip = board.isValidMove(row, column, 'black')

            if piecesToFlip:
                #place piece and flip the surrounded pieces
                board.place(row, column, 'black')
                for (row, column) in piecesToFlip:
                    board.place(row, column, 'black')

                board.display()
                pg.display.flip()

                if board.findAvailable('white'):
                    #if the other player has available moves, then it becomes their
                    #turn, otherwise it is still this players turn
                    playersTurn = False
                    continue

                elif board.checkFinished():
                    #if the game has finished, get scores and display the winner
                    board.findWinner()
                    sleep(8)
                    gameFinished = True


    else:

        # COMPUTER'S TURN #

        #(row, column) = getIndex(board.square_size)
        #(row, column) = board.randomMove('white')
        (row, column) = board.bestMove('white')
        piecesToFlip = board.isValidMove(row, column, 'white')

        #place piece and flip the surrounded pieces
        board.place(row, column, 'white')
        for (row, column) in piecesToFlip:
            board.place(row, column, 'white')

        board.display()
        pg.display.flip()

        if board.findAvailable('black'):
            #if the other player has available moves, then it becomes their
            #turn, otherwise it is still this players turn
            playersTurn = True
            continue

        elif board.checkFinished():
            #if the game has finished, get scores and display the winner
            board.findWinner()
            sleep(8)
            gameFinished = True
