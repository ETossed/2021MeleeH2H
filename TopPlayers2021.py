import pysmashgg
import json
import time
import csv

def results_2021(smash, players, events, output):
    # Initialization of Players
    players_lower = []
    for p in players:
        players_lower.append(p.lower())
    player_dict = {}
    for p in players_lower:
        player_dict[p] = {'W': [], 'L': []}

    # Testing
    # test = smash.tournament_show_events('smash-summit-12-1')
    # print(json.dumps(test, indent=4))
    # sets = smash.event_show_sets(summit_vip,1)
    # print(sets)

    # Main Loop
    event_num = 0
    for event in events:
        print(smash.tournament_show(event))
        event_num += 1
        i = 1
        sets = smash.event_show_sets(event, i)
        while (sets != []):
            # Iterate through pages
            sets = smash.event_show_sets(event, i)
            i += 1
            if (i == 0 or i % 5 == 0):
                time.sleep(15) # Might be able to remove, but idk, just not to time out API
            for set in sets:
                print(json.dumps(set, indent=4))
                print("\n")
                # Get entrants
                entrant1 = set['entrant1Players'][0]['playerTag'].split(' | ')[-1].strip().lower()
                entrant2 = set['entrant2Players'][0]['playerTag'].split(' | ')[-1].strip().lower()

                # Make sure entrants work]
                if (entrant1 == None and entrant2 == None):
                    continue
                elif (entrant1 in players_lower and entrant2 in players_lower and set['completed'] == True):
                    if (set['entrant1Score'] < 0 or set['entrant2Score'] < 0):
                        continue
                    elif (set['entrant1Score'] > set['entrant2Score']):
                        player_dict[entrant1]['W'].append(entrant2)
                        player_dict[entrant2]['L'].append(entrant1)

                    elif (set['entrant2Score'] > set['entrant1Score']):
                        player_dict[entrant2]['W'].append(entrant1)
                        player_dict[entrant1]['L'].append(entrant2)

        # Error checking
        if (i == 1):
            print("Error: Tournament didn't load")

    # Complete file output 
    with open(output, 'w') as outfile:
        json.dump(player_dict, outfile, indent=4)

def add_to_results(smash, event):
    return

def to_csv_matchups(input, output='data.csv'):
    # Read json file
    with open(input, 'r') as json_file:
        data = json.load(json_file)
    
    i = 0
    player_list = []
    with open(output, 'w') as new_file:
        # Top left corner
        new_file.write('ETossed,')

        # Header row
        for player in data:
            # Making sure player has played matches
            if (data[player]['W'] != [] or data[player]['L'] != []):
                player_list.append(player)
                new_file.write(player + ',')

        # Newline after header        
        new_file.write('\n')
        
        # Setup rows
        for player in player_list:
            new_file.write(player + ',')
            for j in range(len(player_list)):
                if (i == j):
                    new_file.write('N/A,')
                else:
                    new_file.write('0-0,')

            # Increment i and write newline
            new_file.write('\n')
            i += 1

    # Open csv file
    csv_file = csv.reader(open(output))
    csv_lines = list(csv_file)

    # For each w/l find index in player_list
    for i in range(len(player_list)):
        cur_player = data[player_list[i]]
        wins = cur_player['W']
        losses = cur_player['L']
        for op in wins:
            # Access cell through csv built in python functions
            j = player_list.index(op)
            score = csv_lines[i+1][j+1]
            print("i+1: " + str(i+1) + ", j+1: " + str(j+1))

            # Split cell by '-' character and modify score
            temp_score = score.split('-')
            temp_score[0] = str(int(score[0]) + 1)
            new_score = "-".join(temp_score)
            csv_lines[i+1][j+1] = new_score

        for op in losses:
            # Access cell through csv built in python functions
            j = player_list.index(op)
            score = csv_lines[i+1][j+1]
            print("i+1: " + str(i+1) + ", j+1: " + str(j+1))

            # Split cell by '-' character and modify score
            temp_score = score.split('-')
            temp_score[1] = str(int(score[2]) + 1)
            new_score = "-".join(temp_score)
            csv_lines[i+1][j+1] = new_score

    # Write csv
    writer = csv.writer(open(output,'w'))
    writer.writerows(csv_lines)

