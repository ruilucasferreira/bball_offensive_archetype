#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 14:37:49 2025

@author: rl
"""

import numpy as np
import pandas as pd

stat_names = np.loadtxt("./stats_names.csv", delimiter=',', dtype=str)

def process_df(df, info=True):
    #make the player name be the index
    df.index = df.PLAYER
    if "index" in df.columns:
        df.drop(columns=["index", "PLAYER"], inplace=True)
    else:
        df.drop(columns=["PLAYER"], inplace=True)
    
    #remove information that typically is represented in every table
    if not info:
        for col in ["GP", "W", "L", "MIN", "AGE", "TEAM", " "]:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
          
    #format column names to remove spaces
    df.columns = df.columns = df.columns.str.replace('\n', '_')
    df.columns = df.columns = df.columns.str.replace(' ', '_')
    
    #stats without value
    df.replace({'-': np.nan}, inplace=True)
    
    #make every column numeric
    for col in df.columns:
        if col not in ["TEAM"]:
            df[col] = pd.to_numeric(df[col])

    return df

#Get biological information
stat_name = "bio"
bios = pd.read_pickle(f"./NBA_Tables/{stat_name}_stats.pkl")
bios.index = bios.PLAYER
bios = bios[["WEIGHT", "HEIGHT", "DRAFT YEAR", "DRAFT NUMBER"]]
bios.WEIGHT = round(pd.to_numeric(bios.WEIGHT) * 0.4536, 1)
bios.HEIGHT = [round(int(s[0])*30.48 + int(s[2:])*2.54) for s in bios.HEIGHT.array]

#General statistics
stat_type = "general"
inds = np.where(stat_names[:, 0] == stat_type)[0]

info = pd.read_pickle(f"./NBA_Tables/traditional_stats.pkl")[["GP", "W", "L", "MIN", "AGE", "TEAM"]]
for ind in inds:
    df = process_df(pd.read_pickle(f"./NBA_Tables/{stat_names[ind, 1]}_stats.pkl"),
                    info = False)
    if stat_names[ind, 1] == "advanced" or stat_names[ind, 1] == "estimated-advanced":
        df.columns = [s+stat_names[ind,2] for s in df.columns]
    else:
        df.columns = ["TOTAL_"+s+stat_names[ind,2] if ("%" not in s and "AVG" not in s) else s+stat_names[ind,2] for s in df.columns]
    if ind == inds[0]:
        TRAD = info.join(df)
    else:
        TRAD = TRAD.join(df)



#Playtype Synergy data    
stat_type = "playtype"
inds = np.where(stat_names[:, 0] == stat_type)[0]

for ind in inds:
    pt = process_df(pd.read_pickle(f"./NBA_Tables/{stat_names[ind, 1]}_stats.pkl"),
                           info=False)
    pt.drop(columns=["PPP", "FREQ%", 'FG%', 'EFG%', 'FT_FREQ%',
                            'TOV_FREQ%', 'SF_FREQ%', 'AND_ONE_FREQ%', 
                            'SCORE_FREQ%', 'PERCENTILE'], inplace=True)
    pt = pt.groupby("PLAYER").sum()        
    pt.columns = ["TOTAL_"+s+stat_names[ind,2] if ("%" not in s and "AVG" not in s) else s+stat_names[ind,2] for s in pt.columns]
    if ind == inds[0]:
        PT = pt.copy()
    else:
        PT = PT.join(pt, how="outer")
        
        
#Tracking data    
stat_type = "tracking"
inds = np.where(stat_names[:, 0] == stat_type)[0]

for ind in inds:
    tk = process_df(pd.read_pickle(f"./NBA_Tables/{stat_names[ind, 1]}_stats.pkl"),
                           info=False) 
    if stat_names[ind, 1] == "pullup" or stat_names[ind, 1] == "catch-shoot":
        tk['2PA'] = tk.FGA - tk['3PA']
        tk['2PM'] = tk.FGM - tk['3PM']
        tk['2P%'] = 100 * tk['2PM'] / tk['2PA'] 
    if stat_names[ind, 1] == "passing":
        v = tk.columns.array
        v[6] = "AST_ADJ"
        v[7] = "AST_TO_PASS%"
        v[8] = "AST_TO_PASS%_ADJ"
        tk.columns = ["TOTAL_"+s if ("%" not in s and "AVG" not in s) else s for s in v]
    else:
        tk.columns = ["TOTAL_"+s+stat_names[ind,2] if ("%" not in s and "AVG" not in s) else s+stat_names[ind,2] for s in tk.columns]
    if ind == inds[0]:
        TK = tk.copy()
    else:
        TK = TK.join(tk, how="outer")


#categories with a single stat        
        
stat_name = "hustle"
hustle = process_df(pd.read_pickle(f"./NBA_Tables/{stat_name}_stats.pkl"), 
                  info=False)
hustle.columns = ["TOTAL_"+s if ("%" not in s and "AVG" not in s) else s for s in hustle.columns]


stat_name = "box-outs"
bo = process_df(pd.read_pickle(f"./NBA_Tables/{stat_name}_stats.pkl"), 
                  info=False)
bo.columns = ["TOTAL_"+s if ("%" not in s and "AVG" not in s) else s for s in bo.columns]


stat_name = "shooting"
shoot = pd.read_pickle(f"./NBA_Tables/{stat_name}_stats.pkl")
shoot.columns = np.array(["PLAYER", "TEAM", "AGE",
                          "FGM_RA", "FGA_RA", "FG%_RA", 
                          "FGM_PAINT_NONRA", "FGA_PAINT_NONRA", "FG%_PAINT_NONRA",
                          "FGM_MID", "FGA_MID", "FG%_MID",
                          "FGM_LCORNER3", "FGA_LCORNER3", "FG%_LCORNER3",
                          "FGM_RCORNER3", "FGA_RCORNER3", "FG%_RCORNER3",
                          "FGM_CORNER3", "FGA_CORNER3", "FG%_CORNER3",
                          "FGM_ATB3", "FGA_ATB3", "FG%_ATB3"])
shoot = process_df(shoot, info=False)
shoot.columns = ["TOTAL_"+s if ("%" not in s and "AVG" not in s) else s for s in shoot.columns]

#connect into a single df
STATS = pd.concat([bios, TRAD, PT, TK, hustle, bo, shoot],
                  axis=1)

STATS.to_pickle(f"./full_stats.pkl")
