import pickle
import random
import os
import json
from tqdm import tqdm
import argparse


MATCHING_TABLE = {"nigerian": "african", "south african": "african", "namibian": "african", "zimbabwean": "african", "ghanian": "african", "egyptian": "african", "kenyan": "african", "mauritian": "african", "ugandan": "african", "cameroonian": "african", "zambian": "african", "congolese": "african", "sierra leonean": "african", "sudanese": "african", "tanzanian": "african", "somali": "african", "malawian": "african", "gambian": "african", "british": "angloAmerican", "irish": "angloAmerican", "american": "angloAmerican", "australian": "angloAmerican", "canadian": "angloAmerican", "new zealander": "angloAmerican", "maltese": "angloAmerican", "british virgin islander": "angloAmerican", "chinese": "eastAsian", "malaysian": "eastAsian", "japanese": "eastAsian", "vietnamese": "eastAsian", "thai": "eastAsian", "korean": "eastAsian", "south korean": "eastAsian", "hong konger": "eastAsian", "taiwanese": "eastAsian", "indonesian": "eastAsian", "polish": "european", "romanian": "european", "italian": "european", "french": "european", "german": "european", "bulgarian": "european", "lithuanian": "european", "dutch": "european", "hungarian": "european", "greek": "european", "latvian": "european", "russian": "european", "belgian": "european", "ukrainian": "european", "slovak": "european", "czech": "european", "swiss": "european", "austrian": "european", "cypriot": "european", "albanian": "european", "estonian": "european", "croatian": "european", "slovenian": "european", "belarusian": "european", "serbian": "european", "moldovan": "european", "kosovan": "european", "filipino": "hispanic", "spanish": "hispanic", "portugese": "hispanic", "brazilian": "hispanic", "mexican": "hispanic", "colombian": "hispanic", "venezuelan": "hispanic", "argentine": "hispanic", "israeli": "Jewish", "pakistani": "arabic", "turkish": "arabic", "bangladeshi": "arabic", "iranian": "arabic", "afghan": "arabic", "iraqi": "arabic", "moroccan": "arabic", "syrian": "arabic", "lebanese": "arabic", "saudi arabian": "arabic", "algerian": "arabic", "jordanian": "arabic", "uzbek": "arabic", "libyan": "arabic", "kazakh": "arabic", "azerbaijani": "arabic", "luxembourger": "european", "georgian": "arabic", "kuwaiti": "arabic", "tunisian": "arabic", "sri lankan": "None", "jamaican": "None", "trinidadian": "None", "swedish": "scandinavian", "denmark": "scandinavian" , "danish": "scandinavian", "norwegian": "scandinavian", "finnish": "scandinavian", "icelandic": "scandinavian", "indian": "southAsian", "singaporean": "southAsian", "nepalese": "southAsian"}


def get_matrix_from_name(name: str, abc_dict: list):
    matrix = []
    for letter in name:
        matrix.append(abc_dict[letter])
    return matrix

def get_name_from_matrix(matrix: list, abc_list: list):
    name = ""
    for letter in matrix:
        index = letter
        letter = abc_list[index]
        name += letter
    return name

def handle_clusters(nationality: str, dict_clusters: dict):
    for key in dict_clusters:
        if nationality in dict_clusters[key]:
            return key
    return "other"

def max_per_cluster(cluster_dict: dict, amount_names_country: dict):
    max_per_cluster = {}
    for key in cluster_dict:

        smallest = 1e10
        for country in cluster_dict[key]:

            if country in amount_names_country:
                if amount_names_country[country] <= smallest:
                    smallest = amount_names_country[country]

        for country in cluster_dict[key]:
            max_per_cluster[country] = smallest

    return max_per_cluster


