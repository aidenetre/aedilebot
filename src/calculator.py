import math
import parse
import utils
import fuzzy as fuzz
import main
import bot

def calculate_damage(weapon, target):
    mitigation_type = target['Mitigation Type']
    damage_type = weapon['DamageType']
    return calculate_damage_inner(weapon["Damage"],damage_type, mitigation_type)

def calculate_damage_inner(damage, damage_type, mitigation_type):
    mitigation_type_damage = parse.damages[damage_type]
    mitigation_value = mitigation_type_damage[mitigation_type]
    real_damage = float(float(damage) * float((1 - float(mitigation_value))))
    return math.ceil(real_damage)

#Arguments are health and damage, returns amount of hits to kill vehicle
def calculate_hits_to_kill(health, damage):
    return math.ceil(float(health) / damage)

def calculate_hits_to_disable(health_to_disable, damage):
    return math.ceil(float(health_to_disable) / damage)

# Arguments are correct weapon and target names
# Function currently returns dictionary with all the useful data possible. Good idea would be to make it a class
def damage_calculator(weapon_name, target_name):
    weapon = parse.weapons[weapon_name]
    target = parse.targets[target_name]
    object_type = target["ObjectType"]
    if object_type == "Vehicles":
        return general_damage_calculator(weapon, target)  #vehicle_damage_calculator()
    elif object_type == "Multitier_structures":
        return multitier_damage_calculator(weapon, target)
    elif object_type == "Emplacements":
        return general_damage_calculator(weapon, target) #emplacement_damage_calculator()
    elif object_type == "Tripods" or object_type == "Structures":
        return general_damage_calculator(weapon, target)
    else:
        raise bot.InvalidTypeError(target_name, "There was an unexpected error trying to find the entity. Please contact the developers.")


    

def general_damage_calculator(weapon, target):
    weapon_name = weapon["Name"]
    target_name = target["Name"]
    final_damage = calculate_damage(weapon, target)
    hits_to_kill = calculate_hits_to_kill(target["Health"], final_damage)
    utils.debug_summary(weapon_name,target_name,final_damage, hits_to_kill)
    data = {"htk": hits_to_kill, "final_damage": final_damage}
    return f"It takes {data['htk']} {weapon_name} to kill a {target_name}"

def multitier_damage_calculator(weapon, target):
    weapon_name = weapon["Name"]
    target_name = target["Name"]
    location_name = "placeholder"
    output_string = f"Hits to kill {main.clean_capitalize(location_name)} ({target_name}) with {weapon_name}: "

    if weapon["DamageType"] == "BPDemolitionDamageType":
        #print(weapon['DamageType'])
        return output_string + f"{math.ceil(int(target['Health']) / calculate_damage_inner(weapon['Damage'],weapon['DamageType'],'Tier3GarrisonHouse'))}"

    t = []
    t.append(math.ceil(int(target['Health']) / calculate_damage_inner(weapon["Damage"],weapon["DamageType"],"Tier1GarrisonHouse")))
    t.append( math.ceil(int(target['Health']) / calculate_damage_inner(weapon["Damage"],weapon["DamageType"],"Tier2GarrisonHouse")))
    t.append( math.ceil(int(target['Health']) / calculate_damage_inner(weapon["Damage"],weapon["DamageType"],"Tier3GarrisonHouse")))
    return output_string + f"{t[0]} (Tier 1) {t[1]} (Tier 2) {t[2]} (Tier 3)"


def disable_calculator(weapon_name, target_name):
    weapon = parse.weapons_dictionary[weapon_name]
    structure = parse.targets_dictionary[target_name]
    if structure["ObjectType"]=="Structures":
        raise bot.InvalidTypeError(structure)
    disable_percentage = float(structure["DisableLevel"])
    if disable_percentage=="0":
        raise bot.InvalidTypeError(structure)
    final_damage = calculate_damage(weapon, structure)
    hits_to_kill = calculate_hits_to_disable(float(structure["Health"]) - (float(structure["Health"]) * disable_percentage), final_damage)
    utils.debug_summary(weapon_name,target_name,final_damage, hits_to_kill)
    return {"htd": hits_to_kill, "final_damage": final_damage}


# general logic functions

def get_th_relic_type(name):
    if name in parse.th_relics_dict:
        return parse.th_relics_dict[name]
    raise RuntimeError


