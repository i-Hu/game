#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/6 16:00
# @Author  : Patrick.hu
# @Site    : 
# @File    : maze.py
# @Software: PyCharm

grid = [
    [1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1],
    [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


def valid(grid, row, column):
    if 0 <= row < len(grid) and 0 <= column < len(grid[0]) and grid[row][column] == 1:
        return True
    else:
        return False


def walk(grid, x, y):
    if x == len(grid) - 1 and y == len(grid[0]) - 1:
        grid[x][y] = 2
        return True

    if valid(grid, x, y):
        grid[x][y] = 2
        if walk(grid, x, y + 1) or walk(grid, x - 1, y) or walk(grid, x, y - 1) or walk(grid, x + 1, y):
            return True
        else:
            grid[x][y] = 3
            return False
    else:
        return False


print(walk(grid, 0, 0))
for i in range(len(grid)):
    print(grid[i])
