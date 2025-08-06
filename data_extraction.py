#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 19:36:02 2025

@author: ruilucasferreira
"""
import pytest
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup

import os

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from time import sleep


#get all names of the pages to scrap from the csv file
stattype = np.loadtxt("./stats_names.csv", delimiter=',', dtype=str)[len(os.listdir("./NBA_Tables")):, 1]

#a cycle for each stat
for cnt in range(len(stattype)):

    #open the browser window
    service = Service(executable_path="/usr/local/bin/chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service=service)
    driver.get(f"https://www.nba.com/stats/players/{stattype[cnt]}?SeasonType=Regular+Season&PerMode=Totals&TypeGrouping=offensive?DistanceRange=By+Zone")
    sleep(1)
    
    #get stat names
    head = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table/thead")
    heads = head.find_elements(By.TAG_NAME, "th")
    head_values = []
    for h in heads:
        head_values.append(h.text)
        
    
    #get number of players (rows) available
    num = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[1]")
    num = int(num.text[:-5])
    
    
    #search all the tables for each stat    
    temp = 0
    player_stats = []
    while temp < num:
        sleep(0.25+np.random.rand()/2)
        #if the site is opened for the first time, it will show up 
        #terms of consent for cookies and for data treatment
        if temp == 0:
            #click accept cookies
            if len(driver.find_elements(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')) != 0:
                sleep(2)
                cookie = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
                cookie.click()
                sleep(2)
                driver.refresh()
                sleep(2)
            #click accept data treatment
            if len(driver.find_elements(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button[2]')) != 0:
                consent = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button[2]')
                consent.click()
                sleep(0.5)
                double_consent = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/div[3]/div[2]/button[2]")
                double_consent.click()
                sleep(0.5)
                
        #get full stats table
        body = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table/tbody")
        
        #get rows and cycle through them
        rows = body.find_elements(By.TAG_NAME, "tr")
        for i, row in enumerate(rows):
            #avoid empty rows (each page can only have 50 rows)
            if i==50 or temp == num:
                break
            temp = temp + 1
            
            #extract data from row
            stat_line = []
            line = row.find_elements(By.TAG_NAME, "td")
            for r in line:
                stat_line.append(r.text)
            
            #print first name for each page just to check if it's working
            if i == 0:
                print(stat_line[1])
            player_stats.append(stat_line)
            
        
        #click next page button
        button = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[5]/button[2]")
        button.click()
        
    #close browser window 
    driver.close()
    
    #if the first column is an index, the column is excluded
    if player_stats[1][0] == '1':
        ind = 1
    else:
        ind=0

    #turn into a dataframe and save it
    n = len(np.array(player_stats)[ind, :]) 
    df = pd.DataFrame(np.array(player_stats)[:, ind:], columns=head_values[ind:n])
    df.drop_duplicates(inplace=True)
    df.to_pickle(f"./NBA_Tables/{stattype[cnt]}_stats.pkl")
