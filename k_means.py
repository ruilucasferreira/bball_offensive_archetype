#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 19:32:52 2025

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
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


n = 4
m = 8
stats = pd.read_pickle("./full_stats.pkl")
old_feats = np.array(np.loadtxt("./features.csv", delimiter=',', dtype=str))[:,0]
feats = np.array(np.loadtxt("./features.csv", delimiter=',', dtype=str))[:,1]

#Only use players with a total of 720 minutes
stats = stats[stats.MIN > 720]


data = stats[old_feats]
data.columns = feats
data = data.fillna(0)


for c in feats:
    if "TOTAL" in c and c != "TOTAL_MIN":
        data[c] = 36 * data[c].values / data.MIN.values

data.drop(columns=["MIN"], inplace=True)        
data.columns = data.columns.str.replace('TOTAL', 'PER36')

Z = (data - data.mean()) / (data.std())

kmeans_kwargs = {
    "init": "random",
    "n_init": 10,
    "random_state": 1,
    }

#create list to hold SSE values for each k
sse = []
sil = []
for k in range(2, 40):
    kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
    kmeans.fit(Z)
    sse.append(kmeans.inertia_)
    sil.append(silhouette_score(Z, kmeans.fit_predict(Z)))
    
#visualize results
fig=plt.figure()
ax=fig.add_subplot(111, label="1")
ax2=fig.add_subplot(111, label="2", frame_on=False)

ax.plot(np.arange(2, 40), sse, color="C0")
ax.set_xlabel("Number of Clusters", color="black")
ax.set_ylabel("SSE", color="C0")
ax.tick_params(axis='x', colors="C0")
ax.tick_params(axis='y', colors="C0")

ax2.plot(np.arange(2, 40), sil, color="C1")
ax2.yaxis.tick_right()
ax2.set_ylabel('SS', color="C1")       
ax2.yaxis.set_label_position('right') 
ax2.tick_params(axis='y', colors="C1")

plt.title("Elbow plot", fontsize=30)
ax.vlines([4, 8], 3000, 12000, "gray", alpha=0.5)
plt.show()

kmeans4 = KMeans(init="random", n_clusters=n, n_init=10, random_state=1)
kmeans4.fit(Z)
centers4 = kmeans4.cluster_centers_
renorm_centers4 = np.array([( c*data.std() )+data.mean() for c in centers4])

kmeans8 = KMeans(init="random", n_clusters=m, n_init=10, random_state=1)
kmeans8.fit(Z)
centers8 = kmeans8.cluster_centers_
renorm_centers8 = np.array([( c*data.std() )+data.mean() for c in centers8])

data['CLUSTER4'] = kmeans4.labels_
stats["CLUSTER4"] = data.CLUSTER4

data['CLUSTER8'] = kmeans8.labels_
stats["CLUSTER8"] = data.CLUSTER8

colors = ['black', "gray", "silver", "red", 
          "blue", "yellow", "aquamarine", "maroon"]


types4 = {0:"Off-ball Bigs", 1:"On-ball Bigs", 
         3:"Ball Handlers", 2:"Off-ball Scorers"}
stats["ARCHETYPE4"] = (stats.CLUSTER4).replace(types4)

types8 = {0: "Pure Shooters", 1:"Scoring Guards", 
         2:"Handyman Wings", 3:"Corner Dwellers", 
         0:"Off-ball Bigs", 5:"Offensive Hub Bigs", 
         6:"Isoball Ballers", 7:"Primary Ball Handlers"}
stats["ARCHETYPE8"] = (stats.CLUSTER8).replace(types8)


stats["OFFRTG_DIFF"] = stats.OFFRTG_ADV - np.mean(stats.OFFRTG_ADV)



sns.boxplot(data=stats, y="OFFRTG_DIFF", x="ARCHETYPE4")
sns.swarmplot(data=stats, y="OFFRTG_DIFF", x="ARCHETYPE4",
              size=4, edgecolor='black', linewidth=1)
plt.xticks(rotation=45, ha='right')
plt.ylabel("Offensive Rating against NBA average")
plt.xlabel("")
plt.show()

sns.boxplot(data=stats, y="OFFRTG_DIFF", x="ARCHETYPE8")
sns.swarmplot(data=stats, y="OFFRTG_DIFF", x="ARCHETYPE8",
              size=4, edgecolor='black', linewidth=1)
plt.xticks(rotation=45, ha='right')
plt.ylabel("Offensive Rating against NBA average")
plt.xlabel("")
plt.show()

#diffs = np.round( 100 * ( centers - Z.mean().values ) / Z.mean().values )

def diff_plot(j, n_clusters=4):
    if n_clusters == 4:
        diff = centers4[j]
        t = types4[j]
    else:
        diff = centers8[j]
        t = types8[j]
    inds = np.argsort( diff )[::-1]
    plt.figure(figsize=(25, 12))
    plt.bar(Z.columns[inds], diff[inds])
    plt.xticks(rotation=80, ha='right')
    plt.title(f"{t} Difference Stats",
              fontsize=30)
    plt.ylabel("Difference to league average")
    plt.show()
    
def examples(j, num=3, n_clusters=4):
    if n_clusters == 4:
        centers = centers4.copy()
        clus = "CLUSTER"+str(n_clusters)
    else:
        centers = centers8.copy()
        clus = "CLUSTER"+str(n_clusters)
        
    three_closest_in = Z[data[clus]==j].iloc[ np.argsort( ((Z[data[clus]==j] - centers[j])**2).mean(axis=1) ) ].index
    values = np.sort( ((Z[data[clus]==j] - centers[j])**2).mean(axis=1) )[:num]
    print("Closest to Cluster Average (Players in Cluster):")
    for i, p in enumerate( three_closest_in[:num] ): 
        print(f"{i+1}º - {p} ({values[i]:.3f})")
    print("\n")
    
    three_farthest_in = Z[data[clus]==j].iloc[ np.argsort( ((Z[data[clus]==j] - centers[j])**2).mean(axis=1) ) ].index
    values = np.sort( ((Z[data[clus]==j] - centers[j])**2).mean(axis=1) )[-num:]
    print("Farthest to Cluster Average (Players in Cluster):")
    for i, p in enumerate( three_farthest_in[-num:] ): 
        print(f"{num-i}º - {p} ({values[i]:.3f})")
    print("\n")
    
    three_closest_out = Z[data[clus]!=j].iloc[ np.argsort( ((Z[data[clus]!=j] - centers[j])**2).mean(axis=1) ) ].index
    values = np.sort( ((Z[data[clus]!=j] - centers[j])**2).mean(axis=1) )[:num]
    print("Closest to Cluster Average (Players outside Cluster):")
    for i, p in enumerate( three_closest_out[:num] ): 
        print(f"{i+1}º - {p} ({values[i]:.3f})")
    print("\n")
    
    three_farthest_out = Z[data[clus]!=j].iloc[ np.argsort( ((Z[data[clus]!=j] - centers[j])**2).mean(axis=1) ) ].index
    values = np.sort( ((Z[data[clus]!=j] - centers[j])**2).mean(axis=1) )[-num:]
    print("Farthest to Cluster Average (Players out Cluster):")
    for i, p in enumerate( three_farthest_out[-num:] ): 
        print(f"{num-i}º - {p} ({values[i]:.3f})")
    
    
stats[["CLUSTER4", "CLUSTER8"]].to_pickle("./kcluster_labels.pkl")
    
stats.to_excel("./stats_with_kcluster.xlsx")