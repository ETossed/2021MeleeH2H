import json
import pysmashgg
import os
from time import sleep

smash = pysmashgg.SmashGG('1d8515d23c643ea751677ce298f62d0c')

# with open('D:\\git\\2021Melee\\Ultimate\\Ultimate_Results_2021.json', 'r', encoding='utf-8') as tempfile:
#     results_ultimate = json.load(tempfile)

with open('Events_Thru_March.json', 'r', encoding='utf-8') as tempfile:
    mpp = json.load(tempfile)

# # Checking individual players
# temp_player_list = ppr_2021['South Korea']['Players_list']
# for p in results_ultimate:
#     if results_ultimate[p]['Tag'] in temp_player_list:
#         if 'Snake' in results_ultimate[p]['Chars_used']:
#             print(results_ultimate[p]['Tag'] + ' - ' + str(results_ultimate[p]['Chars_used']['South Korea']))

# arr = ["dummy", "Bowser", "Captain Falcon", "Donkey Kong", "Dr. Mario", "Falco", "Fox", "Ganondorf", "Ice Climbers", "Jigglypuff", "Kirby", "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Mr. Game and Watch", "Ness", "Peach", "Pichu", "Pikachu", "Roy", "Samus", "Sheik", "Yoshi", "Young Link", "Zelda", "Random", "Shielda"]

matchup_dict = {}
for p in mpp:
    cur_tag = mpp[p]['Tag']
    new_op_dict = {}
    for opp in mpp[p]['Opponents']:
        opp_tag = mpp[opp]['Tag']
        matchup_str = ""
        if (cur_tag < opp_tag):
            matchup_str = cur_tag + '-' + opp_tag
        else:
            matchup_str = opp_tag + '-' + cur_tag
        
        if matchup_str in matchup_dict:
            matchup_dict[matchup_str] += mpp[p]['Opponents'][opp]
        else:
            matchup_dict[matchup_str] = mpp[p]['Opponents'][opp]

for m in matchup_dict:
    matchup_dict[m] = int(matchup_dict[m]/2)

matchup_dict = dict(sorted(matchup_dict.items(), key=lambda item: item[1], reverse=True))

with open('Most_Common_Matchups_Mar_22.json', 'w+', encoding='utf-8') as json_file:
    json.dump(matchup_dict, json_file, indent=4)


# for p in results_ultimate:
#     new_char_dict = {}
#     char_arr = []
#     for char in results_ultimate[p]['Chars_used']:
#         char_arr.append(int(char))

#     char_arr = sorted(char_arr)
#     for c in char_arr:
#         new_char_dict[ultimate_chars[c]] = results_ultimate[p]['Chars_used'][str(c)]

#     results_ultimate[p]['Chars_used'] = new_char_dict

# with open('D:\\git\\2021Melee\\Ultimate\\Ultimate_Results_2021.json', 'w+', encoding='utf-8') as tempfile:
#     json.dump(results_ultimate, tempfile, indent=4)

# # PLAYER REGION STUFF
# if (os.path.isfile('temp_location_project.json')):
#     print('temp_location_project.json found, initializing from file')
#     with open('temp_location_project.json', 'r') as tempfile:
#         player_location_dict = json.load(tempfile)
#     i = len(player_location_dict)
# else:
#     i = 1
#     with open('D:\git\\2021Melee\Players_by_Region\Player_Locations_2021_Full_Year.json', 'r', encoding='utf-8') as tempfile:
#         player_location_dict = json.load(tempfile)

# for id in results_ultimate:
#     if i % 25 == 0:
#         print("Sleeping, i: " + str(i))
#         sleep(15)
#         i += 1
    
#     print("Player: " + results_ultimate[id]['Tag'] + ', ID: ' + str(id))
#     if id in player_location_dict:
#         continue
#     else:
#         i += 1
#         player_info = smash.player_show_info(id)

#         player_location_dict[id] = {'Tag': results_ultimate[id]['Tag']}

#         if player_info is not None:
#             if 'country' in player_info:
#                 player_location_dict[id]['Country'] = player_info['country']

#             if 'state' in player_info:
#                 player_location_dict[id]['State'] = player_info['state']

#             if 'city' in player_info:
#                 player_location_dict[id]['City'] = player_info['city']
#         else:
#             player_location_dict[id]['Tag'] = None
#             player_location_dict[id]['Country'] = None
#             player_location_dict[id]['State'] = None

#         # Failsafe Portion
#         with open('temp_location_project.json', 'w+', encoding='utf-8') as outfile:
#             json.dump(player_location_dict, outfile, indent=4)

# print(i)
# with open('Ultimate_Player_Locations_2021.json', 'w+', encoding='utf-8') as outfile:
#     json.dump(player_location_dict, outfile, indent=4)