# Made them return tuple of (boolean, str)
# If boolean is true, result was successful and str contains result.
# If boolean is false, result was unsuccessful and str contains error message
def general_kill_handler(weapon_fuzzy_name, target_fuzzy_name):

    if weapon_fuzzy_name in parse.weapons_dictionary:
        weapon_name = parse.weapons_dictionary[weapon_fuzzy_name]
    else:
        weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)

    if target_fuzzy_name in parse.targets_dictionary:
        target_name = parse.targets_dictionary[target_fuzzy_name]
    else:
        target_name = fuzz.fuzzy_match_target_name(target_fuzzy_name)
    return damage_calculator(weapon_name, target_name)

def general_disable_handler(weapon_fuzzy_name, target_fuzzy_name):
    weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)
    structure_name = fuzz.fuzzy_match_target_name(target_fuzzy_name)
    data = disable_calculator(weapon_name, structure_name)

    return f"It takes {data['htd']} {weapon_name} to disable a {structure_name}"


def relic_th_kill_handler(weapon_fuzzy_name, location_fuzzy_name):
    location_name = fuzz.fuzzy_match_th_relic_name(location_fuzzy_name)
    weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)
    target_name = get_th_relic_type(location_name)
    output_string = f"Hits to kill {main.clean_capitalize(location_name)} ({target_name}) with {weapon_name}: "

    # check if target_name is relic base, should be done better somehow
    if "relic" in target_name:
        return output_string + f"{damage_calculator(weapon_name, target_name)['htk']}"

    # check if damage type is demolition
    if parse.weapons_dictionary[weapon_name]["DamageType"] == "BPDemolitionDamageType":
        target_name_tiered = f"{target_name} T3"
        return output_string + f"{damage_calculator(weapon_name, target_name_tiered)['htk']}"

    t = []
    for tier in ["T1", "T2", "T3"]:
        t.append(damage_calculator(weapon_name, f"{target_name} {tier}")['htk'])
    return output_string + f"{t[0]} (Tier 1) {t[1]} (Tier 2) {t[2]} (Tier 3)"

def statsheet_handler(entity_name):
    try:
        weapon = parse.weapons[fuzz.fuzzy_match_weapon_name(entity_name)]
        weapon_name = weapon["Informalname"]
        weapon_damage = weapon["Damage"]
        weapon_damage_type = weapon["DamageType"]
        print("im here")
        return f"Weapon name: {weapon_name} \nWeapon raw damage: {weapon_damage} \nWeapon damage type: {weapon_damage_type}"
    except bot.WeaponNotFoundError as e:
        try:
            entity=parse.targets[fuzz.fuzzy_match_target_name(entity_name)]
            if entity["ObjectType"]=="Structures":
                structure_name = entity["Name"]
                structure_raw_hp = entity["Health"]
                structure_mitigation = entity["MitigationType"]
                structure_repair_cost = entity["RepairCost"]
                structure_decay_start = entity["DecayStartHours"]
                structure_decay_duration = entity["DecayDurationHours"]
                return f"Structure name: {structure_name}\Raw HP: {structure_raw_hp}\Mitigation Type: {structure_mitigation}\Repair Cost: {structure_repair_cost}\Decay Timer: {structure_decay_start}\Time to Decay: {structure_decay_duration}"
            else:
                if entity["ObjectType"]=="Vehicles_Tripods_Emplacements":
                    vehicle_name = entity["Name"]
                    vehicle_raw_hp = entity["Health"]
                    vehicle_mitigation = entity["MitigationType"]
                    vehicle_min_pen = int(float(entity["MinBasePenetrationChance"]) * 100)
                    vehicle_max_pen = int(float(entity["MaxBasePenetrationChance"]) * 100)  #note to self: make decimals into fractions, make timer into hours
                    vehicle_armour_hp = entity["ArmourHealth"]
                    vehicle_reload = entity["Reloadtime"]
                    vehicle_main = entity["MainWeapon"]
                    vehicle_main_disable = int(float(entity["MainGunDisableChance"]) * 100)
                    vehicle_track_disable = int(float(entity["TracksDisableChance"])* 100)
                    return f"Name: {vehicle_name}\nRaw HP: {vehicle_raw_hp}\nMitigation Type: {vehicle_mitigation}\nMinimum Penetration Chance (Max Armour): {vehicle_min_pen}%\nMaximum Penetration Chance (Stripped Armour): {vehicle_max_pen}%\nArmour HP (Penetration damage to strip): {vehicle_armour_hp}\nReload Time: {vehicle_reload}\nTrack Chance: {vehicle_track_disable}%\nMain Gun Disable Chance: {vehicle_main_disable}%\nMain Weapon: {vehicle_main}"
            return "Null"
        except bot.EntityNotFoundError as e:
            return e.show_message()