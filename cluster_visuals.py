import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
plt.rcParams["figure.figsize"] = (8, 4.8)
plt.rcParams["xtick.labelsize"] = 8
plt.rcParams["ytick.labelsize"] = 8
plt.rcParams["axes.labelsize"] = 10


def examples(Z, j, centers, num=3, n_clusters=4):
    clus = "CLUSTER"+str(n_clusters)
        
    three_closest_in = Z[data[clus]==j].iloc[ np.argsort( ((Z[data[clus]==j] - centers[j])**2).mean(axis=1) ) ].index
    values = np.sort( ((Z[data[clus]==j] - centers[j])**2).mean(axis=1) )[:num]
    print("Closest to Cluster Average (Players in Cluster):")
    for i, p in enumerate( three_closest_in[:num] ): 
        print(f"{i+1}º - {p} - {values[i]:.3f}")
    print("\n")
    
    three_farthest_in = Z[data[clus]==j].iloc[ np.argsort( ((Z[data[clus]==j] - centers[j])**2).mean(axis=1) ) ].index
    values = np.sort( ((Z[data[clus]==j] - centers[j])**2).mean(axis=1) )[-num:]
    print("Farthest to Cluster Average (Players in Cluster):")
    for i, p in enumerate( three_farthest_in[-num:] ): 
        print(f"{num-i}º - {p} - {values[i]:.3f}")
    print("\n")
    
    three_closest_out = Z[data[clus]!=j].iloc[ np.argsort( ((Z[data[clus]!=j] - centers[j])**2).mean(axis=1) ) ].index
    values = np.sort( ((Z[data[clus]!=j] - centers[j])**2).mean(axis=1) )[:num]
    print("Closest to Cluster Average (Players outside Cluster):")
    for i, p in enumerate( three_closest_out[:num] ): 
        print(f"{i+1}º - {p} - {values[i]:.3f}")
    print("\n")
    
    three_farthest_out = Z[data[clus]!=j].iloc[ np.argsort( ((Z[data[clus]!=j] - centers[j])**2).mean(axis=1) ) ].index
    values = np.sort( ((Z[data[clus]!=j] - centers[j])**2).mean(axis=1) )[-num:]
    print("Farthest to Cluster Average (Players out Cluster):")
    for i, p in enumerate( three_farthest_out[-num:] ): 
        print(f"{num-i}º - {p} - {values[i]:.3f}")

def diff_plot(cluster, centers):
    diff = centers[cluster]
    inds = np.argsort( diff )[::-1]
    plt.figure(figsize=(25, 12))
    plt.bar(Z.columns[inds], diff[inds])
    plt.xticks(rotation=80, ha='right')
    plt.title(f"Cluster {cluster} stat difference",
              fontsize=30)
    plt.ylabel("Difference to league average")
    plt.show()