import random

'''
TO DO:
    - handle un earned runs (reached on errors)
    - stolen bases and base running probabilities
    - extra innings runner on second rule
    - incorperate bullpens
'''

def clear_bases():
    return [None, None, None]

def PA(hitter, pitcher):
        # determine which pitcher probabilities to use
        if hitter.hand == 'L':
            probs_pit = pitcher.probsL
        elif hitter.hand == 'S':
            if pitcher.hand == 'L':
                probs_pit = pitcher.probsR
            else:
                probs_pit = pitcher.probsL
        else:
            probs_pit = pitcher.probsR
        # then for hitters
        if pitcher.hand == 'L': # left probs
            probs_hit = hitter.probsL
        # idk if there are actually that many switch pitchers out there but im prepared
        elif pitcher.hand == 'S': # opp probs
            if hitter.hand == 'L':
                probs_hit = hitter.probsL
            else:
                probs_hit = hitter.probsR
        else: # righty probs
            probs_hit = hitter.probsR
        # calculate probabilities

        kp = [x[1] for x in probs_hit if x[0] == 'K'][0] + [x[1] for x in probs_pit if x[0] == 'K'][0]
        bbp = [x[1] for x in probs_hit if x[0] == 'BB'][0] + [x[1] for x in probs_pit if x[0] == 'BB'][0]
        hbpp = [x[1] for x in probs_hit if x[0] == 'HBP'][0] + [x[1] for x in probs_pit if x[0] == 'HB'][0]
        hp = [x[1] for x in probs_hit if x[0] == 'H'][0] + [x[1] for x in probs_pit if x[0] == 'H'][0]
        ipop = [x[1] for x in probs_hit if x[0] == 'IPO'][0] + [x[1] for x in probs_pit if x[0] == 'IPO'][0]
        roep = [x[1] for x in probs_hit if x[0] == 'ROE'][0] # pitchers dont have roe probability, which is fine
        outcome = random.choices(['K', 'BB', 'HBP', 'H', 'IPO'], (kp, bbp, hbpp, hp, ipop)) # right now trying it without reached on error
        if outcome[0] == 'H':
            # find out what kind of hit (think this is a problem if the probabilities are 0)
            singlep = [x[1] for x in probs_hit if x[0] == '1B'][0] + [x[1] for x in probs_pit if x[0] == '1B'][0]
            doublep = [x[1] for x in probs_hit if x[0] == '2B'][0] + [x[1] for x in probs_pit if x[0] == '2B'][0]
            triplep = [x[1] for x in probs_hit if x[0] == '3B'][0] + [x[1] for x in probs_pit if x[0] == '3B'][0]
            hrp = [x[1] for x in probs_hit if x[0] == 'HR'][0] + [x[1] for x in probs_pit if x[0] == 'HR'][0]
            outcome = random.choices(['1B', '2B', '3B', 'HR'], (singlep, doublep, triplep, hrp))
        hitter.PA += 1
        pitcher.BF += 1
        if outcome[0] not in ['BB', 'HBP', 'ROE']:
            hitter.AB += 1
        return outcome[0]

# mess with advance bases, may need two different functions, (or three)
def advance_bases(base_state, play_result, hitter, pitcher, vis):
        runs_scored_on_play = 0
        bases_occupied = []
        for base in base_state:
            if base != None:
                bases_occupied.append(base_state.index(base) + 1)

        # if there is a homerun
        if play_result == 'HR':
            runs_scored_on_play += (1 + len(bases_occupied))
            base_state = clear_bases()
            if vis == 'y':
                print(f'{hitter.Name} hits a {1 + len(bases_occupied)} run BOMB off of {pitcher.Name}')

        elif play_result == '3B':
            runs_scored_on_play += len(bases_occupied)
            base_state[2] = hitter

        # only one runner on
        else: # if it isnt a homer of triple
            # no runners on
            if len(bases_occupied) == 0:
                if play_result == 'BB' or play_result == 'HBP':
                    base_state[0] = hitter
                elif play_result == '1B':
                    base_state[0] = hitter
                elif play_result == '2B':
                    base_state[1] = hitter
            # one runner on
            elif len(bases_occupied) == 1:
                if sum(bases_occupied) == 1: # runner on 1st
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '1B':
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '2B':
                        runs_scored_on_play += 1
                        base_state[1] = hitter
                        base_state[0] = None
                elif sum(bases_occupied) == 2: # runner on 2nd
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[0] = hitter
                    elif play_result == '1B':
                        base_state[2] = base_state[1]
                        base_state[0] = hitter
                        base_state[1] = None
                    elif play_result == '2B':
                        runs_scored_on_play += 1
                        base_state[1] = hitter
                elif sum(bases_occupied) == 3: # runner on third base
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[0] = hitter
                    elif play_result == '1B':
                        base_state[0] = hitter
                        runs_scored_on_play += 1
                        base_state[2] = None
                    elif play_result == '2B':
                        base_state[1] = hitter
                        base_state[2] = None
                        runs_scored_on_play += 1
            # two runners on
            elif len(bases_occupied) == 2:
                if sum(bases_occupied) == 3: # first and second
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[2] = base_state[1]
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '1B':
                        base_state[2] = base_state[1]
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '2B':
                        runs_scored_on_play += 1
                        base_state[2] = base_state[1]
                elif sum(bases_occupied) == 5: # second and third
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[0] = hitter
                    elif play_result == '1B':
                        runs_scored_on_play += 1
                        base_state[2] = base_state[1]
                        base_state[1] = None
                        base_state[0] = hitter
                    elif play_result == '2B':
                        runs_scored_on_play += 2
                        base_state[1] = hitter
                        base_state[2] = None
                elif sum(bases_occupied) == 4: # first and third
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '1B':
                        if vis == 'y':
                            print(f'{base_state[2].Name} scores after {hitter.Name} {play_result}')
                        runs_scored_on_play += 1
                        base_state[2] = None
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '2B':
                        if vis == 'y':
                            print(f'{base_state[2].Name} and {base_state[0].Name} scores after {hitter.Name} {play_result}')
                        runs_scored_on_play += 2
                        base_state[1] = hitter
                        base_state[0] = None
                        base_state[2] = None
            # bases loaded (3 runners on)
            elif len(bases_occupied) == 3:
                if play_result == 'BB' or play_result == 'HBP':
                    if vis == 'y':
                        print(f'{base_state[2].Name} scores after {hitter.Name} {play_result}')
                    runs_scored_on_play += 1
                    base_state[2] = base_state[1]
                    base_state[1] = base_state[0]
                    base_state[0] = hitter
                elif play_result == '1B':
                    if vis == 'y':
                        print(f'{base_state[2].Name} scores after {hitter.Name} {play_result}')
                    runs_scored_on_play += 1
                    base_state[2] = base_state[1]
                    base_state[1] = base_state[0]
                    base_state[0] = hitter
                elif play_result == '2B':
                    runs_scored_on_play += 2
                    if vis == 'y':
                        print(f'{base_state[2].Name} and {base_state[1].Name} scores after {hitter.Name} {play_result}')
                    base_state[2] = base_state[0]
                    base_state[1] = hitter
                    base_state[0] = None
        hitter.RBI += runs_scored_on_play
        pitcher.ER += runs_scored_on_play
        return base_state, runs_scored_on_play

