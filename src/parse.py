import json
import os 

def load_json_to_dict(filename):
    with open(filename) as f:
        dict = json.load(f)
        return dict
def load_location_names(filename):
    with open(filename) as f:
        return f.read().split(";")
def get_all_names(dictionary, field_name="Additional Names"):
    names_dictionary = {}
    for key,value in dictionary.items():
        additional_names = [value["Name"]]

        if field_name in value:
            additional_names.extend(value[field_name].split(";"))

        for name in additional_names:
            name = name.lower()
            if name == "":
                continue
            if name in names_dictionary:
                # raise RuntimeError(f"Name {name} repeats itself in {names_dictionary[name]} and {key}")
                # prioritize targets over weapon
                if value["ObjectType"] == "Weapons":
                    continue
            names_dictionary[name] = key
    return names_dictionary

# this is inconsistent with other functions, add husk tag in json data later to make consistent
def get_husk_names(names_dictionary):
    husk_names_dict = {}
    for key, value in names_dictionary.items():
        if "husk" in key.lower():
            husk_names_dict[key] = value
            husk_names_dict[key.replace('husk', '')] = value
    return husk_names_dict

def get_vehicle_names(dictionary, field_name="Additional Names"):
    names_dictionary = {}
    for key,value in dictionary.items():
        if value["ObjectType"] != "Vehicles":
            continue
        additional_names = [value["Name"]]

        if field_name in value:
            additional_names.extend(value[field_name].split(";"))

        for name in additional_names:
            name = name.lower()
            if name == "" or name in names_dictionary:
                continue
            names_dictionary[name] = key
    return names_dictionary

def get_bunker_spec(string):
    # size <number> tier <1/2/3> bunker with <numer> <modification>, <numer> <modification>, ...
    args = {}
    tier_words = {"t1":1,"t2":2,"t3":3,"tier 1":1, "tier 2":2,"tier 3":3,"concrete":3}
    mod_words = {"atg": "atg", "at": "atg", "rg": "rg", "rifle": "rg", "hg": "hg", "howi":"hg", "howie":"hg",
                 "mg":"mg", "machinegun":"mg", "machine":"mg", "mgg":"mg", "ammunition":"ammo", "ramp":"ramp",
                  "howitzer":"hg", "engine":"eng", "sc":"sc", "storm cannon":"sc", "ic":"ic", "intel":"ic",
                  "intelligence":"ic", "base":"core", "core":"core", "storage":"ammo", "ammo":"ammo",
                  "obs":"obs", "observation":"obs", "gen":"eng", "generator":"eng", "generater":"eng"}
    words = string.lower().replace(",", " ").split()
    if "size" in words:
        if words[words.index("size")+1].isdigit():
            args["size"] = int(words[words.index("size")+1])
        elif words.index("size")-1 > 0 and words[words.index("size")-1].isdigit():
            args["size"] = int(words[words.index("size")-1])
        else:
            return None
    else:
        return None


    for keyword in tier_words:
        if keyword in words:
            args["tier"] = tier_words[keyword]
            break
    else:
        return None
    
    # slice so only <number> <modification> pairs remain
    if "with" in words:
        words = words[words.index("with"):]
    else:
        words = words[words.index("size"):]

    mod_count = 0
    
    for i, word in enumerate(words):
        if word in mod_words:
            if word == "bunker" and i+1 < len(word) and words[i+1] in mod_words:
                # catch phrases like "bunker ramp"
                word = words[i+1]
            if i-1 >= 0 and words[i-1].isdigit():
                args[mod_words[word]] = int(words[i-1])
                mod_count += int(words[i-1])
    if mod_count > args["size"]:
        return None
    return args


# Structure Json parser
location_names = load_location_names(os.path.join("data", "Location_names.json"))

def check_if_location_name(name):
    return name in location_names

targets = load_json_to_dict(os.path.join("data", "Targets.json"))
damages = load_json_to_dict(os.path.join("data", "Damage.json"))
weapons = load_json_to_dict(os.path.join("data", "Weapons.json"))
all = weapons | targets
dump = load_json_to_dict(os.path.join("data", "dump.json"))
bunker_stats = load_json_to_dict(os.path.join("data", "Bunker_piece.json"))


targets_dictionary = get_all_names(targets)
husk_dictionary = get_husk_names(targets_dictionary)
vehicle_dictionary = get_vehicle_names(targets)
weapons_dictionary = get_all_names(weapons)
all_dictionary = get_all_names(all)

print("Cool")
#slang