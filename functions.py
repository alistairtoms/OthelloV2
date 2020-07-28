import pygame as pg
from math import floor

def getIndex(square_size):
    '''Returns the tuple index of the square under the mouse.'''

    (xpos, ypos) = pg.mouse.get_pos()
    x = floor(xpos/square_size)
    y = floor(ypos/square_size)

    return (x, y)
