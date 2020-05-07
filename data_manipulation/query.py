'''
Author:        Eda
Last modified: 5.07.2020 by ez
Status:        In progress

Given a query (of the format below), returns ranked results (activities)

Query must be in the form ["location", "adjective1", "adjective2", ...]
    - The adjectives are the MAIN adjectives and their synonyms will be obtained
    from the ../scrapers/adjectives_extended.txt file
    - Example: ["BostonMA", "frugal", "foodie", "creative"]
'''
import json

# limit specifies what number of the top results should be returned
# -1 (default) indicates to return ALL results that match query
def get_activities(query, limit=-1):
    # ---- Get expanded adjectives list ---- #
    with open('../scrapers/adjectives_extended.txt', 'r') as a:
        # get adjs in 2d list (adjs[n][0] are the main adjectives)
        all_adjs = [line.rstrip('\n').split(', ') for line in a.readlines()]

    q_adjs = query[1:]
    adjs = [] # the expanded list of adjectives (includes synonyms)
    for a in all_adjs:
        if a[0] in q_adjs:
            adjs.append(a)

    # ---- Get activities at location ---- #
    q_loc = query[0]
    with open('../data/Merged/{0}.json'.format(q_loc), 'r') as d:
        all_loc_act_data = json.load(d) # activities at that location

    loc_act_names = [entry['name'] for entry in all_loc_act_data]

    # ---- Use inverted index to get activity names that match adjectives and location ---- #
    # TODO: what if activities at different locations have the same name... how to differentiate
    with open('../data/InvertedIndex/inverted_index.json', 'r') as i:
        index = json.load(i)

    act_names = []
    for row in adjs:
        for adj in row:
            act_names += index[adj]
    # only keep activities that are in the location
    # TODO: not very efficient... :(
    act_names = (set(act_names) & set(loc_act_names))

    # ---- Get activity data for names ---- #
    act_data = []
    for entry in all_loc_act_data:
        if entry['name'] in act_names:
            act_data.append(entry)

    ranked = rank(act_data, adjs)
    if limit != -1:
        ranked = ranked[:limit]
    return ranked

# Given a list of activity data (dictionaries) and 2d list of adjectives
# (each row is an adjective and its synonyms, adjs[n][0] is the main adjective),
# ranks them and returns list of dictionaries
# Rank is calculated by: 1 pt for occurrence of main adj, .5 for occurrence of secondary adj
# TODO: Incorporate user rating??
# TODO?: Not normalizing anymore but I think that's ok? Not sure what the 'max' would be since number of reviews differs and isn't passed from merged
def rank(act_data, adjs):
    scores = [] # list of pairs: (score, activity)
    primary_adjs = []
    secondary_adjs = []

    # get primary and secondary adjectives (there's probably a pythonic way to do this in one line but...)
    for row in adjs:
        primary_adjs.append(row[0])
        if len(row) > 1:
            secondary_adjs.extend(row[1:])

    # get scores for each activity
    for entry in act_data:
        rank_score = 0
        tags = entry['tags']

        for p_a in primary_adjs:
            rank_score += tags.count(p_a)
        for s_a in secondary_adjs:
            rank_score += (tags.count(s_a) / 2)

        scores.append((rank_score, entry))

    # rank the scores largest to smallest
    scores.sort(key=lambda pair: pair[0], reverse=True)

    # return just the activity data
    ranked_act = [pair[1] for pair in scores]
    return ranked_act

def main(): # this is just for testing :)
    query = ["BostonMA", "frugal", "foodie", "creative"]
    results = get_activities(query, 2)
    print(results)
    return

if __name__ == '__main__':
    main()