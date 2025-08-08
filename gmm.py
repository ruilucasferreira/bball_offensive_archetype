#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 00:05:28 2025

@author: rl
"""

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
plt.rcParams["figure.figsize"] = (20,12)
plt.rcParams["xtick.labelsize"] = 16
plt.rcParams["ytick.labelsize"] = 16

plt.rcParams["axes.labelsize"] = 20

import seaborn as sns

import pandas as pd

from sklearn.mixture import GaussianMixture

n = 4
m = 8
stats = pd.read_pickle("./full_dataset.pkl")

stats = stats.loc[:,~stats.columns.duplicated()].copy()
stats.loc["Jaylen Wells", "WEIGHT"] = 93

stats = stats[stats.TOTAL_MIN > 720]

cols = np.array(stats.columns)

feats = np.array(["WEIGHT", "HEIGHT", "TOTAL_MIN", "USG%",
                  "TOTAL_OREB_CHANCES", "CONTESTED_OREB%", #"OREB_CHANCE%", 
                  "TOTAL_AVG_OREB_DISTANCE", "TOTAL_DEFERRED_OREB_CHANCES",
                  "TOTAL_2PA_PULLUP", "TOTAL_3PA_PULLUP", 
                  "TOTAL_2PA_C&S", "TOTAL_3PA_C&S", 
                  "TOTAL_PASSES_MADE", "TOTAL_PASSES_RECEIVED", 
                  "TOTAL_POTENTIAL_AST", #"TOTAL_SECONDARY_AST",
                  "PER36_SCREEN_ASSISTS", "PER36_OFF_LOOSE_BALLS_RECOVERED",
                  "PER36_CONTESTED_2PT_SHOTS", "PER36_CONTESTED_3PT_SHOTS",
                  "TOTAL_DIST._MILES_OFF", "AVG_SPEED_OFF", 
                  "TOTAL_FRONT_CT_TOUCHES", "AVG_SEC_PER_TOUCH", "AVG_DRIB_PER_TOUCH",
                  "TOTAL_TOUCHES", "TOTAL_ELBOW_TOUCHES", "TOTAL_FGA_ELBOW",
                  "TOTAL_PASS_ELBOW", # "TOTAL_TO_ELBOW", "TOTAL_PF_ELBOW",
                  "TOTAL_PAINT_TOUCHES", "TOTAL_FGA_PAINT",
                  "TOTAL_PASS_PAINT", #"TOTAL_TO_PAINT", "TOTAL_PF_PAINT",
                  "TOTAL_DRIVES", "TOTAL_FGA_DRIVES",
                  "TOTAL_PASS_DRIVES", #"TOTAL_TO_DRIVES", "TOTAL_PF_DRIVES",
                  "TOTAL_POST_UPS", "TOTAL_FGA_POSTUP",
                  "TOTAL_PASS_POSTUP", #"TOTAL_TO_POSTUP", "TOTAL_PF_POSTUP",
                  "TOTAL_FGA_RA", "TOTAL_FGA_PAINT_NONRA", "TOTAL_FGA_MID", 
                  "TOTAL_FGA_CORNER3", "TOTAL_FGA_ATB3",
                  "TOTAL_POSS_ISOLATION", "TOTAL_FGA_ISOLATION",
                  "TOTAL_POSS_TRANSITION", "TOTAL_FGA_TRANSITION",
                  "TOTAL_POSS_BALL-HANDLER", "TOTAL_FGA_BALL-HANDLER",
                  "TOTAL_POSS_ROLL-MAN", "TOTAL_FGA_ROLL-MAN",
                  "TOTAL_POSS_PLAYTYPE-POST-UP", "TOTAL_FGA_PLAYTYPE-POST-UP",
                  "TOTAL_POSS_SPOT-UP", "TOTAL_FGA_SPOT-UP",
                  "TOTAL_POSS_HAND-OFF", "TOTAL_FGA_HAND-OFF",
                  "TOTAL_POSS_CUT", "TOTAL_FGA_CUT",
                  "TOTAL_POSS_OFF-SCREEN", "TOTAL_FGA_OFF-SCREEN",
                  "TOTAL_POSS_PUTBACKS", "TOTAL_FGA_PUTBACKS",
                  "TOTAL_POSS_PLAYTYPE-MISC", "TOTAL_FGA_PLAYTYPE-MISC"
                  ])


data = stats[feats]
data = data.fillna(0)
data.columns = data.columns.str.replace('TOTAL_MIN', 'MIN')


for c in feats:
    if "TOTAL" in c and c != "TOTAL_MIN":
        data[c] = 36 * data[c].values / data.MIN.values

data.drop(columns=["MIN"], inplace=True)        
data.columns = data.columns.str.replace('TOTAL', 'PER36')

Z = (data - data.mean()) / (data.std())

aic = []
bic = []
for k in range(1, 40):
    gm = GaussianMixture(n_components=k, 
                         random_state=0,
                         ).fit(Z)
    bic.append(gm.bic(Z))
    aic.append(gm.aic(Z))

bic = np.array(bic)
aic = np.array(aic)
fig=plt.figure()
ax=fig.add_subplot(111, label="1")
ax2=fig.add_subplot(111, label="2", frame_on=False)

ax.plot(np.arange(1, 40), aic, color="C0")
ax.set_xlabel("Number of Clusters", color="black")
ax.set_ylabel("AIC", color="C0")
ax.tick_params(axis='x', colors="C0")
ax.tick_params(axis='y', colors="C0")

ax2.plot(np.arange(1, 40), bic, color="C1")
ax2.yaxis.tick_right()
ax2.set_ylabel('BIC', color="C1")       
ax2.yaxis.set_label_position('right') 
ax2.tick_params(axis='y', colors="C1")

plt.title("Elbow plot", fontsize=30)
ax.vlines([4, 8], 3000, 12000, "gray", alpha=0.5)
plt.show()

k = 14
gm = GaussianMixture(n_components=k, 
                     random_state=0,
                     ).fit(Z)

data['CLUSTER'] = gm.predict(Z)
stats["CLUSTER"] = data.CLUSTER

