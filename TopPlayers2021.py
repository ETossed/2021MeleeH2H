from numpy import True_
import pysmashgg
import json
import time
import csv
import os
from copy import copy
from statistics import mode

# By ETossed

def results_2021_name(smash, players, events, output):
    # Initialization of Players
    # The players_lower is used now for more efficiency later
    players_lower = []

    if (os.path.isfile('temp.json')):
        print('temp.json found, initializing from file')
        with open('temp.json', 'r') as tempfile:
            player_dict = json.load(tempfile)
            for p in player_dict:
                players_lower.append(p.lower())
    else:
        print("'temp.json' was not found, initializing from empty dictionary")
        for p in players:
            players_lower.append(p.lower())
        player_dict = {}
        for p in players_lower:
            player_dict[p] = {'Events': [], 'Sets': [], 'W': [], 'L': []}

    broke_tourneys = []
    events_not_done = events.copy()

    # Main Loop
    event_num = 0
    for event in events:
        print("Current event: " + str(event))
        event_num += 1
        i = 0
        sets = ['dummy']
        while (sets != []):
            # Iterate through pages
            i += 1
            try:
                sets = smash.event_show_sets(event, i)
            except (TypeError, IndexError) as e:
                broke_tourneys.append(event)
                print("Broken, Index Error or Type Error")
                with open('errors.txt', 'a+') as errors:
                    errors.write(event)
                    errors.write('\n')
                break
            
            if (i % 7 == 0):
                print("Sleeping")
                time.sleep(10) # Might be able to remove, but idk, just not to time out API
            for set in sets:
                # Get entrants, gets rid of sponsor in case they have it in there for some reason
                entrant1 = set['entrant1Players'][0]['playerTag'].split(' | ')[-1].strip().lower()
                entrant2 = set['entrant2Players'][0]['playerTag'].split(' | ')[-1].strip().lower()

                # Checking for set completion and no DQ here instead of at each individual case
                if (set['completed'] and set['entrant1Score'] >= 0 and set['entrant2Score'] >= 0):
                    # Make sure entrants work -- Lot of cases here
                    if (entrant1 == None or entrant2 == None):
                        continue
                    # Both players in the player list
                    elif (entrant1 in players_lower and entrant2 in players_lower):
                        # Checking for event attendance marked already or not
                        if (event not in player_dict[entrant1]['Events']):
                            player_dict[entrant1]['Events'].append(event)
                        if (event not in player_dict[entrant2]['Events']):
                            player_dict[entrant2]['Events'].append(event)

                        # Add set to sets
                        player_dict[entrant1]['Sets'].append(set)
                        player_dict[entrant2]['Sets'].append(set)

                        # Adding wins and losses
                        if (set['entrant1Score'] > set['entrant2Score']):
                            player_dict[entrant1]['W'].append(entrant2)
                            player_dict[entrant2]['L'].append(entrant1)
                        elif (set['entrant2Score'] > set['entrant1Score']):
                            player_dict[entrant2]['W'].append(entrant1)
                            player_dict[entrant1]['L'].append(entrant2)

                    # Only entrant1 in player list
                    elif (entrant1 in players_lower):
                        # Checking for event attendance marked already or not
                        if (event not in player_dict[entrant1]['Events']):
                            player_dict[entrant1]['Events'].append(event)

                        # Add set to sets
                        player_dict[entrant1]['Sets'].append(set)

                        # Only add losses, because if the player isn't in the list it is an expected win
                        if (set['entrant2Score'] > set['entrant1Score']):
                            player_dict[entrant1]['L'].append(set['entrant2Players'][0]['playerTag'].split(' | ')[-1].strip())
                            # That line above is so long above because since they don't have a reference in the json
                            # we're just going to make it capitalized so it's easier

                    # Only entrant 2 in player list
                    elif (entrant2 in players_lower):
                        # Checking for event attendance marked already or not
                        if (event not in player_dict[entrant2]['Events']):
                            player_dict[entrant2]['Events'].append(event)

                        # Add set to sets
                        player_dict[entrant2]['Sets'].append(set)

                        # Only add losses, because if the player isn't in the list it is an expected win
                        if (set['entrant1Score'] > set['entrant2Score']):
                            player_dict[entrant2]['L'].append(set['entrant1Players'][0]['playerTag'].split(' | ')[-1].strip())
                            # That line above is so long above because since they don't have a reference in the json
                            # we're just going to make it capitalized so it's easier

        # Error checking that the tournmament actually loaded
        if (i == 1):
            print("Error: Tournament didn't load")
            if (event not in broke_tourneys):
                broke_tourneys.append(event)
                with open('errors.txt', 'a+') as errors:
                    errors.write(event)
                    errors.write('\n')

        # Failsafe Portion
        with open('temp.json', 'w+') as outfile:
            json.dump(player_dict, outfile, indent=4)

        e_removed = events_not_done.pop(event, None)
        with open('events_not_done.json', 'w+') as outfile:
            json.dump(events_not_done, outfile, indent=4)

    # Complete file output 
    with open('errors.txt', 'w+') as outfile:
        for t in broke_tourneys:
            outfile.write(str(t))

    print(broke_tourneys)

    # Complete file output 
    with open(output, 'w+') as outfile:
        json.dump(player_dict, outfile, indent=4)

