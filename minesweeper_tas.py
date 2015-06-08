# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 21:48:21 2015

@author: colinh
"""

import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
 
#felt: 'c-2D', 'c-3D', etc
 
#work piles: work1, work2... work8
#free cell piles: temp1, ... temp4
#completion piles: good1, ... good4
grid =[[-1 for j in range(30)] for i in range(16)]
cell_queue = []
cell_bomb_probs = {}
processed_cells = []


class TAS:
    

    def __init__(self):
        #select the headless web browser (whatever is installed)
        driver = webdriver.Firefox()

        f = open('minesweeper_logfile.txt', 'a')

        game_number = 1
        while True and game_number == 1:
            driver.get('http://minesweeperonline.com/')

            f.write(str(game_number) + "\n")
            self.play_game(driver, f)
            time.sleep(3)
            game_number += 1

        f.close()

    def play_game(self, driver, f):
        self.print_grid()
        print "///////////////////////////////" 
        self.print_grid()
        driver.find_element_by_id("2_15").click()
        print "///////////////////////////////"
        self.print_grid()
        cell_tuple_temp = self.string_to_tuple("2_15")
        self.refresh_specific_cells(driver, cell_tuple_temp)
        
        
        while True:
            cell_tuple_temp = min(cell_bomb_probs, key = cell_bomb_probs.get)
            cell_string_temp = self.tuple_to_string(cell_tuple_temp)
            driver.find_element_by_id(cell_string_temp).click()
            self.refresh_specific_cells(driver, cell_tuple_temp)
            del cell_bomb_probs[cell_tuple_temp]
        
        print "///////////////////////////////"
        self.print_grid()

    #add any >0 val cell to the queue
    # for each cell in the queue
    ## update the prob to max
    ## if prob == 1:
    ### deiterate all cells around


    def refresh_specific_cells(self, driver, cell_tuple):
        html = driver.page_source
        soup = BeautifulSoup(html, "html5lib")
        
        queue = [cell_tuple]
        processed_cells = []
                
        while len(queue) > 0:

            x, y = queue.pop(0)
            cell_string = self.tuple_to_string((x, y))
            cell_soup = soup.find("div", {"id":cell_string})
            cell_value = cell_soup['class'][-1]
            new_val = self.process_cell(cell_value)
            if grid[x][y] != new_val:
                grid[x][y] = new_val
                if (grid[x][y]>0):
                    processed_cells.append(((x,y),grid[x][y]))

                queue = queue + self.get_valid_neighbors(x,y)
   
        for cell in processed_cells:
            self.update_probs(cell[0][0], cell[0][1], cell[1])
#        print "probs"
#        print cell_bomb_probs

        
    def refresh_all_cells(self, driver):
        html = driver.page_source
        soup = BeautifulSoup(html, "html5lib")
        
        for y in xrange(30):
            for x in xrange(16):
                cell_string = self.tuple_to_string(x, y)
                cell_soup = soup.find("div", {"id":cell_string})
                cell_value = cell_soup['class'][-1]
                grid[x][y] = self.process_cell(cell_value)
        
    #convert string "x_y" to tuple (x-1, y-1)
    def string_to_tuple(self, string):
        string_list = string.split('_')
        return (int(string_list[0])-1, int(string_list[1])-1)
    
    #convert tuple (x, y) to string "x+1_y+1"
    def tuple_to_string(self, cell_tuple):
        x, y = cell_tuple
        return str(x+1) +"_"+ str(y+1)

    def process_cell(self, string_value):
        if string_value == "blank":
            return -1
        else:
            string_value_list = list(string_value)
            return int(string_value_list[-1])
    
    def update_probs(self, x, y, val):
        neighbor_cells = []
        for i in range(-1,2):
            for j in range(-1,2):
                if ((x,y)!=(x+i,y+j)):
                    if (-1<x+i<16 and -1<y+j<30):
                        if grid[x+i][y+j]==-1:
                            neighbor_cells.append((x+i,y+j))
        new_prob = float(val)/float(len(neighbor_cells))
#        print "neighbor cells for:"
#        print x, y
#        print neighbor_cells
        for cell in neighbor_cells:
            x, y = cell
            if (x,y) in cell_bomb_probs:
                cell_bomb_probs[(x,y)] = max([new_prob, cell_bomb_probs[(x,y)]])
            else:
                cell_bomb_probs[(x,y)] = new_prob
            
    def get_valid_neighbors(self, x, y):
        neighbors = []
        for i in range(-1,2):
            for j in range(-1,2):
                if ((x,y)!=(x+i,y+j)):
                    if (-1<x+i<16 and -1<y+j<30):
                        neighbors.append((x+i,y+j))
        return neighbors
    
    def print_grid(self):
        for x in range(0,16):
            print grid[x]
                    
    def click(self, driver, felt):
        #driver.find_element_by_class_name('c-QS').click()
        driver.find_element_by_class_name(felt).click()

TAS()