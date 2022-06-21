# Sports-Ref-Time-Travel-Sim

DATA COURTESY OF SPORTS-REFERENCE

SIMULATOR:

Who was more dominant, the 1975 Cincinnati Reds or the 1927 Yankees? Debates like this can now be settled through simulation analysis. The simulator is based on plate appearance probabilities, you can either strikeout, walk, get a hit, or hit the ball in play but get out (in play out). When you enter in your two teams into the program, the web-crawler searches baseball reference for those two teams. Once it is able to get the data from those team pages, I convert the data into probabilities that add up to one for each player, on a plate appearance basis. Then when it's time to face off, in the plate apearance function for example, the probability of the hitter striking out is the probability of the pitcher striking someone out, plus the probability of the hitter striking out. This is the same for all events, and it adds up to 2, so if the hitter rarely strikes out (say 6% of the time) but the pitcher is a strikout pitcher (say 30% K rate), the probability of a strikout in this plate appearance is (.36 / 2) which is 18% for example. 

You can also choose to opt out of the auto lineup function and set your own lineup and rotation for both teams.

DISCLAIMERS:

* If there is a runner on 2nd base and the batter hits a single, the runner will always score (working on base running probability)
* If there is a runner on 1st and the batter hits into an in play out, there is no double play (working on double play probability)
* The starting pitcher always goes all 9 innings in each game (working on cycling through relievers after the 6th inning of games)
* The automatic lineup function sorts all hitters by total bases and uses the top 9 for the lineup 
* The automatic rotation funciton sorts all starting pitchers by innings pitched and uses the top 10 to hopefully include a couple relievers
* working on incorperating righty / lefty, home / away splits
* Currently only works on Japanese league teams, the MLB, and summer baseball leagues (working on minors and college)

LINEUP OPTIMIZATION:

The lineup optimizer function allows you to try every possible variation of a starting 9 against a specific pitcher and will spit out the top 5 lineups sorted by runs scored per game off of that pitcher.

SITUATIONAL ANALYSIS:

The goal with this function of the sumulator is to be able to simulate as many games as you want, all starting in a certain situation and seeing what the most likley results are. Another goal of it is to be able to simulate an equal amount of games with different pitchers and see which pitcher is most likley to get you out of a jam.


# Current Stage

I am currently finished with the principles of the baseball simulator, although later on I would like to work in stolen bases, and reaching on error probability into it. For now I am working on finishing up the lineup optimizer so that for the MLB it will use righty lefty splits, to more accuratley spit out the best lineup possible. This will be an MLB only feature as that data is not as easily availabe for other leagues. The righty lefty splits should be in the simulator as well and not just the lineup optimizer so that will be cool. Then I will crank out the situational analysis option.

Once I finish baseball and do everything I have been thinking of, I would like to move on to doing other sports that are on Sports-Reference like football, basketball, futbol, college football and basketball, and hockey.
