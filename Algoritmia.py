from pyswip import Prolog
from random import randint
import time

prolog = Prolog()
prolog.consult("spell_logic.pl")
prolog.retract("warrior(you, Health)")
prolog.retract("warrior(boss, Health)")
prolog.assertz("warrior(you, 100)")
prolog.assertz("warrior(boss, 100)")



def format_to_print(string):
    #summon_frog -> SUMMON FROG
    return " ".join(string.split("_")).upper()

def format_to_prolog(string):
    #SUMMON FROG -> summon_frog
    return string.replace(" ", "_").lower()

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
    else:
        print("That's not a spell silly!")
        return

def print_data(spell_data):
    print("-------------------------------------")
    print(format_to_print(spell_data), "-", list(prolog.query(f"description({spell_data}, Desc)"))[0]["Desc"])
    damage = list(prolog.query(f"damage_range({spell_data}, Min, Max)"))
    if spell_data == "heal":
        print("Heals", damage[0]["Min"], "to", damage[0]["Max"], "hp")
    else:
        print("Deals", damage[0]["Min"], "to", damage[0]["Max"], "damage")
    print("Critical chance:", list(prolog.query(f"crit_chance({spell_data}, Chance)"))[0]["Chance"],"%")
    print("-------------------------------------\n")

def cast_spell(spell,caster):
    #lógica para castear un spell
    crit_modifier = 1
    spell_data = format_to_prolog(spell) #formateo nombre del spell para hacer consultas de prolog
    target_list = [target["Target"] for target in prolog.query(f"target({spell_data}, {caster}, Target)")] #oponente o todos en la batalla
    # check si es crítico
    crit_chance = list(prolog.query(f"crit_chance({spell_data}, Chance)"))[0]["Chance"]
    if randint(0, 100) < crit_chance:
        print("Critical hit!")
        if spell == "SUMMON FROG": #easter egg, si el usuario hace un critico con SUMMON FROG, se invoca un dragon
            print("That's a big frog!")
            cast_spell("SUMMON DRAGON", caster)
            return
        else:
            crit_modifier = 2
    #calculo daño
    damage_range = list(prolog.query(f"damage_range({spell_data}, Min, Max)"))[0]
    damage = randint(damage_range["Min"], damage_range["Max"]) * crit_modifier 

    print(f"{format_to_print(caster)} casted {format_to_print(spell)}")
    #handle daño a los objetivos
    for target in target_list:
        #query vida actual
        current_health = list(prolog.query(f"warrior({target}, Health)"))[0]["Health"]
        #actualizo vida del objetivo e imprimo
        prolog.retract(f"warrior({target}, {current_health})")
        if spell == "HEAL":
            prolog.assertz(f"warrior({target}, {current_health + damage})")
            print(f"{format_to_print(target)} healed {damage} hp!")
        else:
            prolog.assertz(f"warrior({target}, {current_health - damage})")
            print(f"Dealt {damage} damage to {format_to_print(target)}")
        #imprimo resultado
        print(f"{format_to_print(target)} health: {list(prolog.query(f'warrior({target}, Health)'))[0]['Health']}\n")
        if list(prolog.query(f"warrior({target}, Health)"))[0]["Health"] < 0:
            print(f"O V E R K I L L E D\n")

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
    warriors = list(prolog.query(f"warrior(Warrior, Health)"))
    #loop de juego hasta que alguien se quede sin vida
    while(warriors[0]["Health"] > 0 and warriors[1]["Health"] > 0):
        boss_turn()
        warriors = list(prolog.query(f"warrior(Warrior, Health)"))
        if warriors[0]["Health"] > 0 and warriors[1]["Health"] > 0:
            user_turn()
            warriors = list(prolog.query(f"warrior(Warrior, Health)"))
    
    print("GAME OVER")
    if warriors[0]["Health"] <= 0 and warriors[1]["Health"] <= 0:
        print("What even was your plan dude?")
    elif warriors[0]["Health"] <= 0:
        print("YOU LOST!")
    else:
        print("YOU WON!")
main()