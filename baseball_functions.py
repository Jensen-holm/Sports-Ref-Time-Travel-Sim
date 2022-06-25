import random

def PA(hitter, pitcher):
        result = random.choices(['K', 'BB', 'H', 'IPO', 'HBP'], weights = (hitter.Kp + pitcher.Kp, hitter.BBp + pitcher.BBp, hitter.Hp + pitcher.Hp, hitter.IPOp + pitcher.IPOp, hitter.HBPp + pitcher.HBPp))
        hitter.PA += 1
        pitcher.BF += 1
        if result != 'HBP' and result != 'BB':
            hitter.AB += 1
        return result[0]

def clear_bases():
        return [None, None, None]

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
        elif play_result != 'HR' and play_result != '3B':
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

def half_inning(lineup, current_batsman_index, pitcher, visualize = 'n'):
        index = current_batsman_index
        runs_scored = 0
        # base_state = base_state
        # base_stase = self.clear_bases(base_state)
        base_state = [None, None, None]
        outs = 0
        results = []

        if current_batsman_index >= len(lineup):
            index = 0

        while outs < 3:

            result = PA(lineup[index], pitcher)

            if visualize == 'y':
                print(f'{lineup[index].team} {index + 1} {lineup[index].Name} {result}')

            # check if there was an out
            if result == 'IPO':
                lineup[index].IPO += 1
                index += 1
                results.append(result)
                outs += 1
            elif result == 'K':
                lineup[index].K += 1
                pitcher.K += 1
                index += 1
                results.append('K')
                outs += 1

            # then if it was something else
            elif result == 'HBP':
                base_state, scored = advance_bases(base_state, result, lineup[index], pitcher, visualize)
                runs_scored += scored
                pitcher.HBP += 1
                results.append(result)
                lineup[index].HBP += 1
                index += 1
            elif result == 'BB':
                base_state, scored = advance_bases(base_state, result, lineup[index], pitcher, visualize)
                runs_scored += scored
                results.append(result)
                pitcher.BB += 1
                lineup[index].BB += 1
                index += 1
            elif result == 'H':
                pitcher.H += 1
                lineup[index].H += 1
                # then determine what kind of hit it is
                hit_type = random.choices(['1B', '2B', '3B', 'HR'], (lineup[index].singlep, lineup[index].doublep, lineup[index].triplep, lineup[index].HRp))[0]
                if hit_type == '1B':
                    base_state, scored = advance_bases(base_state, hit_type, lineup[index], pitcher, visualize)
                    runs_scored += scored
                    results.append(hit_type)
                    lineup[index].singles += 1
                    pitcher.singles += 1
                    index += 1
                elif hit_type == '2B':
                    base_state, scored = advance_bases(base_state, hit_type, lineup[index], pitcher, visualize)
                    runs_scored += scored
                    results.append(hit_type)
                    lineup[index].doubles += 1
                    pitcher.doubles += 1
                    index += 1
                elif hit_type == '3B':
                    base_state, scored = advance_bases(base_state, hit_type, lineup[index], pitcher, visualize)
                    runs_scored += scored
                    results.append(hit_type)
                    lineup[index].triples += 1
                    pitcher.triples += 1
                    index += 1
                elif hit_type == 'HR':
                    base_state, scored = advance_bases(base_state, hit_type, lineup[index], pitcher, visualize)
                    runs_scored += scored
                    results.append(hit_type)
                    lineup[index].HR += 1
                    pitcher.HR += 1
                    index += 1

            if index >= len(lineup):
                index = 0
        pitcher.IP += 1
        return runs_scored, index, results