def results_2021_ids(smash, pids, events, output):
    # Initialization of Players
    # The players_lower is used now for more efficiency later
    id_list = []

    if (os.stat('temp.json').st_size != 0):
        with open('temp.json', 'r') as tempfile:
            player_dict = json.load(tempfile)
            for p in player_dict:
                id_list.append(player_dict[p]['ID'])
    else:
        print("temp.json empty")
        player_dict = {}
        for p in pids:
            id = pids[p]
            id_list.append(id)
            player_dict[p] = {'ID': id, 'Events': [], 'Sets': [], 'W': [], 'L': []}
    
    broke_tourneys = []
    events_not_done = events.copy()

    # Main Loop
    event_num = 0
    for event in events:
        print("Current event: " + str(event))
        event_num += 1
        i = 0
        sets = ['dummy']
        while (sets != []):
            # Iterate through pages
            i += 1
            try:
                sets = smash.event_show_sets(event, i)
            except TypeError:
                print("Error: Broken Tournament -- " + str(event))
                if (event not in broke_tourneys):
                    broke_tourneys.append(event)
                    with open('errors.txt', 'a+') as errors:
                        errors.write(event)
                        errors.write('\n')

                break
            
            if (i % 6 == 0):
                print("Sleeping")
                time.sleep(10) # Might be able to remove, but idk, just not to time out API
            for set in sets:
                # Get entrants, gets rid of sponsor in case they have it in there for some reason
                entrant1 = set['entrant1Players'][0]['playerTag'].split(' | ')[-1].strip()
                entrant2 = set['entrant2Players'][0]['playerTag'].split(' | ')[-1].strip()

                # Checking for set completion and no DQ here instead of at each individual case
                if (set['completed'] and set['entrant1Score'] >= 0 and set['entrant2Score'] >= 0):
                    # Make sure entrants work -- Lot of cases here
                    if (entrant1 == None or entrant2 == None):
                        continue
                    # Both players in the player list
                    elif (entrant1 in player_dict and entrant2 in player_dict):
                        if (player_dict[entrant1]['ID'] in id_list and player_dict[entrant2]['ID'] in id_list):
                            # Checking for event attendance marked already or not
                            if (event not in player_dict[entrant1]['Events']):
                                player_dict[entrant1]['Events'].append(event)
                            if (event not in player_dict[entrant2]['Events']):
                                player_dict[entrant2]['Events'].append(event)

                            # Add set to sets
                            player_dict[entrant1]['Sets'].append(set)
                            player_dict[entrant2]['Sets'].append(set)

                            # Adding wins and losses
                            if (set['entrant1Score'] > set['entrant2Score']):
                                player_dict[entrant1]['W'].append(entrant2)
                                player_dict[entrant2]['L'].append(entrant1)
                            elif (set['entrant2Score'] > set['entrant1Score']):
                                player_dict[entrant2]['W'].append(entrant1)
                                player_dict[entrant1]['L'].append(entrant2)

                    # Only entrant1 in player list
                    elif (entrant1 in player_dict): # This extra line prevents fraudulent players from getting into the thing
                        if (player_dict[entrant1]['ID'] in id_list):
                            # Checking for event attendance marked already or not
                            if (event not in player_dict[entrant1]['Events']):
                                player_dict[entrant1]['Events'].append(event)

                            # Add set to sets
                            player_dict[entrant1]['Sets'].append(set)

                            # Only add losses, because if the player isn't in the list it is an expected win
                            if (set['entrant2Score'] > set['entrant1Score']):
                                player_dict[entrant1]['L'].append(set['entrant2Players'][0]['playerTag'].split(' | ')[-1].strip())
                                # That line above is so long above because since they don't have a reference in the json
                                # we're just going to make it capitalized so it's easier

                    # Only entrant 2 in player list
                    elif (entrant2 in player_dict): # This extra line prevents fraudulent players from getting into the thing
                        if (player_dict[entrant2]['ID'] in id_list):
                            # Checking for event attendance marked already or not
                            if (event not in player_dict[entrant2]['Events']):
                                player_dict[entrant2]['Events'].append(event)

                            # Add set to sets
                            player_dict[entrant2]['Sets'].append(set)

                            # Only add losses, because if the player isn't in the list it is an expected win
                            if (set['entrant1Score'] > set['entrant2Score']):
                                player_dict[entrant2]['L'].append(set['entrant1Players'][0]['playerTag'].split(' | ')[-1].strip())
                                # That line above is so long above because since they don't have a reference in the json
                                # we're just going to make it capitalized so it's easier

        # Error checking that the tournmament actually loaded
        if (i == 1):
            print("Error: Tournament didn't load -- "+ str(event))
            if (event not in broke_tourneys):
                broke_tourneys.append(event)
                with open('errors.txt', 'a') as errors:
                    errors.write(event)
                    errors.write('\n')

        # Failsafe Portion
        with open('temp.json', 'w+') as outfile:
            json.dump(player_dict, outfile, indent=4)

        e_removed = events_not_done.pop(event, None)
        with open('events_not_done.json', 'w+') as outfile:
            json.dump(events_not_done, outfile, indent=4)
        
        print("Removed event: " + str(e_removed))

    print(broke_tourneys)

    # Complete file output 
    with open(output, 'w') as outfile:
        json.dump(player_dict, outfile, indent=4)

def add_to_results(smash, event):
    # Not done
    return

