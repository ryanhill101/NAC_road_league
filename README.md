# NAC_road_league
Newbury Athletic Club road running league python script - gets results from powerof10, finds NAC athletes, and calculates various league tables


-reads list of events from a csv file named 'events.txt'. format: Date (format: 1st January 2020), race type, race name, location (**must match po10 as this is used by the script to find the event**), comments

-downloads results files for each event from po10 (races MUST be on po10 to be included).  the code will cache results it has previously found so that it's not hammering the po10 website.

-searches for NAC athletes in the results, classifies them as Male/Female and Senior/Veteran

-calculates position and points against other NAC athletes in same category.  certain race distances also qualifiable for PB bonus points (PBs are determined by po10 including PB next to the athlete in the results, so only measured against past po10 performances)

-generates the league tables to screen and to a PDF which can be uploaded to the website.

TO RUN
-have events.txt and NAC_RL.py in the same directory.  run "python NAC_RL.py"

TODO
-identify NAC athletes from a list of registered athletes provided by membership secretary
-calculate points total only using best 10 (or best n) races.  PB-qualifying races complicates this...
