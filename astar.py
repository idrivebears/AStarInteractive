# -*- coding: utf-8 -*-

'''
A* implementation
Alejandro Walls Rancaño
ITESO


DISCLAIMER:
-code was rushed, do not look for coding tips in here
-no diagonal movement considered, although adding it is very simple
-the way i handled the grid couldve been done waaaay better, but its late now and i dont want to fix it atm



'''


import pygame
import sys
from enum import Enum

pygame.init()

#PARAMETERS
square_size = 30
map_size = 30
start_square = (5,10)
goal_square = (10,15)

draw_on = False

#get cmd params
if len(sys.argv) == 3:
    square_size = int(sys.argv[1])
    map_size = int(sys.argv[2])

normal_move = 10        #cost to do a normal move (up,down,left,right)
diagonal_move = 14      #cost to do diagonal move

size = width, height = square_size*map_size, square_size*map_size
screen = pygame.display.set_mode(size)


#Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
BLUE = (51,205,255)
YELLOW = (255,255,0)
ORANGE = (255,153, 0)
GREEN = (50,255,50)

current_mode = "obs"

class Square_Type(Enum):
        empty = 0
        obstacle = 1
        start = 2
        end = 3
        search = 4
        path = 5

class Square(object):
    def __init__(self, square_type = Square_Type.empty):
        self.square_type = square_type
        self.parent = None
        self.Fcost = 0
        self.Gcost = 0
        self.Hcost = 0
    def __lt__(self, other):
        return self.Fcost < other.Fcost

#Initialize grid
grid = [[Square() for x in range(map_size)] for y in range(map_size)]

#Set start loc and goal
grid[start_square[0]][start_square[1]] = Square(Square_Type.start)
grid[goal_square[0]][goal_square[1]] = Square(Square_Type.end)

cur_selected = []
cur_selected.append(0)
cur_selected.append(0)


def get_color(square_type):
    if square_type == Square_Type.empty:
         return WHITE        #empty
    elif square_type == Square_Type.obstacle:
        return BLACK      #obstacle
    elif square_type == Square_Type.start:
        return GREEN       #start
    elif square_type == Square_Type.end:
         return RED        #end
    elif square_type == Square_Type.search:
         return YELLOW     #search
    elif square_type == Square_Type.path:
         return ORANGE     #search
    else: return WHITE

def draw_grid(grid):
    for i in range(map_size):
        for j in range(map_size):
            if i == cur_selected[0] and j == cur_selected[1]:
                if current_mode == "str":
                    pygame.draw.rect(screen, GREEN,(i*square_size, j*square_size, square_size,square_size), 0)
                elif current_mode == "end":
                    pygame.draw.rect(screen, RED,(i*square_size, j*square_size, square_size,square_size), 0)
                else:
                    pygame.draw.rect(screen, BLUE,(i*square_size, j*square_size, square_size,square_size), 0)
            else:
                pygame.draw.rect(screen, get_color(grid[i][j].square_type),(i*square_size, j*square_size, square_size,square_size), 0)

def clear_grid(grid):
    for i in range(map_size):
        for j in range(map_size):
            if grid[i][j].square_type != Square_Type.obstacle:
                grid[i][j] = Square()
            if i == start_square[0] and j == start_square[1]:
                grid[i][j].square_type = Square_Type.start
            elif i == goal_square[0] and j == goal_square[1]:
                grid[i][j].square_type = Square_Type.end

def convert_mousepos_to_gridpos(mouse_pos):
    x = 0
    y = 0
    x = int(mouse_pos[0]/square_size)
    y = int(mouse_pos[1]/square_size)

    grid_pos = (x, y);

    return grid_pos

def mod_map(position):
    sel_square = convert_mousepos_to_gridpos(position)
    global start_square
    global goal_square
    global current_mode

    if sel_square == start_square and current_mode == "obs":
        current_mode = "str"
        return
    elif sel_square == goal_square and current_mode == "obs":
        current_mode = "end"
        return

    if current_mode == "str":
        start_square = sel_square
        current_mode = "obs"
        clear_grid(grid)
        return
    elif current_mode == "end":
        goal_square = sel_square
        current_mode = "obs"
        clear_grid(grid)
        return

    if(current_mode == "obs"):
        if grid[sel_square[0]][sel_square[1]].square_type == Square_Type.obstacle:
            grid[sel_square[0]][sel_square[1]] = Square(Square_Type.empty)
        else:
            grid[sel_square[0]][sel_square[1]] = Square(Square_Type.obstacle)

