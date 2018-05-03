import time
import sys
import json
import collections

dictionary = dict()
transition_probability = collections.defaultdict(dict)
emission_probability = collections.defaultdict(dict)
starting_tag_list = []
entire_tag_list = []
entire_word_list = []
starting_tag_count = dict()
total_tag_dict = dict()
sentence_contents = []
sentence_words = []
transition_tag_list = []
transition_tag_count = dict()

starting_count = dict()
f = open(sys.argv[1], 'r', encoding="utf-8")


def parse_input():
    i = 1
    f = open(sys.argv[1], 'r', encoding="utf-8")
    for sentence in f:
        wordtags = sentence.split()
        for tags in wordtags:
            # print(tags)
            tags = list(tags)
            pair = "".join(tags).rsplit('/', 1)
            word = pair[0]
            tag = pair[1]
            starting_tag_list.append(tag)
            break

    # calculate denominator for transition probabilities.
    f = open(sys.argv[1], 'r', encoding="utf-8")
    i = 0
    for sentence in f:
        i = 0
        wordtags = sentence.split()
        n = len(wordtags)
        for tags in wordtags:
            tags = list(tags)
            pair = "".join(tags).rsplit('/', 1)
            word = pair[0]
            tag = pair[1]
            if (i != n - 1):
                transition_tag_list.append(tag)
            if (i == 0):
                transition_tag_list.append(tag)
            i += 1

    for every_tag in transition_tag_list:
        if every_tag in transition_tag_count:
            transition_tag_count[every_tag] += 1
        else:
            transition_tag_count[every_tag] = 1

    transition_probability["start"] = {}

    count_start = 0

    for el in starting_tag_list:
        count_start = 0
        # print(el)
        if el in transition_probability["start"]:
            transition_probability["start"][el] += 1
        else:
            count_start = 1
            transition_probability["start"][el] = 1

    ################################################### ADD ONE SMOOTHING FOR START STATE ##########################################

    for tag1 in transition_tag_count:
        # print(tag1)
        if (tag1 not in transition_probability["start"]):

            transition_probability["start"][tag1] = float(
                0.7 / (5 * len(transition_tag_count) + len(starting_tag_list)))

        else:
            transition_probability["start"][tag1] = float(0.7 + transition_probability["start"][tag1]) / (
            5 * len(transition_tag_count) + len(starting_tag_list))

    return starting_tag_list

    # calculate  transition probabilities.
    # calculate q0 state probabilities


