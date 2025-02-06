from pyswip import Prolog
from random import randint
import time

prolog = Prolog()
prolog.consult("spell_logic.pl")

health_dictionary = {warrior["Name"]: warrior["Health"] for warrior in prolog.query("warrior(Name, Health)")}


def format_to_print(string):
    #summon_frog -> SUMMON FROG
    return " ".join(string.split("_")).upper()

def format_to_prolog(string):
    #SUMMON FROG -> summon_frog
    return string.replace(" ", "_").lower()

def testPrint():
    #print warriors
    warriors = []
    for warrior in prolog.query("warrior(Name,Health)"):
        warriors.append(format_to_print(warrior["Name"]))
    print("Warriors:", warriors)
    #print todos los spells
    spells = []
    for spell in prolog.query("spell(Name)"):
        spells.append(format_to_print(spell["Name"]))
    print("Spells: ", spells)
    #print spells que el usuario puede ver
    visible_spells = []
    for spell in prolog.query("can_cast(you, Spell)"):
        visible_spells.append(format_to_print(spell["Spell"]))
    print("Visible spells:", visible_spells)
    #print spells que el usuario puede usar
    available_spells = visible_spells
    for spell in (prolog.query("secret(you, Spell)")):
        available_spells.append(format_to_print(spell["Spell"]))
    print("Available spells:", available_spells)
    #print descripcion de un spell
    for spell in prolog.query("description(Name, Desc)"):
        print(format_to_print(spell["Name"]),"-", spell["Desc"])
    #print daño de un spell
    for spell in prolog.query("damage_range(Name, Min, Max)"):
        print(format_to_print(spell["Name"]),"deals", spell["Min"], "to", spell["Max"], "damage")
    #print crit chance de un spell
    for spell in prolog.query("crit_chance(Name, Chance)"):
        print(format_to_print(spell["Name"]), "critical hit chance:", spell["Chance"],"%")

def first_turn():
    print("Welcome to the game!")
    print("You're a word wizard!")
    print("Any spells you type will be casted! Pretty neat huh?")
    print("Why don't you give it a try?\n")
    user_turn()
    print("\nSeems you hit someone, whoops!")
    print("Oh well! My job here is done!\n")
    print("Good luck man!\n")

def load_spell_lists(user, visible_spells, secret_spells):
    for spell in prolog.query(f"secret({user}, Spell)"):
        secret_spells.append(format_to_print(spell["Spell"]))
    for spell in prolog.query("spell(Name)"):
        if format_to_print(spell["Name"]) in secret_spells:
            continue
        visible_spells.append(format_to_print(spell["Name"]))

def user_turn():
    print("YOUR TURN")
    #cargar spells que el usuario puede usar
    visible_spells = []
    secret_spells = []
    load_spell_lists("you",visible_spells,secret_spells)

    #loop hasta que el usuario seleccione un spell válido
    valid = False
    while(valid == False):
        print("Known spells:", visible_spells)
        print("Type HELP to check a spell's description or SKIP to skip your turn.")
        spell = input().upper()
        if spell in visible_spells: #si el spell es conocido
            valid = True
        elif spell in secret_spells: #si el spell es un spell especial
            print("Hey that's a secret!")
            prolog.retract(f"secret(you, {format_to_prolog(spell)})")
            valid = True
        elif spell == "HELP": #si el usuario quiere ver la descripción de un spell
            help_handler(visible_spells,secret_spells)
        elif spell == "SKIP": #si el usuario quiere saltar su turno
            print("Skipping turn...")
            return
        else:
            print("Invalid spell, try again!")
    cast_spell(spell,"you")
    return

def help_handler(visible_spells,secret_spells):
    print("Select a spell to see its description")
    spell = input().upper()
    spell_data = format_to_prolog(spell)
    if spell in visible_spells: #si el spell es conocido
        print_data(spell_data)
    elif spell in secret_spells: #si el spell es un spell especial
        print("Hey that's a secret!")
        prolog.retract(f"secret(you, {format_to_prolog(spell)})")
        print_data(spell_data)
    else:
        print("That's not a spell silly!")
        return

def print_data(spell_data):
    print("-------------------------------------")
    print(format_to_print(spell_data), "-", list(prolog.query(f"description({spell_data}, Desc)"))[0]["Desc"])
    damage = list(prolog.query(f"damage_range({spell_data}, Min, Max)"))
    print("Deals", damage[0]["Min"], "to", damage[0]["Max"], "damage")
    print("Critical hit chance:", list(prolog.query(f"crit_chance({spell_data}, Chance)"))[0]["Chance"],"%")
    #print("Cooldown: ",list(prolog.query(f"can_cast({spell_data}, Cooldown)"))[0]["Cooldown"],"turns")
    print("-------------------------------------\n")

def cast_spell(spell,caster):
    #lógica para castear un spell normal
    spell_data = format_to_prolog(spell)
    for crit in prolog.query(f"crit_chance({spell_data}, Chance)"):
        crit_chance = crit["Chance"]
    crit_modifier = 1
    target_list = []
    for target in prolog.query(f"target({spell_data}, {caster}, Target)"):
        target_list.append(target["Target"])
    if randint(0,100) < crit_chance:
        print("Critical hit!")
        if spell == "SUMMON FROG":
            cast_spell("SUMMON DRAGON",caster)
        else:
            crit_modifier = 2
    for damage in prolog.query(f"damage_range({spell_data}, Min, Max)"):
        damage = randint(damage["Min"],damage["Max"])*crit_modifier
    
    print(f"{format_to_print(caster)} casted {format_to_print(spell)}")
    deal_damage(damage,target_list)

def deal_damage(damage,target_list):
    global health_dictionary
    for target in target_list:
        if target in health_dictionary:
            health_dictionary[target] -= damage
            if health_dictionary[target] < 0:
                health_dictionary[target] = 0
                print("O V E R K I L L !")
            print(f"Dealt {damage} damage to {format_to_print(target)}")
            print(f"{format_to_print(target)} health: {health_dictionary[target]}")

def boss_turn():
    #lógica de turno del enemigo
    print("BOSS' TURN")
    #lista de spells que el boss puede usar
    visible_spells = []
    secret_spells = []
    load_spell_lists("boss",visible_spells,secret_spells)
    if randint(0,100) < 10:
        spell = secret_spells[randint(0,len(secret_spells)-1)]
    else:
        spell = visible_spells[randint(0,len(visible_spells)-1)]
    cast_spell(spell,"boss")
    return
    

def main():
    first_turn()
    
    while(health_dictionary["you"] > 0 and health_dictionary["boss"] > 0):
        boss_turn()
        
        if health_dictionary["you"] > 0:
            user_turn()
main()