def to_csv_h2h_names(players, input, output='h2h.csv'):
    # Read json file
    with open(input, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # The players_lower is used now for more efficiency later
    players_lower = []
    for p in players:
        players_lower.append(p.lower())
    
    i = 0
    with open(output, 'w', encoding='utf-8') as new_file:
        # Top left corner
        new_file.write('ETossed,')

        # Header row
        for p in players:
            new_file.write(p + ',')

        # Other losses and newline after header        
        new_file.write('Other losses\n')
        
        # Setup rows
        for p in players:
            new_file.write(p + ',')
            for j in range(len(players)):
                if (i == j):
                    new_file.write('N/A,')
                else:
                    new_file.write('0-0,')

            # Increment i and write other losses and newline
            new_file.write(',\n')
            i += 1

    # Open csv file
    csv_file = csv.reader(open(output))
    csv_lines = list(csv_file)

    # For each w/l find index in player_list
    for i in range(len(players_lower)):
        cur_player = data[players_lower[i]]
        wins = cur_player['W']
        losses = cur_player['L']
        for op in wins:
            # Access cell through csv built in python functions
            j = players_lower.index(op)
            score = csv_lines[i+1][j+1]
            print("i+1: " + str(i+1) + ", j+1: " + str(j+1))

            # Split cell by '-' character and modify score
            temp_score = score.split('-')
            temp_score[0] = str(int(temp_score[0]) + 1)
            new_score = "-".join(temp_score)
            csv_lines[i+1][j+1] = new_score

        other_losses = []

        for op in losses:
            # Access cell through csv built in python functions
            if op in players_lower:
                j = players_lower.index(op)
                score = csv_lines[i+1][j+1]
                print("i+1: " + str(i+1) + ", j+1: " + str(j+1))

                # Split cell by '-' character and modify score
                temp_score = score.split('-')
                temp_score[1] = str(int(temp_score[1]) + 1)
                new_score = "-".join(temp_score)
                csv_lines[i+1][j+1] = new_score
            else: # For non player list losses
                other_losses.append(op)
        
        if other_losses != []:
            csv_lines[i+1][len(players)+1] = ", ".join(other_losses)

    # Write csv
    writer = csv.writer(open(output, 'w+', encoding='utf-8', newline=''))
    writer.writerows(csv_lines)

def to_csv_h2h_ids(players, input, output='h2h.csv'):
    # Read json file
    with open(input, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
    i = 0
    with open(output, 'w', encoding='utf-8') as new_file:
        # Top left corner
        new_file.write('ETossed,')

        # Header row
        for p in players:
            new_file.write(p + ',')

        # Other losses and newline after header        
        new_file.write('Other losses\n')
        
        # Setup rows
        for p in players:
            new_file.write(p + ',')
            for j in range(len(players)):
                if (i == j):
                    new_file.write('N/A,')
                else:
                    new_file.write('0-0,')

            # Increment i and write other losses and newline
            new_file.write(',\n')
            i += 1

    # Open csv file
    csv_file = csv.reader(open(output, encoding='utf-8'))
    csv_lines = list(csv_file)

    # For each w/l find index in player_list
    for i in range(len(players)):
        cur_player = data[players[i]]
        wins = cur_player['W']
        losses = cur_player['L']
        for op in wins:
            # Access cell through csv built in python functions
            j = players.index(op)
            score = csv_lines[i+1][j+1]
            print("i+1: " + str(i+1) + ", j+1: " + str(j+1))

            # Split cell by '-' character and modify score
            temp_score = score.split('-')
            temp_score[0] = str(int(temp_score[0]) + 1)
            new_score = "-".join(temp_score)
            csv_lines[i+1][j+1] = new_score

        other_losses = []

        for op in losses:
            # Access cell through csv built in python functions
            if op in players:
                j = players.index(op)
                score = csv_lines[i+1][j+1]
                print("i+1: " + str(i+1) + ", j+1: " + str(j+1))

                # Split cell by '-' character and modify score
                temp_score = score.split('-')
                temp_score[1] = str(int(temp_score[1]) + 1)
                new_score = "-".join(temp_score)
                csv_lines[i+1][j+1] = new_score
            else: # For non player list losses
                other_losses.append(op)
        
        if other_losses != []:
            csv_lines[i+1][len(players)+1] = ", ".join(other_losses)

    # Write csv
    writer = csv.writer(open(output,'w',encoding='utf-8',newline=''))
    writer.writerows(csv_lines)

def to_csv_wl(players, input, output='win_loss.csv'):
    with open(input, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    players_lower = []
    for p in players:
        players_lower.append(p.lower())
    
    with open(output, 'w', encoding='utf-8') as new_file:
        # Top left corner
        new_file.write('ETossed,')

        # Header row
        new_file.write('Wins,Losses\n')

        for player in players:
            # Initialization
            wins = {}
            losses = {}

            new_file.write(player + ',\"') # Initial quote
            for op in data[player.lower()]['W']:
                # In order to get capitalization
                if op in players_lower:
                    x = players_lower.index(op)
                    real_op = players[x]
                else:
                    real_op = op
                
                if real_op in wins:
                    wins[real_op] += 1
                else:
                    wins[real_op] = 1
            
            # Adding wins to column
            for w in sorted(wins, key=str.casefold):
                if wins[w] == 1:
                    new_file.write(w + ", ")
                else:
                    new_file.write(w + "(x" + str(wins[w]) + "), ")

            # Closing quote and new quote
            new_file.write('\",\"')

            for op in data[player.lower()]['L']:
                # In order to get capitalization
                if op in players_lower:
                    x = players_lower.index(op)
                    real_op = players[x]
                else:
                    real_op = op

                # If already in lossses
                if real_op in losses:
                    losses[real_op] += 1
                # elif op == "kürv": #The umlaut causes it to print the wrong letter wtf
                #     losses["Kurv"] = 1
                else:
                    losses[real_op] = 1
            
            # Adding wins to column
            for l in sorted(losses, key=str.casefold):
                if losses[l] == 1:
                    new_file.write(l + ", ")
                else:
                    new_file.write(l + "(x" + str(losses[l]) + "), ")

            # Closing quote
            new_file.write('\",')

            # Print newline
            new_file.write('\n')

def events_attended(smash, pids, output):
    events = {}
    substrings = ['singles', '1v1', 'championships', 'ladder', 'aman0', 'vip']
    bad_substrings = ['volleyball', 'doubles']

    tp = 1
    for p in pids:
        done = False
        i = 1

        while (not done):
            if (tp % 8 == 0):
                time.sleep(15)

            print("Player: " + p + ", i: " + str(i))
            tourneys = smash.player_show_tournaments_for_game(pids[p]['ID'], p, 1, i)
            for t in tourneys:
                if (t['startTimestamp'] > 1609480800):
                    if any(x in t['eventName'].lower() for x in substrings):
                        if any(y in t['eventName'].lower() for y in bad_substrings):
                            continue
                        elif t['eventId'] not in events: # Make sure no duplicates
                            id = t['eventId']
                            events[id] = {'name': t['name'], 'slug': t['slug'], 'entrants': t['eventEntrants'], 'eventSlug': t['eventSlug']}
                else:
                    done = True
            
            i += 1
            tp += 1
        
        # Failsafe Portion
        with open('temp_events.json', 'w+') as outfile:
            json.dump(events, outfile, indent=4)

    e_array = []
    for e in events:
        e_array.append(e)

    if (len(e_array) == len(set(e_array))):
        print("Done, no repeat events")
    else:
        print("Error: Repeat event")

    # Complete file output 
    with open(output, 'w', encoding='utf-8') as outfile:
        json.dump(events, outfile, indent=4)

def results_to_players(input):
    with open(input, 'r', encoding='utf-8') as json_file:
        full_year = json.load(json_file)
        for p in full_year:
            temp_name = str(p).split('/')[0].strip()

            fname = str(temp_name) + '.json'
            with open(fname, 'w+') as outfile:
                json.dump(full_year[p], outfile, indent=4)

def remove_fake_results(input, pids, output):
    with open(input, 'r') as json_file: # Get results json
        results = json.load(json_file)

    lc_pids = {}
    for pid in pids:
        lc_pids[pid.lower()] = pids[pid]

    for p in results:
        print("Player: " + p)
        correct_id = lc_pids[p]['ID']
        set_indexes_remove = []

        for i in range(len(results[p]['Sets'])):
            cur_set = results[p]['Sets'][i]
            if (p.lower() == cur_set['entrant1Players'][0]['playerTag'].lower()):
                cur_id = cur_set['entrant1Players'][0]['playerId']
                opp_name = cur_set['entrant2Players'][0]['playerTag']
                opp_id = cur_set['entrant2Players'][0]['playerId']
                if (cur_set['entrant1Score'] > cur_set['entrant2Score']):
                    did_win = True
                else:
                    did_win = False
            else:
                cur_id = cur_set['entrant2Players'][0]['playerId']
                opp_name = cur_set['entrant1Players'][0]['playerTag']
                opp_id = cur_set['entrant1Players'][0]['playerId']
                if (cur_set['entrant2Score'] > cur_set['entrant1Score']):
                    did_win = True
                else:
                    did_win = False

            if (correct_id != cur_id):
                set_indexes_remove.insert(0, i)
                if opp_name.lower() in lc_pids:
                    opp_name = opp_name.lower()
                else: 
                    opp_name = opp_name.split('|')[-1].strip()
                if (did_win and opp_name in lc_pids):
                    print("Removing " + opp_name + " from Wins")
                    results[p]['W'].remove(opp_name)
                elif (did_win == False): # If didn't win
                    print("Removing " + opp_name + " from Losses")
                    results[p]['L'].remove(opp_name)

            # For if opponent is fake
            opp_name = opp_name.lower()
            if opp_name in lc_pids:
                if (opp_id != lc_pids[opp_name]['ID']):
                    # print(opp_id)
                    # print(lc_pids[opp_name]['ID'])
                    set_indexes_remove.insert(0, i)
                    if did_win:
                        print("Removing " + opp_name + " from Wins")
                        results[p]['W'].remove(opp_name)
                    elif (did_win == False): # If didn't win
                        print("Removing " + opp_name + " from Losses")
                        results[p]['L'].remove(opp_name)


        print(set_indexes_remove)
        for index in set_indexes_remove:
            del results[p]['Sets'][index]

        with open('temp_results_fixing.json', 'w+') as temp_file: # In case of crashes
            json.dump(results, temp_file, indent=4)
                
    with open(output, 'w') as outfile: # Actual output
        json.dump(results, outfile, indent=4)

def get_most_played_opponents(input, output):
    with open(input, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    players_lower = []
    for p in data:
        players_lower.append(p.lower())
    
    result_dict = {}
    for player in data:
        # Initialization
        result_dict[player] = {'Tag': data[player]['Tag'], 'Opponents': {}}

        for op in data[player]['W']:
            if op in result_dict[player]['Opponents']:
                result_dict[player]['Opponents'][op] += 1
            else:
                result_dict[player]['Opponents'][op] = 1

        for op in data[player]['L']:
            if op in result_dict[player]['Opponents']:
                result_dict[player]['Opponents'][op] += 1
            else:
                result_dict[player]['Opponents'][op] = 1

        temp =  dict(sorted(result_dict[player]['Opponents'].items(), key=lambda item: item[1], reverse=True))
        result_dict[player]['Opponents'] = temp

    with open(output, 'w+', encoding='utf-8') as json_file:
        json.dump(result_dict, json_file, indent=4)

    matchup_dict = {}
    for player in result_dict:
        for op in result_dict[player]['Opponents']:
            p1 = result_dict[player]['Tag']
            p2 = result_dict[op]['Tag']
            if p1 < p2:
                matchup_str = result_dict[player]['Tag'] + '-' + result_dict[op]['Tag']
            else:
                matchup_str = result_dict[op]['Tag'] + '-' + result_dict[player]['Tag']

            if matchup_str not in matchup_dict:
                matchup_dict[matchup_str] = result_dict[player]['Opponents'][op]

    matchup_dict = dict(sorted(matchup_dict.items(), key=lambda item: item[1], reverse=True))
    with open('Entire_List.json', 'w+', encoding='utf-8') as json_file:
        json.dump(matchup_dict, json_file, indent=4)

def events_in_year(smash, output):
    events = {}
    # substrings = ['singles', '1v1', 'championships', 'ladder', 'aman0', 'vip']
    bad_substrings = ['volleyball', 'doubles', 'akaneia', 'wolf', 'teams', 'crews']

    tp = 1
    ta = 1
    i = 1
    done = False
    while(not done):
        tourneys = smash.tournament_show_event_by_game_size_dated(2, 1, 1641016800, 1656997200, i)
        if (tourneys == []):
            done = True
        elif tourneys is None:
            done = True
        else:
            if (i % 6 == 0):
                time.sleep(10)
            for t in tourneys:
                tp += 1
                # if any(x in t['eventName'].lower() for x in substrings):
                if any(y in t['eventName'].lower() for y in bad_substrings):
                    continue
                elif t['eventId'] not in events: # Make sure no duplicates
                    id = t['eventId']
                    events[id] = {'tournamentName': t['tournamentName'], 'tournamentId': t['tournamentId'], 'eventName': t['eventName'], 'entrants': t['numEntrants'], 'online': t['online'], 'endTime': t['endAt']}
                    ta += 1
        
        print("Page " + str(i) + " done")
        i += 1

        # Failsafe Portion
        with open('temp_events.json', 'w+') as outfile:
            json.dump(events, outfile, indent=4)

    e_array = []
    for e in events:
        e_array.append(e)

    if (len(e_array) == len(set(e_array))):
        print("Done, no repeat events")
        print("Pages: " + str(i))
        print("Tournaments processed: " + str(tp))
        print("Tournaments added: " + str(ta))
    else:
        print("Error: Repeat event")

    # Complete file output 
    with open(output, 'w', encoding='utf-8') as outfile:
        json.dump(events, outfile, indent=4)

def big_project(smash, events, output, char_data_name='bp_char_data.json'):
    broke_tourneys = []
    # ultimate_chars = [1271,1272,1273,1274,1275,1276,1277,1278,1279,1280,1282,1283,1285,1286,1287,1289,1290,1291,1292,1293,1294,1295,1296,1297,1298,1299,1300,1301,1302,1304,1305,1307,1310,1311,1313,1314,1315,1316,1317,1318,1319,1320,1321,1322,1323,1324,1325,1326,1327,1328,1329,1330,1331,1332,1333,1334,1335,1336,1337,1338,1339,1340,1341,1405,1406,1407,1408,1409,1410,1411,1412,1413,1414,1415,1441,1453,1526,1530,1532,1539,1746,1747,1766,1777,1795,1846,1897]
    melee_chars = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,1744,628]
    if (os.path.isfile('temp_char_data.json')):
        print('temp_char_data.json found, initializing from file')
        with open('temp_char_data.json', 'r') as tempfile:
            char_arr = json.load(tempfile)
    else:
        char_arr = []
        for i in range(len(melee_chars)):
            char_arr.append({'char': melee_chars[i], 'times_played': 0, 'vs': {}})
        
        for char in char_arr:
            for i in range(len(melee_chars)):
                char['vs'][str(i)] = {'W': 0, 'L': 0}

    # print(json.dumps(char_arr, indent=4))

    if (os.path.isfile('temp_bp.json')):
        print('temp_bp.json found, initializing from file')
        with open('temp_bp.json', 'r') as tempfile:
            player_dict = json.load(tempfile)
    else:
        print("'temp_bp.json' was not found, initializing from empty dictionary")
        player_dict = {}
    
    events_not_done = events.copy()

    # Main Loop
    event_num = 0
    set_num = 0
    page_num = 0
    threetwo = False
    for event in events:
        print("Current event: " + str(event))
        event_num += 1
        i = 1
        sets = ['dummy']
        while (sets != []):
            if ['nodes'] in sets:
                if sets['nodes'] == []:
                    sets = []
                    break
            try:
                sets = smash.event_show_sets(event, i)
                # print(json.dumps(sets, indent=4))
                print("Page: " + str(i))
                page_num += 1
            except (TypeError, IndexError) as e:
                broke_tourneys.append(event)
                print("Broken page, Index Error or Type Error")
                with open('errors.txt', 'a+') as errors:
                    errors.write("Event: " + str(event) + ", page: " + str(i))
                    errors.write('\n')
                sets = ['dummy']

            if (page_num % 35 == 0):
                print("Sleeping, num: " + str(page_num))
                time.sleep(15) # Might be able to remove, but idk, just not to time out API
            if sets is None:
                sets = ['dummy']
            for set in sets:
                if (set == 'dummy'):
                    break
                # Data purposes
                set_num += 1

                
                if (len(set['entrant1Players']) == 0 or len(set['entrant2Players']) == 0):
                    continue
                # Checking for set completion and no DQ here instead of at each individual case
                elif (set['completed'] and set['entrant1Score'] >= 0 and set['entrant2Score'] >= 0):
                    # Get entrants, gets rid of sponsor in case they have it in there for some reason
                    entrant1_name = set['entrant1Players'][0]['playerTag'].split(' | ')[-1].strip()
                    entrant1_id = str(set['entrant1Players'][0]['playerId'])
                    entrant1_event_id = set['entrant1Players'][0]['entrantId']
                    entrant2_name = set['entrant2Players'][0]['playerTag'].split(' | ')[-1].strip()
                    entrant2_id = str(set['entrant2Players'][0]['playerId'])
                    entrant2_event_id = set['entrant2Players'][0]['entrantId']

                    # Checking if player is in player dictionary
                    if (entrant1_id not in player_dict):
                        player_dict[entrant1_id] = {'Tag': entrant1_name, 'Event_ids': [], 'Tourney_names': [], 'Chars_used': {}, 'W': [], 'L': []}

                    if (entrant2_id not in player_dict):
                        player_dict[entrant2_id] = {'Tag': entrant2_name, 'Event_ids': [], 'Tourney_names': [], 'Chars_used': {}, 'W': [], 'L': []}

                    # Checking if player has this event marked down
                    if (event not in player_dict[entrant1_id]['Event_ids']):
                        player_dict[entrant1_id]['Event_ids'].append(event)
                        player_dict[entrant1_id]['Tourney_names'].append(events[event]['tournamentName'])

                    if (event not in player_dict[entrant2_id]['Event_ids']):
                        player_dict[entrant2_id]['Event_ids'].append(event)
                        player_dict[entrant2_id]['Tourney_names'].append(events[event]['tournamentName'])

                    # W/L
                    if (set['entrant1Score'] > set['entrant2Score']):
                        player_dict[entrant1_id]['W'].append(entrant2_id)
                        player_dict[entrant2_id]['L'].append(entrant1_id)
                    elif (set['entrant2Score'] > set['entrant1Score']):
                        player_dict[entrant2_id]['W'].append(entrant1_id)
                        player_dict[entrant1_id]['L'].append(entrant2_id)
                    
                    # Character_data parts
                    if ('entrant1Chars' in set and 'entrant2Chars' in set):
                        if (len(set['entrant1Chars']) != len(set['entrant2Chars'])):
                            continue
                        else:
                            for a in range(len(set['entrant1Chars'])):
                                char1 = melee_chars.index(set['entrant1Chars'][a])
                                char2 = melee_chars.index(set['entrant2Chars'][a])
                                game_winner = set['gameWinners'][a]
                                # # 1744 is random character
                                # if (char1 == 1744):
                                #     char1 = 27
                                # if (char2 == 1744):
                                #     char2 = 27
                                # # 628 is Shielda
                                # if (char1 == 628):
                                #     char1 = 28
                                # if (char2 == 628):
                                #     char2 = 28

                                if (char1 in range(len(melee_chars)) and char2 in range(len(melee_chars))):
                                    char_arr[char1]['times_played'] += 1
                                    char_arr[char2]['times_played'] += 1

                                    if str(char1) in player_dict[entrant1_id]['Chars_used']:
                                        player_dict[entrant1_id]['Chars_used'][str(char1)] += 1
                                    else:
                                        player_dict[entrant1_id]['Chars_used'][str(char1)] = 1

                                    if str(char2) in player_dict[entrant2_id]['Chars_used']:
                                        player_dict[entrant2_id]['Chars_used'][str(char2)] += 1
                                    else:
                                        player_dict[entrant2_id]['Chars_used'][str(char2)] = 1

                                    # W/L for char
                                    if (game_winner == entrant1_event_id):
                                        char_arr[char1]['vs'][str(char2)]['W'] += 1
                                        char_arr[char2]['vs'][str(char1)]['L'] += 1
                                    elif (game_winner == entrant2_event_id):
                                        char_arr[char2]['vs'][str(char1)]['W'] += 1
                                        char_arr[char1]['vs'][str(char2)]['L'] += 1

                                elif (char1 in range(len(melee_chars))):
                                    char_arr[char1]['times_played'] += 1
                                    if str(char1) in player_dict[entrant1_id]['Chars_used']:
                                        player_dict[entrant1_id]['Chars_used'][str(char1)] += 1
                                    else:
                                        player_dict[entrant1_id]['Chars_used'][str(char1)] = 1
                                elif (char2 in range(len(melee_chars))):
                                    char_arr[char2]['times_played'] += 1
                                    if str(char2) in player_dict[entrant2_id]['Chars_used']:
                                        player_dict[entrant2_id]['Chars_used'][str(char2)] += 1
                                    else:
                                        player_dict[entrant2_id]['Chars_used'][str(char2)] = 1

                    elif ('entrant1Chars' in set):
                        for x in set['entrant1Chars']:
                            if (x == 1744): # Random
                                x = 27
                            if (x == 628): # Shielda
                                x = 28

                            if (x in range(len(melee_chars))):
                                char_arr[x]['times_played'] += 1 # Overall data
                                if str(x) in player_dict[entrant1_id]['Chars_used']:
                                    player_dict[entrant1_id]['Chars_used'][str(x)] += 1
                                else:
                                    player_dict[entrant1_id]['Chars_used'][str(x)] = 1

                    elif ('entrant2Chars' in set):
                        for x in set['entrant2Chars']:
                            if (x == 1744): # Random
                                x = 27
                            if (x == 628): # Shielda
                                x = 28

                            if (x in range(len(melee_chars))):
                                char_arr[x]['times_played'] += 1 # Overall data
                                if x in player_dict[entrant2_id]['Chars_used']:
                                    player_dict[entrant2_id]['Chars_used'][str(x)] += 1
                                else:
                                    player_dict[entrant2_id]['Chars_used'][str(x)] = 1

            i += 1 # Increment i

        if (i == 1):
            print("Error: Tournament didn't load")
            if (event not in broke_tourneys):
                broke_tourneys.append(event)
                with open('errors.txt', 'a+') as errors:
                    errors.write(event)
                    errors.write('\n')

        # Failsafe Portion
        with open('temp_bp.json', 'w+') as outfile:
            json.dump(player_dict, outfile, indent=4)

        with open('temp_char_data.json', 'w+') as charfile:
            json.dump(char_arr, charfile, indent=4)

        e_removed = events_not_done.pop(event, None)
        with open('events_not_done.json', 'w+') as outfile:
            json.dump(events_not_done, outfile, indent=4)

    arr = ["dummy", "Bowser", "Captain Falcon", "Donkey Kong", "Dr. Mario", "Falco", "Fox", "Ganondorf", "Ice Climbers", "Jigglypuff", "Kirby", "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Mr. Game and Watch", "Ness", "Peach", "Pichu", "Pikachu", "Roy", "Samus", "Sheik", "Yoshi", "Young Link", "Zelda", "Random", "Shielda"]

    # Data Cleanup
    for p in player_dict:
        player_dict[p]['Number_sets'] = len(player_dict[p]['W']) + len(player_dict[p]['L'])

    # File cleanup
    os.remove('temp_bp.json')
    os.remove('temp_char_data.json')
    os.remove('events_not_done.json')

    print("Sets played: " + str(set_num))
    print("Pages gone through: " + str(page_num))
    print("Events gone through: " + str(page_num))

    # Complete char data file output
    with open(char_data_name, 'w+') as outfile:
        json.dump(char_arr, outfile, indent=4)

    # Complete file output 
    with open(output, 'w+') as outfile:
        json.dump(player_dict, outfile, indent=4)

def char_data_to_csvs(char_data, year):
    # Character Usage csv print
    with open('Char_Usage' + year + '.csv', 'w+') as outfile:
        for char in char_data:
            outfile.write(char['char'])
            outfile.write(',')
            outfile.write(str(char['times_played']))
            outfile.write('\n')

    # Record csv print
    with open('Char_Records' + year + '.csv', 'w+') as outfile:
        for char in char_data:
            char_str = ""
            # print(char)
            cur_char = char['vs']
            for opp in cur_char:
                temp = str(cur_char[opp]['W']) + '-' + str(cur_char[opp]['L']) + ","
                char_str += temp

            outfile.write(char_str)
            outfile.write('\n')

    # Winrate csv
    with open('Char_Winrate' + year + '.csv', 'w+') as outfile:
        for char in char_data:
            char_str = ""
            # print(char)
            cur_char = char['vs']
            for opp in cur_char:
                if cur_char[opp]['W'] + cur_char[opp]['L'] == 0:
                    char_str += "N/A,"
                else:
                    temp = str(cur_char[opp]['W'] / (cur_char[opp]['W'] + cur_char[opp]['L'])) + ","
                    char_str += temp

            outfile.write(char_str)
            outfile.write('\n')

    # Most Played Matchups csv
    with open('Most_Played_Matchups' + year + '.csv', 'w+') as outfile:
        matchups = []
        games_nums = []
        for char in char_data:
            cur_char = char['vs']
            # print(char)
            for opp in cur_char:
                if (char['char'] == opp or char['char'] < opp):
                    matchup_str = char['char'] + "-" + opp 
                    matchups.append(matchup_str)
                    if char['char'] == opp:
                        games = cur_char[opp]['W']
                    else:
                        games = cur_char[opp]['W'] + cur_char[opp]['L']
                    games_nums.append(games)

        for i in range(len(matchups)):
            outfile.write(matchups[i])
            outfile.write(',')
            outfile.write(str(games_nums[i]))
            outfile.write('\n')

    return

def character_played_most_by_player(results, output):
    arr = ["dummy", "Bowser", "Captain Falcon", "Donkey Kong", "Dr. Mario", "Falco", "Fox", "Ganondorf", "Ice Climbers", "Jigglypuff", "Kirby", "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Mr. Game and Watch", "Ness", "Peach", "Pichu", "Pikachu", "Roy", "Samus", "Sheik", "Yoshi", "Young Link", "Zelda", "Random", "Shielda"]
    ultimate_chars = ['Bayonetta', 'Bowser Jr.', 'Bowser', 'Captain Falcon', 'Cloud', 'Corrin', 'Daisy', 'Dark Pit', 'Diddy Kong', 'Donkey Kong', 'Dr. Mario', 'Duck Hunt', 'Falco', 'Fox', 'Ganondorf', 'Greninja', 'Ice Climbers', 'Ike', 'Inkling', 'Jigglypuff', 'King Dedede', 'Kirby', 'Link', 'Little Mac', 'Lucario', 'Lucas', 'Lucina', 'Luigi', 'Mario', 'Marth', 'Mega Man', 'Meta Knight', 'Mewtwo', 'Mii Brawler', 'Ness', 'Olimar', 'Pac-Man', 'Palutena', 'Peach', 'Pichu', 'Pikachu', 'Pit', 'Pokemon Trainer', 'Ridley', 'R.O.B.', 'Robin', 'Rosalina', 'Roy', 'Ryu', 'Samus', 'Sheik', 'Shulk', 'Snake', 'Sonic', 'Toon Link', 'Villager', 'Wario', 'Wii Fit Trainer', 'Wolf', 'Yoshi', 'Young Link', 'Zelda', 'Zero Suit Samus', 'Mr. Game & Watch', 'Incineroar', 'King K. Rool', 'Dark Samus', 'Chrom', 'Ken', 'Simon Belmont', 'Richter', 'Isabelle', 
    'Mii Swordfighter', 'Mii Gunner', 'Piranha Plant', 'Joker', 'Hero', 'Banjo-Kazooie', 'Terry', 'Byleth', 'Random Character', 'Min Min', 'Steve', 'Sephiroth', 'Pyra & Mythra', 'Kazuya', 'Sora']
    player_dict = {}
    print(len(ultimate_chars))
    for i in range(len(ultimate_chars)):
        player_dict[ultimate_chars[i]] = {'Player': '', 'Games': 0}

    # print(json.dumps(player_dict, indent=4))

    for player in results:
        for i in results[player]['Chars_used']:
            cur_char = i
            cur_char_games = results[player]['Chars_used'][i]

            if (cur_char_games > player_dict[cur_char]['Games']):
                player_dict[cur_char]['Games'] = cur_char_games
                player_dict[cur_char]['Player'] = results[player]['Tag']

    # print stuff
    print("Character, Player, Games")
    for player in player_dict:
        print(player + ', ' + player_dict[player]['Player'] + ', ' + str(player_dict[player]['Games']))

    with open(output, 'w+') as outfile:
        json.dump(player_dict, outfile, indent=4)

def players_per_region(results, player_locations):
    location_dict = {}
    for p in player_locations:
        if p in results:
            cur_results = results[p]
            # print(p)
            cur_sets_played = cur_results['Number_sets']
            cur_chars_used = cur_results['Chars_used']
            cur_tag = player_locations[p]['Tag']
            cur_country = player_locations[p]['Country']
            if cur_country == "CA":
                cur_country = "Canada"
            cur_state = player_locations[p]['State']

            if cur_country not in location_dict:
                location_dict[cur_country] = {'Sets_played': copy(cur_sets_played), 'Num_players': 1, 'Players_list': [copy(cur_tag)],
                'Chars_used': copy(cur_chars_used), 'Player_most_sets': copy(cur_tag), 'Player_most_sets_num': copy(cur_sets_played), 'States': {}}
            else:
                location_dict[cur_country]['Sets_played'] += cur_sets_played
                location_dict[cur_country]['Num_players'] += 1
                location_dict[cur_country]['Players_list'].append(cur_tag)

                # Update char data
                for char in cur_chars_used:
                    if char not in location_dict[cur_country]['Chars_used']:
                        location_dict[cur_country]['Chars_used'][char] = cur_chars_used[char]
                    else:
                        location_dict[cur_country]['Chars_used'][char] += cur_chars_used[char]

                # Replace most active player
                if (cur_sets_played > location_dict[cur_country]['Player_most_sets_num']):
                    location_dict[cur_country]['Player_most_sets'] = cur_tag
                    location_dict[cur_country]['Player_most_sets_num'] = cur_sets_played

            if cur_state is not None: # SOMETHING HERE BROKEN
                if cur_state not in location_dict[cur_country]['States']:
                    location_dict[cur_country]['States'][cur_state] = {'Sets_played': cur_sets_played, 'Num_players': 1, 
                    'Players_list': [cur_tag], 'Chars_used': cur_chars_used, 'Player_most_sets': cur_tag, 
                    'Player_most_sets_num': cur_sets_played}
                else:
                    location_dict[cur_country]['States'][cur_state]['Sets_played'] += cur_sets_played
                    location_dict[cur_country]['States'][cur_state]['Num_players'] += 1
                    location_dict[cur_country]['States'][cur_state]['Players_list'].append(cur_tag)

                    # Update char data
                    for char in cur_chars_used:
                        if char not in location_dict[cur_country]['States'][cur_state]['Chars_used']:
                            location_dict[cur_country]['States'][cur_state]['Chars_used'][char] = cur_chars_used[char]
                        else:
                            location_dict[cur_country]['States'][cur_state]['Chars_used'][char] += cur_chars_used[char]

                    # Replace most active player
                    if (cur_sets_played > location_dict[cur_country]['States'][cur_state]['Player_most_sets_num']):
                        location_dict[cur_country]['States'][cur_state]['Player_most_sets'] = cur_tag
                        location_dict[cur_country]['States'][cur_state]['Player_most_sets_num'] = cur_sets_played

    with open('Players_Per_Region.json', 'w+', encoding='utf-8') as outfile:
        json.dump(location_dict, outfile, indent=4)

def players_per_region_to_csvs(ppr):
    with open('Countries.csv', 'w+', encoding='utf-8') as country_file:
        country_file.write('Country, # Players, Sets Played, Player With Most Sets, Player Most Sets #, Most Played Character, # Character Times Played\n')
        for place in ppr:
            most_played_char = ""
            char_times_played = 0
            for char in ppr[place]['Chars_used']:
                if ppr[place]['Chars_used'][char] > char_times_played:
                    char_times_played = ppr[place]['Chars_used'][char]
                    most_played_char = char
                elif ppr[place]['Chars_used'][char] == char_times_played: # In weird event of a tie
                    most_played_char = most_played_char + '/' + char
            
            # Actual writing
            country_file.write(place)
            country_file.write(',')
            country_file.write(str(ppr[place]['Num_players']))
            country_file.write(',')
            country_file.write(str(ppr[place]['Sets_played']))
            country_file.write(',')
            country_file.write(ppr[place]['Player_most_sets'])
            country_file.write(',')
            country_file.write(str(ppr[place]['Player_most_sets_num']))
            country_file.write(',')
            country_file.write(most_played_char)
            country_file.write(',')
            country_file.write(str(char_times_played))
            country_file.write('\n')

    
    with open('US_States.csv', 'w+', encoding='utf-8') as state_file:
        state_file.write('States, # Players, Sets Played, Player With Most Sets, Player Most Sets #, Most Played Character, # Character Times Played\n')
        for state in ppr['United States']['States']:
            most_played_char = ""
            char_times_played = 0
            for char in ppr['United States']['States'][state]['Chars_used']:
                if ppr['United States']['States'][state]['Chars_used'][char] > char_times_played:
                    char_times_played = ppr['United States']['States'][state]['Chars_used'][char]
                    most_played_char = char
                elif ppr['United States']['States'][state]['Chars_used'][char] == char_times_played: # In weird event of a tie
                    most_played_char = most_played_char + '/' + char
            
            # Actual writing
            state_file.write(state)
            state_file.write(',')
            state_file.write(str(ppr['United States']['States'][state]['Num_players']))
            state_file.write(',')
            state_file.write(str(ppr['United States']['States'][state]['Sets_played']))
            state_file.write(',')
            state_file.write(ppr['United States']['States'][state]['Player_most_sets'])
            state_file.write(',')
            state_file.write(str(ppr['United States']['States'][state]['Player_most_sets_num']))
            state_file.write(',')
            state_file.write(most_played_char)
            state_file.write(',')
            state_file.write(str(char_times_played))
            state_file.write('\n')

    with open('Canadian_Provinces.csv', 'w+', encoding='utf-8') as state_file:
        state_file.write('Provinces, # Players, Sets Played, Player With Most Sets, Player Most Sets #, Most Played Character, # Character Times Played\n')
        for state in ppr['Canada']['States']:
            most_played_char = ""
            char_times_played = 0
            for char in ppr['Canada']['States'][state]['Chars_used']:
                if ppr['Canada']['States'][state]['Chars_used'][char] > char_times_played:
                    char_times_played = ppr['Canada']['States'][state]['Chars_used'][char]
                    most_played_char = char
                elif ppr['Canada']['States'][state]['Chars_used'][char] == char_times_played: # In weird event of a tie
                    most_played_char = most_played_char + '/' + char
            
            # Actual writing
            state_file.write(state)
            state_file.write(',')
            state_file.write(str(ppr['Canada']['States'][state]['Num_players']))
            state_file.write(',')
            state_file.write(str(ppr['Canada']['States'][state]['Sets_played']))
            state_file.write(',')
            state_file.write(ppr['Canada']['States'][state]['Player_most_sets'])
            state_file.write(',')
            state_file.write(str(ppr['Canada']['States'][state]['Player_most_sets_num']))
            state_file.write(',')
            state_file.write(most_played_char)
            state_file.write(',')
            state_file.write(str(char_times_played))
            state_file.write('\n')

    with open('Australian_States.csv', 'w+', encoding='utf-8') as state_file:
        state_file.write('States, # Players, Sets Played, Player With Most Sets, Player Most Sets #, Most Played Character, # Character Times Played\n')
        for state in ppr['Australia']['States']:
            most_played_char = ""
            char_times_played = 0
            for char in ppr['Australia']['States'][state]['Chars_used']:
                if ppr['Australia']['States'][state]['Chars_used'][char] > char_times_played:
                    char_times_played = ppr['Australia']['States'][state]['Chars_used'][char]
                    most_played_char = char
                elif ppr['Australia']['States'][state]['Chars_used'][char] == char_times_played: # In weird event of a tie
                    most_played_char = most_played_char + '/' + char
            
            # Actual writing
            state_file.write(state)
            state_file.write(',')
            state_file.write(str(ppr['Australia']['States'][state]['Num_players']))
            state_file.write(',')
            state_file.write(str(ppr['Australia']['States'][state]['Sets_played']))
            state_file.write(',')
            state_file.write(ppr['Australia']['States'][state]['Player_most_sets'])
            state_file.write(',')
            state_file.write(str(ppr['Australia']['States'][state]['Player_most_sets_num']))
            state_file.write(',')
            state_file.write(most_played_char)
            state_file.write(',')
            state_file.write(str(char_times_played))
            state_file.write('\n')

def mains_per_state(results, player_locations):
    state_dict = {}
    arr = ["Bowser", "Captain Falcon", "Donkey Kong", "Dr. Mario", "Falco", "Fox", "Ganondorf", "Ice Climbers", "Jigglypuff", "Kirby", "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Mr. Game and Watch", "Ness", "Peach", "Pichu", "Pikachu", "Roy", "Samus", "Sheik", "Yoshi", "Young Link", "Zelda", "Random", "Shielda"]

    for p in player_locations:
        if p in results:
            cur_results = results[p]
            cur_main = ""
            cur_main_num = 0
            # if (player_locations[p]['Country'] == "Canada" and player_locations[p]['State'] is not None):
            if (player_locations[p]['Country'] not in state_dict):
                state_dict[player_locations[p]['Country']] = {"Characters": {}, "Num_players": 1} # Char dict
            else:
                state_dict[player_locations[p]['Country']]["Num_players"] += 1
            
            if (cur_results['Chars_used'] != {}):
                for c in cur_results['Chars_used']:
                    if cur_results['Chars_used'][c] > cur_main_num:
                        cur_main = arr[int(c)]
                        cur_main_num = cur_results['Chars_used'][c]
                
                if (cur_main not in state_dict[player_locations[p]['Country']]["Characters"]):
                    state_dict[player_locations[p]['Country']]["Characters"][cur_main] = 1
                else:
                    state_dict[player_locations[p]['Country']]["Characters"][cur_main] += 1

    
    new_state_dict = {}
    for s in state_dict:
        new_state_dict[s] = {"Characters": {}, "Num_players": 1}
        new_state_dict[s]["Characters"] = dict(sorted(state_dict[s]["Characters"].items(), key=lambda item: item[1], reverse=True))
        new_state_dict[s]["Num_players"] = state_dict[s]["Num_players"]

    sorted_keys = sorted(state_dict, key=lambda item: state_dict[item]["Num_players"], reverse=True)
    final_state_dict = {}
    for key in sorted_keys:
        final_state_dict[key] = new_state_dict[key]

    with open("mains_per_state.json", "w+") as outfile:
        json.dump(final_state_dict, outfile, indent=4)
    
def main():
    # Initialize pysmashgg
    with open(".env", "r") as fp: # Would use .env but my computer hates it, feel free to use it
        key = fp.readline()

    smash = pysmashgg.SmashGG(key)

    # arr = ["dummy", "Bowser", "Captain Falcon", "Donkey Kong", "Dr. Mario", "Falco", "Fox", "Ganondorf", "Ice Climbers", "Jigglypuff", "Kirby", "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Mr. Game and Watch", "Ness", "Peach", "Pichu", "Pikachu", "Roy", "Samus", "Sheik", "Yoshi", "Young Link", "Zelda", "Random", "Shielda"]
    
    # events_in_year(smash, 'Events_Thru_Jul_4.json')

    with open('Events_Thru_Jul_4.json', 'r', encoding='utf-8') as tempfile:
        events_2022 = json.load(tempfile)

    big_project(smash, events_2022, "Results_Thru_Jul_4.json")

    # TODO 
    # with open('D:\\git\\2021Melee\\Ultimate\\Ultimate_Player_Locations_2021.json', 'r', encoding='utf-8') as tempfile:
    #     results_2022 = json.load(tempfile)

    # tag_arr = []
    # tag_dict = {}

    # for p in results_2022:
    #     if results_2022[p]["Tag"] is None:
    #         continue;
    #     elif len(results_2022[p]["Tag"]) > 15:
    #         tag_arr.append(results_2022[p]["Tag"])
    
    # tag_arr.sort(key=len, reverse=True)
    
    # for t in tag_arr:
    #     tag_dict[t] = len(t)

    # with open('temp2.json', 'w+', encoding='utf-8') as tempfile:
    #     json.dump(tag_dict, tempfile, indent=4)

    


    # big_project(smash, results_2022, 'Results_Thru_March_2022.json')

    # with open('D:\\git\\2021Melee\\Ultimate\\Ultimate_Results_2021.json', 'r', encoding='utf-8') as tempfile:
    #     ultimate_results_2021 = json.load(tempfile)

    # get_most_played_opponents('Results_Thru_March_2022.json', 'mpp_thru_march.json')

    # with open('D:\\git\\2021Melee\\Players_by_Region\\Player_Locations_2021_Full_Year.json', 'r', encoding='utf-8') as tempfile:
    #     player_locations = json.load(tempfile)

    # with open('D:\\git\\2021Melee\\Ultimate\\Ultimate_Player_Locations_2021.json', 'r', encoding='utf-8') as tempfile:
    #     ultimate_player_locations = json.load(tempfile)

    # with open('mains_per_state.json', 'r', encoding='utf-8') as tempfile:
    #     mains_per_p = json.load(tempfile)

    # for s in mains_per_p:
    #     i = 0
    #     print(s + ",", end="")
    #     if mains_per_p[s]["Characters"] == {}:
    #         print("N/A" + ",N/A")
    #     else:
    #         for c in mains_per_p[s]["Characters"]:
    #             print(c + ",", end="")
    #             print(mains_per_p[s]["Characters"][c])
    #             if (i == 0):
    #                 break
    
    # players_per_region(results_ultimate, locations_ultimate)
    # players_per_region_to_csvs(ppr_ultimate)

    # DONE
    # events_in_year(smash, 'Events_Thru_Feb_2022.json')
    # big_project(smash, events_2022, 'Results_Thru_Feb_2022.json', 'CharData_Thru_Feb_2022.json');
    # mains_per_state(results_2021, player_locations)
    
    # # Replace numbers with chars
    # for char in char_data:
    #     if char['char'] != 0:
    #         char['char'] = arr[int(char['char'])]
    #         temp_char_vs = {}
    #         for opp in char['vs']:
    #             if opp != "0":
    #                 temp_char_vs[arr[int(opp)]] = char['vs'][opp]

    #         char['vs'] = temp_char_vs

    # with open('CharData_2019.json', 'w+') as outfile:
    #     json.dump(char_data, outfile, indent=4)

    # # Replace numbers in results with chars
    # for player in results_2019:
    #     new_char_dict = {}
    #     for char in results_2019[player]['Chars_used']:
    #         new_char_dict[arr[int(char)]] = results_2019[player]['Chars_used'][char]

    #     results_2019[player]['Chars_used'] = new_char_dict

    # with open('Results_2018.json', 'w+') as outfile:
    #     json.dump(results_2019, outfile, indent=4)

    # for i in range(2,30):
    #     print("=C" + str(i) + "/C30")

    # # Combining Character Data
    # cd_arr = [char_data_2021, char_data_2020, char_data_2019, char_data_2018, char_data_2017, char_data_2016]
    # for cd in cd_arr:
    #     for i in range(len(cd)):
    #         char_data_end[i]['times_played'] += cd[i]['times_played']
    #         for char in cd[i]['vs']:
    #             char_data_end[i]['vs'][char]['W'] += cd[i]['vs'][char]['W']
    #             char_data_end[i]['vs'][char]['L'] += cd[i]['vs'][char]['L']

    # with open('CharData_ALL.json', 'w+') as outfile:
    #     json.dump(char_data_end, outfile, indent=4)

    # # Combining Results Files
    # for results in rarr:
    #     for p in results:
    #         if p in results_end:
    #             results_end[p]['Number_sets'] += results[p]['Number_sets']
    #             results_end[p]['Event_ids'] += results[p]['Event_ids']
    #             results_end[p]['W'] += results[p]['W']
    #             results_end[p]['L'] += results[p]['L']
    #             for char in results[p]['Chars_used']:
    #                 if char in results_end[p]['Chars_used']:
    #                     results_end[p]['Chars_used'][char] += results[p]['Chars_used'][char]
    #                 else:
    #                     results_end[p]['Chars_used'][char] = results[p]['Chars_used'][char]
    #         else:
    #             results_end[p] = results[p]

    # with open('Results_ALL.json', 'w+') as outfile:
    #     json.dump(results_end, outfile, indent=4)

if __name__ == "__main__":
    main()
