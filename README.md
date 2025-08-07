# Offensive Archetypes in the NBA: A cluster-based search

## General Goal

The traditional basketball positions have long  been insufficient to properly characterize the roles of players in modern NBA offenses. 
Some have opted to reduce the number of categories from the five to only three (bigs, wings and guards), while others have developed new categories based on statistics and film analyisis of the game 
(famously, Todd Whitehead [identified 11 offensive roles](https://fansided.com/2019/05/29/nylon-calculus-grouping-players-offensive-role-again/) based on NBA and Synergy data). 

In this work, I seek to follow in the same steps as Todd, starting from a simple clustering method (and what is simpler than K-Means) and evenetually understand the data better and better, building more adequate, insightful models.


## Web Scrapping and Data Processing

The data used in this work is available for free in the NBA website. The data was scrapped using Python and [Selenium](https://www.selenium.dev/). 
All data is referent to the Regular Season (RS) and by Totals. 
The playoffs, All-Star game and pre-season were excluded since they typically provide different intensity leves that may conflict with the RS basketball. 
The choice for the RS instead of the playoffs is one of convenience, since there are much more data for the former, by obvious reasons.

The data was treated (using [Numpy](https://numpy.org/) and [Pandas](https://pandas.pydata.org/)) into a single dataframe, with rows representing single players (the samples) and columns representing stats (the features).

Only offensive-related stats - shot-making, passing, handling, screening and offensive hustle - were included in the dataset.