def compute_transition_prob(starting_tag_list):
    entire_tag_list = []
    entire_word_list = []
    for starting_tags in starting_tag_list:
        if (starting_tags in starting_tag_count):
            starting_tag_count[starting_tags] += 1
        else:
            starting_tag_count[starting_tags] = 1
    # print(starting_tag_count)

    # checking if all have been parsed correctly.
    total_count = 0
    for el in starting_tag_count:
        total_count += starting_tag_count[el]
    # for every tag, compute the number of times it transitions to the immediately following tag.
    f = open(sys.argv[1], 'r', encoding="utf-8")

    # getting all the tags.
    tag_list = []
    for sentence in f:
        wordtags = sentence.split()
        # print(wordtags)
        # exit()
        for tags in wordtags:
            tags = list(tags)
            pair = "".join(tags).rsplit('/', 1)
            word = pair[0]
            tag = pair[1]
            entire_tag_list.append(tag)
            entire_word_list.append(word)
   
    # total unique tags in file.
    for every_tag in entire_tag_list:
        if (every_tag in total_tag_dict):
            total_tag_dict[every_tag] += 1
        else:
            total_tag_dict[every_tag] = 1



    f = open(sys.argv[1], 'r', encoding="utf-8")
    # getting tags for each sentence.
    tag_list = []
    sentence_tags = []
    sentence_words = []
    for sentence in f:
        wordtags = sentence.split()
        # print(wordtags)
        entire_tag_list = []
        entire_word_list = []
        for tags in wordtags:
            tags = list(tags)
            pair = "".join(tags).rsplit('/', 1)
            word = pair[0]
            tag = pair[1]
            entire_tag_list.append(tag)
            entire_word_list.append(word)
        sentence_tags.append(entire_tag_list)
        sentence_words.append(entire_word_list)

    # get the transition probabilities.
    i = 0
    j = 0
    k = 0
    indices = []
    for every_tag in total_tag_dict:
        transition_probability[every_tag] = {}
        for i, tag_list in enumerate(sentence_tags):
            k = 0
            for k, tags in enumerate(tag_list):
                if (tags == every_tag):
                    index = k
                    n = len(tag_list)
                    if (index < n - 1):
                        next_tag = tag_list[index + 1]
                        if (next_tag in transition_probability[every_tag]):

                            transition_probability[every_tag][next_tag] += 1
                        else:
                            trans_count = 1
                            transition_probability[every_tag][next_tag] = 1

    ########################################################ADD ONE SMOOTHING.
    for tag1 in transition_tag_count:
        for tag2 in transition_tag_count:
            # print(tag1)
            if (tag2 not in transition_probability[tag1]):

                transition_probability[tag1][tag2] = float(
                    0.7 / (5 * len(transition_tag_count) + transition_tag_count[tag1]))

            else:
                transition_probability[tag1][tag2] = float(0.7 + transition_probability[tag1][tag2]) / (
                5 * len(transition_tag_count) + transition_tag_count[tag1])

    # Calculating Last Transitions.
    last_transition = []
    for tag_list in sentence_tags:
        i = 0
        for s in tag_list:
            n = len(tag_list)
            if (i == n - 1):
                last_transition.append(s)
                # rint(last_transition)
            i += 1

    stop_count = 0
    transition_probability["stop"] = {}
    for el in last_transition:
        if el in transition_probability["stop"]:
            transition_probability["stop"][el] += 1
        else:
            transition_probability["stop"][el] = 1

    for tag1 in transition_tag_count:
        if (tag1 not in transition_probability["stop"]):

            transition_probability["stop"][tag1] = float(0.7 / (5 * len(transition_tag_count) + len(last_transition)))

        else:
            transition_probability["stop"][tag1] = float(0.7 + transition_probability["stop"][tag1]) / (
                5 * len(transition_tag_count) + len(last_transition))

    ct = 0
    for el in transition_probability:
        for f in transition_probability[el]:
            ct += 1

    transition_count = 0
    for tag in transition_probability:
        for el in transition_probability[tag]:
            transition_count += 1
    return sentence_words, sentence_tags


def compute_emission_prob(sentence_words, sentence_tags):
    # probability of a sentence with a particular tag/ total number of tags.
   # print("Computing Emission Probabilites!")
    last_transition = []

    #print("********** EMISSION PROBABILITES ***********")

    sentence_dict = dict()

    emission_probability[""] = {}
    f = open(sys.argv[1], 'r', encoding="utf-8")
    emission_count = 0
    for sentence in f:
        wordtags = sentence.split()
        for tags in wordtags:
            tags = list(tags)
            pair = "".join(tags).rsplit('/', 1)
            word = pair[0]
            tag = pair[1]

            if (tag in emission_probability[word]):
                emission_count = emission_probability[word][tag] * total_tag_dict[tag]

                emission_probability[word][tag] = float((emission_count + 1) / total_tag_dict[tag])
                # print(emission_probability)
            else:
                emission_count = 0
                emission_probability[word][tag] = float(1 / total_tag_dict[tag])

    cnt = 0
    for el in emission_probability:
        for i in emission_probability[el]:
            cnt += 1
    # print(cnt)
    return emission_probability


def write(emission_probability):  # write to json file.
    joint_probability = {"transition": transition_probability, "emission": emission_probability,
                         "uniquetags": transition_tag_count}
    # print(transition_probability)
    with open("hmmmodel.txt", 'w') as outfile:
        json.dump(joint_probability, outfile, indent=4)


start_time = time.time()

if __name__ == '__main__':
    starting_tag_list = parse_input()
    word_list, tag_list = compute_transition_prob(starting_tag_list)
    emission_probability = compute_emission_prob(word_list, tag_list)
    write(emission_probability)