def half_inningOther(lineup, current_batsmen_index, pitcher, input_outs = 0, vis = 'y'):
        index = current_batsmen_index
        runs_scored = 0
        base_state = [None, None, None]
        outs = input_outs
        results = []

        if current_batsmen_index == len(lineup):
            index = 0

        while outs < 3:

                    result = PA(lineup[index], pitcher)

                    if vis == 'y':
                        print(f'{str(index + 1)} {lineup[index].team_name} {lineup[index].Name} {result}')

                    # check if there was an out
                    # add double plays eventually
                    if result == 'IPO':
                        lineup[index].IPO += 1
                        pitcher.IPO += 1
                        index += 1
                        results.append(result)
                        outs += 1
                    elif result == 'K':
                        lineup[index].K += 1
                        pitcher.K += 1
                        index += 1
                        results.append(result)
                        outs += 1

                    # then if it was something else
                    elif result == 'HBP':
                        base_state, scored = advance_bases(base_state, result, lineup[index], pitcher, vis = 'n')
                        runs_scored += scored
                        pitcher.HBP += 1
                        results.append(result)
                        lineup[index].HBP += 1
                        index += 1
                    elif result == 'BB':
                        base_state, scored = advance_bases(base_state, result, lineup[index], pitcher, vis = 'n')
                        runs_scored += scored
                        results.append(result)
                        pitcher.BB += 1
                        lineup[index].BB += 1
                        index += 1
                    elif result == 'ROE':
                        # for now we are just counting it as an earned run...
                        base_state, scored = advance_bases(base_state, result, lineup[index], pitcher, vis = 'n')
                        runs_scored += scored
                        results.append(result)
                        pitcher.ROE += 1
                        lineup[index].ROE += 1
                        index += 1

                    # else if it was a hit of some kind

                        # then determine what kind of hit it is
                    elif result == '1B':
                                base_state, scored = advance_bases(base_state, result, lineup[index], pitcher, vis = 'n')
                                runs_scored += scored
                                results.append(result)
                                lineup[index].singles += 1
                                pitcher.singles += 1
                                lineup[index].H += 1
                                index += 1
                                pitcher.H += 1
                    elif result == '2B':
                                base_state, scored = advance_bases(base_state, result, lineup[index], pitcher, vis = 'n')
                                runs_scored += scored
                                results.append(result)
                                lineup[index].doubles += 1
                                lineup[index].H += 1
                                pitcher.doubles += 1
                                pitcher.H += 1
                                index += 1
                    elif result == '3B':
                                base_state, scored = advance_bases(base_state, result, lineup[index], pitcher, vis = 'n')
                                runs_scored += scored
                                results.append(result)
                                lineup[index].triples += 1
                                lineup[index].H += 1
                                pitcher.triples += 1
                                pitcher.H += 1
                                index += 1
                    elif result == 'HR':
                                base_state, scored = advance_bases(base_state, result, lineup[index], pitcher, vis = 'n')
                                runs_scored += scored
                                results.append(result)
                                lineup[index].HR += 1
                                lineup[index].H += 1
                                pitcher.HR += 1
                                pitcher.H += 1
                                index += 1
                    if index == len(lineup):
                        index = 0

        pitcher.IP += 1
        return runs_scored, index, results