def generate_hcost():
    for i in range(map_size):
        for j in range(map_size):
            grid[i][j].Hcost = (abs(goal_square[0] - i) + abs(goal_square[1] - j)) *10
            #print(str(i) + ", " + str(j) + " hcost: " + str(grid[i][j].Hcost))

def calculate_cost(g, square_pos):
    if grid[square_pos[0]][square_pos[1]].parent == None:
        gcost = g
    else:
        gcost = g + grid[square_pos[0]][square_pos[1]].parent.Gcost

    fcost = gcost + grid[square_pos[0]][square_pos[1]].Hcost
    return fcost

def check_square(cur_check, square, open_list):
    if square not in open_list:
        grid[square[0]][square[1]].Fcost = calculate_cost(normal_move, square)
        grid[square[0]][square[1]].parent = grid[cur_check[0]][cur_check[1]]
        #print("Right:"+str(grid[square[0]][square[1]].Fcost))
        open_list.append(square)
    else:
        if grid[cur_check[0]][cur_check[1]].Gcost + normal_move < grid[square[0]][square[1]].Gcost:
            grid[square[0]][square[1]].Fcost = calculate_cost(normal_move, square)
            #print("Down:"+str(grid[square[0]][square[1]].Fcost))
            grid[square[0]][square[1]].parent = grid[cur_check[0]][cur_check[1]]
            open_list.remove(square)
            open_list.append(square)

def path_find(start_square, goal_square):

    generate_hcost()
    #print("Done generating hcosts")

    path_found = False

    open_list = []
    closed_list = []

    open_list.append(start_square)

    while(len(open_list) > 0):

        #cur_check = open_list.pop()

        smallest = open_list[0]
        for s in open_list:
            if grid[s[0]][s[1]].Fcost < grid[smallest[0]][smallest[1]].Fcost:
                smallest = s
        cur_check = smallest
        open_list.remove(cur_check)


        closed_list.append(cur_check)

        #print("Checking: " + str(cur_check))

        cur_r = (cur_check[0]+1, cur_check[1])      #square to right
        cur_l = (cur_check[0]-1, cur_check[1])      #square to left
        cur_u = (cur_check[0], cur_check[1]-1)      #square up
        cur_d = (cur_check[0], cur_check[1]+1)    #square down

        #Right check
        if cur_r[0] < map_size:
            if grid[cur_r[0]][cur_r[1]].square_type != Square_Type.obstacle and cur_r not in closed_list:
                check_square(cur_check, cur_r, open_list)
        #Left check
        if cur_l[0] >= 0:
            if grid[cur_l[0]][cur_l[1]].square_type != Square_Type.obstacle and cur_l not in closed_list:
                check_square(cur_check, cur_l, open_list)
        #Up check
        if cur_u[1] >= 0:
            if grid[cur_u[0]][cur_u[1]].square_type != Square_Type.obstacle and cur_u not in closed_list:
                check_square(cur_check, cur_u, open_list)
        #Down check
        if cur_d[1] < map_size:
            if grid[cur_d[0]][cur_d[1]].square_type != Square_Type.obstacle and cur_d not in closed_list:
                check_square(cur_check, cur_d, open_list)

        if goal_square in open_list:
            path_found = True
            break

    if path_found == False:
        print("No path found")
        return

    #work backwards from end square to start
    end_square = grid[goal_square[0]][goal_square[1]]
    end_square = end_square.parent

    #paint path found
    while(end_square.parent != None):
        end_square.square_type = Square_Type.path
        end_square = end_square.parent


#MainLoop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
            	draw_on = True
                mod_map(pygame.mouse.get_pos())
                clear_grid(grid)
            elif pygame.mouse.get_pressed()[2]:
                clear_grid(grid)
                path_find(start_square, goal_square)
        elif event.type == pygame.MOUSEMOTION:
            cur_selected[0] = convert_mousepos_to_gridpos(pygame.mouse.get_pos())[0]
            cur_selected[1] = convert_mousepos_to_gridpos(pygame.mouse.get_pos())[1]
            if draw_on:
            	mod_map(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
        	if not pygame.mouse.get_pressed()[0]:
        		draw_on = False


        screen.fill(WHITE)
        draw_grid(grid)
        pygame.display.flip()
