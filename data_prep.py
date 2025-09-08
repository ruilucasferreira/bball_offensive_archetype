#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 14:37:49 2025

@author: rl
"""

import numpy as np
import pandas as pd
import os

writer = pd.ExcelWriter('./stats.xlsx', 
                        mode="w",
                        engine='openpyxl')

seasons = os.listdir("./NBA_Tables/")

stat_names = np.loadtxt("./stats_names.csv", delimiter=',', dtype=str)

def process_df(df, info=True):
    #make the player name be the index
    df.index = [df.PLAYER, df.SEASON]
    #df = df[df.MIN >= 720]
    if "index" in df.columns:
        df.drop(columns=["index", "PLAYER", "SEASON"], inplace=True)
    else:
        df.drop(columns=["PLAYER", "SEASON"], inplace=True)
    
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

def total_to_per36(df, info):
    indexes = [df.index[i][0] for i in range(len(df))]
    for c in df.columns:
        if "TOTAL" in c:
            df[c] = 36*df[c]/info.loc[indexes].MIN
    
    df.columns = df.columns.str.replace('TOTAL', 'PER36')

    return df

#Get biological information
stat_name = "bio"
for s in seasons:
    bios = pd.read_pickle(f"./NBA_Tables/{s}/{stat_name}_stats.pkl")
    #bios.index = bios.PLAYER
    bios = bios[["PLAYER", "WEIGHT", "HEIGHT", "DRAFT YEAR", "DRAFT NUMBER"]]
    bios.WEIGHT = round(pd.to_numeric(bios.WEIGHT) * 0.4536, 1)
    bios.HEIGHT = [round(int(s[0])*30.48 + int(s[2:])*2.54) for s in bios.HEIGHT.array]
    #bios["SEASON"] = s
    if s == seasons[0]:
        all_bios = bios.copy()
    else:
        all_bios = pd.concat([all_bios, bios], axis=0) 
all_bios.drop_duplicates(subset=["PLAYER"], keep="last", inplace=True)
all_bios.index = all_bios.PLAYER
all_bios.drop(columns=["PLAYER"], inplace=True)
all_bios.loc["Jaylen Wells", "WEIGHT"] = 93
all_bios.to_excel(writer, sheet_name=f"{stat_name}", engine='openpyxl')

#General statistics
stat_type = "general"
inds = np.where(stat_names[:, 0] == stat_type)[0]

for s in seasons:
    info = pd.read_pickle(f"./NBA_Tables/{s}/traditional_stats.pkl").loc[:, ["PLAYER", "GP", "W", "L", "MIN", "AGE", "TEAM"]]
    info["SEASON"] = s
    info = process_df(info)
    if s == seasons[0]:
        all_info = info.copy()
    else:
        all_info = pd.concat([all_info, info], axis=0)

for ind in inds:
    for s in seasons:
        df = pd.read_pickle(f"./NBA_Tables/{s}/{stat_names[ind, 1]}_stats.pkl")
        df["SEASON"] = s
        df = process_df(df, info = False)
        if stat_names[ind, 1] == "advanced" or stat_names[ind, 1] == "estimated-advanced":
            df.columns = [s+stat_names[ind,2] for s in df.columns]
        else:
            df.columns = ["TOTAL_"+s+stat_names[ind,2] if ("%" not in s and "AVG" not in s) else s+stat_names[ind,2] for s in df.columns]
        df = total_to_per36(df, all_info)
        if s == seasons[0]:
            all_df = df.copy()
        else:
            all_df = pd.concat([all_df, df], axis=0)
    all_df.to_excel(writer, sheet_name=f"{stat_names[ind, 1]}", engine='openpyxl')



#Playtype Synergy data    
stat_type = "playtype"
inds = np.where(stat_names[:, 0] == stat_type)[0]

for ind in inds:
    for s in seasons:
        pt = pd.read_pickle(f"./NBA_Tables/{s}/{stat_names[ind, 1]}_stats.pkl")
        pt["SEASON"] = s 
        pt = process_df(pt, info=False)
        for c in ['FT_FREQ%', 'TOV_FREQ%', 'SF_FREQ%', 'AND_ONE_FREQ%']:
            pt[c[:-6]] = round(pt[c] * pt.POSS)
        pt.drop(columns=["PPP", "FREQ%", 'FG%', 'EFG%', 'FT_FREQ%',
                        'TOV_FREQ%', 'SF_FREQ%', 'AND_ONE_FREQ%', 
                        'SCORE_FREQ%', 'PERCENTILE'],
                inplace=True)
        pt = pt.groupby(["PLAYER", "SEASON"]).sum()        
        pt.columns = ["TOTAL_"+s+stat_names[ind,2] if ("%" not in s and "AVG" not in s) else s+stat_names[ind,2] for s in pt.columns]
        pt = total_to_per36(pt, all_info)
        if s == seasons[0]:
            all_pt = pt.copy()
        else:
            all_pt = pd.concat([all_pt, pt], axis=0)          
    all_pt.to_excel(writer, sheet_name=f"{stat_names[ind, 1]}", engine='openpyxl')
        
        
#Tracking data    
stat_type = "tracking"
inds = np.where(stat_names[:, 0] == stat_type)[0]

for ind in inds:
    for s in seasons:
        tk = pd.read_pickle(f"./NBA_Tables/{s}/{stat_names[ind, 1]}_stats.pkl")
        tk["SEASON"] = s
        tk = process_df(tk, info=False) 
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
        tk = total_to_per36(tk, all_info)
        if s == seasons[0]:
            all_tk = tk.copy()
        else:
            all_tk = pd.concat([all_tk, tk], axis=0)
    all_tk.to_excel(writer, sheet_name=f"{stat_names[ind, 1]}", engine='openpyxl')


#categories with a single stat        
        
stat_name = "hustle"
for s in seasons:
    hustle = pd.read_pickle(f"./NBA_Tables/{s}/{stat_name}_stats.pkl")
    hustle["SEASON"] = s
    hustle = process_df(hustle, info=False)
    hustle.columns = ["TOTAL_"+s if ("%" not in s and "AVG" not in s) else s for s in hustle.columns]
    hustle = total_to_per36(hustle, all_info)
    if s == seasons[0]:
        all_hustle = hustle.copy()
    else:
        all_hustle = pd.concat([all_hustle, hustle], axis=0) 
all_hustle.to_excel(writer, sheet_name=f"{stat_name}", engine='openpyxl')

stat_name = "box-outs"
for s in seasons:
    bo = pd.read_pickle(f"./NBA_Tables/{s}/{stat_name}_stats.pkl")
    bo["SEASON"] = s
    bo = process_df(bo, info=False)
    bo.columns = ["TOTAL_"+s if ("%" not in s and "AVG" not in s) else s for s in bo.columns]
    bo = total_to_per36(bo, all_info)
    if s == seasons[0]:
        all_bo = bo.copy()
    else:
        all_bo = pd.concat([all_bo, bo], axis=0) 
all_bo.to_excel(writer, sheet_name=f"{stat_name}", engine='openpyxl')

stat_name = "shooting"
for s in seasons:
    shoot = pd.read_pickle(f"./NBA_Tables/{s}/{stat_name}_stats.pkl")
    shoot.columns = np.array(["PLAYER", "TEAM", "AGE",
                            "FGM_RA", "FGA_RA", "FG%_RA", 
                            "FGM_PAINT_NONRA", "FGA_PAINT_NONRA", "FG%_PAINT_NONRA",
                            "FGM_MID", "FGA_MID", "FG%_MID",
                            "FGM_LCORNER3", "FGA_LCORNER3", "FG%_LCORNER3",
                            "FGM_RCORNER3", "FGA_RCORNER3", "FG%_RCORNER3",
                            "FGM_CORNER3", "FGA_CORNER3", "FG%_CORNER3",
                            "FGM_ATB3", "FGA_ATB3", "FG%_ATB3"])
    shoot["SEASON"] = s
    shoot = process_df(shoot, info=False)
    shoot.columns = ["TOTAL_"+s if ("%" not in s and "AVG" not in s) else s for s in shoot.columns]
    shoot = total_to_per36(shoot, all_info)
    if s == seasons[0]:
        all_shoot = shoot.copy()
    else:
        all_shoot = pd.concat([all_shoot, shoot], axis=0)
all_shoot.to_excel(writer, sheet_name=f"{stat_name}", engine='openpyxl')

writer.close()
