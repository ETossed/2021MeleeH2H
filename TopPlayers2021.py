import pysmashgg
import json
import time
import csv
import os

# By ETossed

def results_2021_name(smash, players, events, output):
    # Initialization of Players
    # The players_lower is used now for more efficiency later
    players_lower = []
    for p in players:
        players_lower.append(p.lower())
    player_dict = {}
    for p in players_lower:
        player_dict[p] = {'Events': [], 'Sets': [], 'W': [], 'L': []}

    broke_tourneys = []

    # Main Loop
    event_num = 0
    for event in events:
        print("Current event: " + str(event))
        event_num += 1
        i = 1
        sets = ['dummy']
        while (sets != []):
            # Iterate through pages
            try:
                sets = smash.event_show_sets(event, i)
            except TypeError:
                broke_tourneys.append(event)
                print("Broken")
                break
            i += 1
            if (i % 6 == 0):
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

    # Complete file output 
    with open('errors.txt', 'w') as outfile:
        for t in broke_tourneys:
            outfile.write(str(t))

    print(broke_tourneys)

    # Complete file output 
    with open(output, 'w') as outfile:
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

    # with open('eu_events.json', 'r') as json_file:
    #     events_not_done = json.load(json_file)

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
                    with open('errors.txt', 'a') as errors:
                        errors.write(event)
                        errors.write('\n')

                break
            
            if (i % 6 == 0):
                print("Sleeping")
                time.sleep(10) # Might be able to remove, but idk, just not to time out API
            for set in sets:
                # print(json.dumps(set, indent=4)) # For debugging purposes
                # print("\n")
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
        with open('temp.json', 'w') as outfile:
            json.dump(player_dict, outfile, indent=4)

        # e_removed = events_not_done.pop(event, None)
        # with open('events_not_done.json', 'w') as outfile:
        #     json.dump(events_not_done, outfile, indent=4)
        
        # print("Removed event: " + str(e_removed))

    print(broke_tourneys)

    # Complete file output 
    with open(output, 'w') as outfile:
        json.dump(player_dict, outfile, indent=4)

def add_to_results(smash, event):
    # Not done
    return

def to_csv_h2h_names(players, input, output='h2h.csv'):
    # Read json file
    with open(input, 'r') as json_file:
        data = json.load(json_file)

    # The players_lower is used now for more efficiency later
    players_lower = []
    for p in players:
        players_lower.append(p.lower())
    
    i = 0
    with open(output, 'w') as new_file:
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
            temp_score[0] = str(int(score[0]) + 1)
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
                temp_score[1] = str(int(score[2]) + 1)
                new_score = "-".join(temp_score)
                csv_lines[i+1][j+1] = new_score
            else: # For non player list losses
                other_losses.append(op)
        
        if other_losses != []:
            csv_lines[i+1][len(players)+1] = ", ".join(other_losses)

    # Write csv
    writer = csv.writer(open(output,'w'))
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
    writer = csv.writer(open(output,'w',encoding='utf-8'))
    writer.writerows(csv_lines)

def to_csv_wl(players, input, output='win_loss.csv'):
    with open(input, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
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
            for op in data[player]['W']:
                # In order to get capitalization
                if op in players:
                    x = players.index(op)
                    real_op = players[x]
                else:
                    real_op = op
                
                if real_op in wins:
                    wins[real_op] += 1
                # elif real_op == "kürv": #The umlaut causes it to print the wrong letter wtf
                #     wins["Kurv"] = 1
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

            for op in data[player]['L']:
                # In order to get capitalization
                if op in players:
                    x = players.index(op)
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
            if (tp % 10 == 0):
                time.sleep(15)

            print("Player: " + p + ", i: " + str(i))
            tourneys = smash.player_show_tournaments_for_game(pids[p], p, 1, i)
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

    e_array = []
    for e in events:
        e_array.append(e)

    if (len(e_array) == len(set(e_array))):
        print("gamer moment")

    # Complete file output 
    with open(output, 'w', encoding='utf-8') as outfile:
        json.dump(events, outfile, indent=4)

def results_to_players(input):
    with open(input, 'r', encoding='utf-8') as json_file:
        full_year = json.load(json_file)
        for p in full_year:
            temp_name = str(p).split('/')[0].strip()

            fname = 'players/' + str(temp_name) + '.json'
            with open(fname, 'w') as outfile:
                json.dump(full_year[p], outfile, indent=4)

def main():
    # Initialize pysmashgg
    with open(".env", "r") as fp: # Would use .env but my computer hates it, feel free to use it
        key = fp.readline()

    smash = pysmashgg.SmashGG(key)

    # EU Work
    rcadia = 627868
    swt_eu = 554625
    myth = 457669
    kamp_kone = 570804
    poilson_col = 572809
    bagarre = 550396
    teaghlach = 545157
    super_bou = 550373
    fete = 549952
    sauna = 549684
    regen = 543662
    phoenix_blue = 554988
    upset = 550163
    valhalla = 541113
    # MISSION COMPLETE IS LIQUIPEDIA
    hflan = 428582
    endless = 627359
    forever3 = 592222
    hts7 = 607431
    hts8 = 622655
    # SMASHHOOD IS CHALLONGE
    hivemas2 = 648241
    
    eu_events = [rcadia, swt_eu, myth, kamp_kone, poilson_col, bagarre, teaghlach, 
                super_bou, fete, sauna, regen, phoenix_blue, upset, valhalla, hflan,
                endless, forever3, hts7, hts8, hivemas2]

    with open('EU.json', 'r') as json_file:
        eu_pids = json.load(json_file)

    # results_2021_ids(smash, eu_pids, eu_events, 'eu_results.json')

    with open('eu_results.json', 'r') as json_results:
        eu_results = json.load(json_results)
    eu_players = []
    for p in eu_results:
        eu_players.append(p)

    # results_2021_name(smash, eu_players, eu_events, 'eu_results_2.json')

    # to_csv_h2h_names(eu_players, 'eu_results.json', 'eu_h2h.csv')
    to_csv_wl(eu_players, 'eu_results.json', 'eu_wl.csv')
    

if __name__ == "__main__":
    main()
