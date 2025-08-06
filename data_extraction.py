#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 19:36:02 2025

@author: rl
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

#chrome_options = Options()
#chrome_options.add_argument("--headless")

stattype = np.loadtxt("./stats_names.csv", delimiter=',', dtype=str)[len(os.listdir("./NBA_Tables")):]

for cnt in range(len(stattype)):

    service = Service(executable_path="/usr/local/bin/chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service=service)
    

    driver.get(f"https://www.nba.com/stats/players/{stattype[cnt]}?SeasonType=Regular+Season&PerMode=Totals&TypeGrouping=offensive")
    
    sleep(1)
    
    head = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table/thead")
    
    #"/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button[2]"
    
    heads = head.find_elements(By.TAG_NAME, "th")
    
    num = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[1]")
    
    num = int(num.text[:-5])
    
    head_values = []
    for h in heads:
        head_values.append(h.text)
        
    temp = 0
    player_stats = []
    
    while temp < num:
        sleep(0.25+np.random.rand()/2)
        if temp == 0:
            
            if len(driver.find_elements(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')) != 0:
        
                sleep(2)
    
                cookie = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
                cookie.click()
                sleep(2)
                driver.refresh()
                sleep(2)
                
            if len(driver.find_elements(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button[2]')) != 0:
                consent = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button[2]')
                consent.click()
                sleep(0.5)
                double_consent = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/div[3]/div[2]/button[2]")
                double_consent.click()
                sleep(0.5)
            
        body = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table/tbody")
        rows = body.find_elements(By.TAG_NAME, "tr")
        
        for i, row in enumerate(rows):
            if i==50 or temp == num:
                break
            temp = temp + 1
            stat_line = []
            line = row.find_elements(By.TAG_NAME, "td")
            for r in line:
                stat_line.append(r.text)
            if i == 0:
                print(stat_line[1])
            player_stats.append(stat_line)
            
        #temp = int(player_stats[-1][0])
        
        button = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[5]/button[2]")
        
        sleep(0.25+np.random.rand()/2)
        
        button.click()
        
    driver.close()
    
    if player_stats[1][0] == '1':
        ind = 1
    else:
        ind=0
    n = len(np.array(player_stats)[ind, :])
    
    df = pd.DataFrame(np.array(player_stats)[:, ind:], columns=head_values[ind:n])
    
    df.drop_duplicates(inplace=True)
    
    df.to_pickle(f"./NBA_Tables/{stattype[cnt]}_stats.pkl")
