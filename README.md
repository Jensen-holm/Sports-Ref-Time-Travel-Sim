# Sports-Ref-Time-Travel-Sim

(all data used is from the sports reference webpage. they are amazing)

SIMULATOR:

Who was more dominant, the 1975 Cincinnati Reds or the 1927 Yankees? Debates like this can now be settled through simulation analysis. The simulator is based on plate appearance probabilities, you can either strikeout, walk, get a hit, or hit the ball in play but get out (in play out). When you enter in your two teams into the program, the web-crawler searches baseball reference for those two teams. Once it is able to get the data from those team pages, I convert the data into probabilities that add up to one for each player, on a plate appearance basis. Then when it's time to face off, in the plate apearance function for example, the probability of the hitter striking out is the probability of the pitcher striking someone out, plus the probability of the hitter striking out. This is the same for all events, and it adds up to 2, so if the hitter rarely strikes out (say 6% of the time) but the pitcher is a strikout pitcher (say 30% K rate), the probability of a strikout in this plate appearance is (.36 / 2) which is 18% for example. 

You can also choose to opt out of the auto lineup function and set your own lineup and rotation for both teams.

DISCLAIMERS:

* If there is a runner on 2nd base and the batter hits a single, the runner will always score (working on base running probability)
* If there is a runner on 1st and the batter hits into an in play out, there is no double play (working on double play probability)
* The starting pitcher always goes all 9 innings in each game (working on cycling through relievers after the 6th inning or so of games)
* The automatic lineup function sorts all hitters by total bases and uses the top 9 for the lineup 
* The automatic rotation funciton sorts all starting pitchers by innings pitched and uses the top 10 to hopefully include a couple relievers
* working on incorperating righty / lefty, home / away splits
* Currently only works on Japanese league teams, the MLB, and summer baseball leagues (working on minors and college)
* Results of a plate appearance are based on overall season numbers, I am currently working on it to incorperate righty lefty splits and potentially other split statistics as well to have more 'authentic' probabilities for each plate appearance.

LINEUP OPTIMIZATION:

The lineup optimizer function allows you to try every possible variation of a starting 9 against a specific pitcher and will spit out the top 10 lineups sorted by runs scored per game off of that pitcher (this function ususally takes a while, I would reccommend 100 sims per lineup).

SITUATIONAL ANALYSIS:

The goal with this function of the sumulator is to be able to simulate as many games as you want, all starting in a certain situation and seeing what the most likley results are. Another goal of it is to be able to simulate an equal amount of games with different pitchers and see which pitcher is most likley to get you out of a jam.

# Current Stage

The basic simulator is complete, it simulates as many games as you would like between two teams. but currently the stats that the probabilities are calculated off of a players total or current season statistics. I believe the simulator would be better if I were to base the probabilities off of split statistics, like righty/lefty, and home/away, anything you could think of to make it just that much more like real baseball. So that is what I am currently working on. However most of those features will only be availabe if you are doing an MLB simulation due to lack of data on other leagues.

Once I finish baseball and do everything I have been thinking of, I would like to move on to doing other sports that are on Sports-Reference like football, basketball, futbol, college football and basketball, and hockey.