def preprocess_groups(job_id: str="", groups: str="", raw_dataset_path: str=""):
    # load raw dataset
    with open(raw_dataset_path, "rb") as o:
        dict_chosen_names = pickle.load(o)

    # set lower limit of names per country if wanted
    minimum_per_country = 1

    # abc_dict is a dictionary where the letters "a"-"z" and " " and "-" are keys to lists representing these values in the matrix_name_list
    abc_dict = {}
    abc_list = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"," ","-"]
    a = list(range(len(abc_list)))
    for i in range(len(abc_list)):
        abc_dict[abc_list[i]] = a[i]

    # create nationality selection dictionary
    all_nationalities = ['british', 'indian', 'american', 'german', 'polish', 'pakistani', 'italian', 'romanian', 'french', 'chinese', 'irish', 'japanese', 'spanish', 'filipino', 'dutch', 'nigerian', 'south korean', 'taiwanese', 'hong konger','korean', 'swiss', 'danish', 'austrian','belgian', 'luxembourger', 'portugese',
                        'norwegian', 'swedish', 'finnish', 'icelandic', 'denmark', 'lithuanian', 'estonian', 'latvian', 'hungarian', 'bulgarian', 'czech', 'albanian', 'slovak', 'slovenian', 'algerian', 'croatian', 'serbian', 'macedonian', 'georgian', 'citizen of bosnia and herzegovina', 'kosovan', 'belarusian',
                        'cypriot', 'greek', 'russian', 'ukrainian', 'uzbek', 'moldovan', 'turkmen','kazakh','kyrgyz', 'australian',
                        'nepalese', 'sri lankan', 'singaporean','bangladeshi', 'malaysian', 'fijian', 'thai', 'indonesian', 'burmese', 'vietnamese',
                        'turkish', 'iraqi', 'iranian', 'israeli', 'yemeni', 'syrian', 'afghan', 'palestinian', 'kuwaiti', 'armenian', 'bahraini', 'lebanese', 'saudi arabian', 'azerbaijani', 'emirati','omani','qatari','jordanian','maltese',
                        'egyptian', 'moroccan', 'tunisian','libyan', 'cameroonian', 'ghanian', 'ugandan', 'nigerien', 'kenyan', 'gambian', 'ivorian', 'senegalese', 'eritrean', 'sierra leonean', 'congolese', 'somali', 'sudanese', 'ethiopian','angolan',
                        'zimbabwean', 'south african', 'zambian', 'mauritian', 'malawian', 'tanzanian', 'botswanan', 'namibian','citizen of seychelles',
                        'canadian', 'new zealander','mexican', 'dominican', 'trinidadian', 'barbadian', 'kittitian', 'st lucian','jamaican','british virgin islander', 'costa rican','grenadian','panamanian', 'cuban',
                        'brazilian', 'colombian', 'argentinian', 'peruvian', 'venezuelan', 'ecuadorean','chilean', 'guyanese','bolivian','uruguayan']

    nationalities = []
    for nationality in all_nationalities:
        if nationality in MATCHING_TABLE and MATCHING_TABLE[nationality] in groups:
            nationalities.append(nationality)

    if "else" in groups:
        nationalities.append("else")

    chosen_nationalities = []
    available_nationalities = all_nationalities.copy()
    for nationality in nationalities:
        if nationality == "else":
            continue

        chosen_nationalities.append(nationality)
        available_nationalities.pop(available_nationalities.index(nationality))
    
    if "else" in nationalities:
        chosen_nationalities.append("else")
        else_ = available_nationalities
    else:
        else_ = []
    
    group_names = [[] for _ in range(len(groups))]

    for country in dict_chosen_names:
        if country in MATCHING_TABLE and MATCHING_TABLE[country] in groups:
            group = MATCHING_TABLE[country]
        elif country in else_:
            group = "else"
        else:
            print(country)

        class_ = groups.index(group)
        for name in dict_chosen_names[country]:
            try:
                name = name.lower()

                # remove "dr", "ms", "mr", "mrs"
                if name.split(" ")[0] == "dr" or name.split(" ")[0] == "mr" or name.split(" ")[0] == "ms" or name.split(" ")[0] == "miss" or name.split(" ")[0] == "mrs":
                    space_idx = name.strip().index(" ")
                    name = name[space_idx:]

                # remove random spaces before name
                if list(name)[0] == " ":
                    name = name[1:]

                name = name.strip()
                int_name = get_matrix_from_name(name, abc_dict)
                group_names[class_].append([class_ + 1, int_name])
            except Exception as e:
                pass

    maximum_names = len(group_names[0])
    for idx, group in enumerate(group_names[1:]):
        if len(group) < maximum_names:
            maximum_names = len(group)

    dataset = []
    for group in group_names:
        names = group.copy()
        random.shuffle(names)
        dataset += names[:maximum_names]
        
    random.shuffle(dataset)

    dataset_path = "nec_user_models/" + job_id + "/dataset"
    if not os.path.exists(dataset_path):
        os.mkdir(dataset_path)

    with open(dataset_path + "/dataset.pickle", "wb+") as o:
        pickle.dump(dataset, o, pickle.HIGHEST_PROTOCOL)

    classes = {k: v for v, k in enumerate(groups)}

    filepath = dataset_path + "/nationalities.json"
    with open(filepath, 'w+') as f:
        json.dump(classes, f, indent=4)


# preprocess(job_id="10_nationalities_and_else", groups=["african", "eastAsian", "european", "arabic", "angloAmerican", "hispanic", "scandinavian", "southAsian"], raw_dataset_path="dataset/total_names_dataset.pickle")