def to_csv_big(input, output='data_big.csv'):
    with open(input, 'r') as json_file:
        data = json.load(json_file)
    
    with open(output, 'w') as new_file:
        # Top left corner
        new_file.write('ETossed,')

        # Header row
        new_file.write('Wins,Losses\n')

        for player in data:
            # Making sure player has played matches
            if (data[player]['W'] != [] or data[player]['L'] != []):
                # Initialization
                wins = {}
                losses = {}

                new_file.write(player + ',\"') # Initial quote
                for op in data[player]['W']:
                    # If already in wins
                    if op in wins:
                        wins[op] += 1
                    elif op == "kürv": #The umlaut causes it to print the wrong letter wtf
                        wins["kurv"] = 1
                    else:
                        wins[op] = 1
                
                # Adding wins to column
                for w in sorted(wins):
                    if wins[w] == 1:
                        new_file.write(w + ",")
                    else:
                        new_file.write(w + "(x" + str(wins[w]) + "),")

                # Closing quote and new quote
                new_file.write('\",\"')

                for op in data[player]['L']:
                    # If already in lossses
                    if op in losses:
                        losses[op] += 1
                    elif op == "kürv": #The umlaut causes it to print the wrong letter wtf
                        losses["kurv"] = 1 # Kurv only has singular losses, this can be fixed later
                    else:
                        losses[op] = 1
                
                # Adding wins to column
                for l in sorted(losses):
                    if losses[l] == 1:
                        new_file.write(l + ",")
                    else:
                        new_file.write(l + "(x" + str(losses[l]) + "),")

                # Closing quote
                new_file.write('\",')

                # Print newline
                new_file.write('\n')

def main():
    # Initialize pysmashgg
    with open(".env", "r") as fp: # Would use .env but my computer hates it, feel free to use it
        key = fp.readline()
    smash = pysmashgg.SmashGG(key)
    
    # Needs to be their smashgg names
    players = ['2saint', 'Aklo', 'Albert', 'aMSa', 'Android 0', 'Aura', 'Axe', 'Ben', 'billybopeep', 
                'bobby big ballz', 'Bones', 'Captain Smuckers', 'Chem', 'Colbol', 'Dacky', 'Drephen',
                'Eddy Mexico', 'Eggy', 'Faceroll', 'Far!', 'FatGoku', 'Fiction', 'Fizz', 'Flash',
                'Free Palestine', 'Frenzy', 'Gahtzu', 'Ginger', 'Hungrybox', 'iBDW', 'Ice', 'Jah Ridin\'', 
                'Jflex', 'Jmook', 'Juicebox', 'Justus', 'Kalamazhu', 'Kalvar', 'Khryke', 'KJH',
                'KoDoRiN', 'Krudo', 'Kürv', 'Leffen', 'lloD', 'Logan', 'Lucky', 'Luigi Ka-Master', 'Magi', 
                'Mang0', 'Medz', 'Mekk', 'Mew2King', 'Michael', 'moky', 'Morsecode762', 'Mot$', 'n0ne/ Bond / wizzyfan109',
                'Nicki', 'NoFluxes', 'null', 'Nut', 'Palpa', 'Panda', 'Pappi', 'Pipsqueak', 'Plup', 'Polish',
                'Professor Pro', 'Ringler', 'Rishi', 'Rocky', 'Ryobeat', 'S2J', 'SDJ', 'Secrets',
                'SFAT', 'SFOP', 'Shroomed', 'Skerzo', 'Slowking', 'SluG', 'Smashdaddy', 'Sock',
                'Sora/Joshman', 'Spark', 'Swift', 'Tai', 'TheSWOOPER', 'Trif', 'Wally', 
                'Warmmer', 'Wizzrobe', 'Zain', 'Zamu', 'Zealot', 'Zuppy']

    # Event IDs can be found by using smash.tournament_show_events('tournament-smashgg-name')
    # Example: smash.tournament_show_events('riptide-2021')
    # Supermajors
    summit_11 = 596002
    summit_12 = 635845

    # Majors
    swt_main = 644621
    riptide = 573828
    mainstage = 584741 # DOESN'T WORK, ADDED MANUALLY
    swt_east = 554630

    # Regionals
    swt_lcq = 633485 # BREAKS IT, ADDED MANUALLY
    ltc = 585641
    htl6 = 598932
    ctg4 = 438347
    function = 623950
    pinnacle = 596731
    ssc = 605856
    swt_west = 554629
    swt_eu = 554625
    hflan = 428582
    summit_vip = 657283

    # Smaller Regionals/Superlocals
    the_grail = 596528
    returnament = 582685
    tp_109 = 606697
    toms = 593246
    homecoming = 611389
    the_trail_inv = 610808
    myth = 457669
    super_verdugo = 644033
    super_meat = 644491

    # List of melee singles events
    events = [summit_11, summit_12, swt_main, riptide, mainstage, ltc, htl6, ctg4, function,
                pinnacle, ssc, swt_west, swt_east, swt_eu, hflan, summit_vip, the_grail,
                returnament, tp_109, toms, homecoming, the_trail_inv, myth, super_verdugo, 
                super_meat]

    summits = [summit_11, summit_12]

    # results_2021(smash, players, events, 'results.json')
    to_csv_matchups('results.json')
    print("Done")

if __name__ == "__main__":
    main()