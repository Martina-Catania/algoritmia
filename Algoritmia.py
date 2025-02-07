from pyswip import Prolog
from random import randint
import time

prolog = Prolog()
prolog.consult("spell_logic.pl")
prolog.retract("warrior(you, Health)")
prolog.retract("warrior(boss, Health)")
prolog.assertz("warrior(you, 100)")
prolog.assertz("warrior(boss, 100)")

trap_dictionary = {"you": [], "boss": []} #diccionario de trampas, se guardan en el formato {victima: [trap, letra]}
disable_dictionary = {"you": [], "boss": []} #diccionario letras desactivadas, se guardan en el formato {victima: letra}

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
    print("Seems someone's mad, whoops!")
    print("Oh well! My job here is done!")
    print("Good luck man!\n")

def end_game():
    print("-------------------------------------------------------------------")
    print("GAME OVER")
    you_hp = list(prolog.query("warrior(you, Health)"))[0]["Health"]
    boss_hp = list(prolog.query("warrior(boss, Health)"))[0]["Health"]
    if you_hp <= 0 and boss_hp <= 0:
        print("What even was your plan dude?")
    elif you_hp <= 0:
        print("YOU LOST!")
    else:
        print("YOU WON!")

def load_spell_lists(user, visible_spells, secret_spells,traps):
    for spell in prolog.query(f"secret({user}, Spell)"):
        secret_spells.append(format_to_print(spell["Spell"]))
    for spell in prolog.query("spell(Name)"):
        if format_to_print(spell["Name"]) in secret_spells:
            continue
        visible_spells.append(format_to_print(spell["Name"]))
    for trap in prolog.query("trap(Name)"):
        traps.append(format_to_print(trap["Name"]))

def user_turn():
    print("YOUR TURN")
    #cargar spells que el usuario puede usar
    visible_spells = []
    secret_spells = []
    traps = []
    load_spell_lists("you",visible_spells,secret_spells,traps)

    #loop hasta que el usuario seleccione un spell válido
    valid = False
    while(valid == False):
        print("\nCAST-------------------------------------------------------------------")
        print("Known spells:", visible_spells)
        print("Traps:", traps)
        print("Type HELP to check a spell's description or SKIP to skip your turn.\n")
        spell = input().upper()
        spell_data = format_to_prolog(spell)
        #lógica para manejar el input del usuario
        if spell == "HELP":
            help_handler(visible_spells, secret_spells, traps)
        elif spell == "SKIP":
            print("Skipping turn...")
            valid = True
        elif spell in traps: #si el spell es una trap
            if spell_data == "trap_key" and len(trap_dictionary["boss"]) < 2:
                letter = input_trap_letter("boss")
                cast_trap(spell_data, "you", letter)
                trap_dictionary["boss"].append([spell_data, letter])
                valid = True
            elif spell_data == "disable_key" and len(disable_dictionary["boss"]) == 0:
                letter = input_trap_letter("boss")
                cast_trap(spell_data, "you", letter)
                disable_dictionary["boss"].append(letter)
                valid = True
            else:
                print("You can't cast more traps!")
        elif not check_disabled(spell_data, "you"):
            if spell in visible_spells or spell in secret_spells:
                if spell in secret_spells:
                    print("Hey that's a secret!")
                    prolog.retract(f"secret(you, {spell_data})")
                check_trap(spell_data, "you") #check si el spell tiene una letra trappeada
                if list(prolog.query(f"warrior(you, Health)"))[0]["Health"] <= 0:
                    return
                cast_spell(spell_data, "you")
                valid = True
            else:
                print("Invalid spell, try again!")
    return

def input_trap_letter(target):
    while True:
        letter = input("\nType a letter to cast the trap: ").lower()
        if len(letter) != 1:
            print("Please type a single letter!")
            continue
        if any(f[1] == letter for f in trap_dictionary[target]):
            print(f"The letter {letter} is already trapped!")
            continue
        break
    return letter

def check_disabled(spell_data, caster):
    is_disabled = False
    #check si el spell necesita una letra para ser casted
    for trap in trap_dictionary[caster]:
        if trap[0] == "disable_key" and trap[1] in spell_data: #si el spell tiene una letra trappeada
            print(f"The letter {format_to_print(trap[1])} is disabled!\n")
            is_disabled = True
    return is_disabled

def help_handler(visible_spells,secret_spells,traps):
    print("\nHELP-------------------------------------------------------------------")
    print("Select a spell or trap to see its description")
    valid = False
    while(valid == False):
        print("Known spells:", visible_spells)
        print("Known traps:", traps)
        print("Type BACK when you're ready to cast a spell.\n")
        spell = input().upper()
        spell_data = format_to_prolog(spell)
        if spell in visible_spells or spell in traps:  # si el spell es conocido
            print_data(spell_data)
        elif spell in secret_spells:  # si el spell es un spell especial
            print("Hey that's a secret!")
            prolog.retract(f"secret(you, {spell_data})")
            visible_spells.append(spell)
            secret_spells.remove(spell)
            print_data(spell_data)
        elif spell == "BACK":
            valid = True
        else:
            print("That's not a spell silly!")

def print_data(spell_data):
    print("-------------------------------------------------------------------")
    print(format_to_print(spell_data), "-", list(prolog.query(f"description({spell_data}, Desc)"))[0]["Desc"])
    damage = list(prolog.query(f"damage_range({spell_data}, Min, Max)"))
    match spell_data:
        case "heal":
            print(f"Heals {damage[0]['Min']} to {damage[0]['Max']} hp")
        case "trap_key":
            print(f"Deals {damage[0]['Min']} damage for every instance of the letter in a spell.")
        case "disable_key":
            print("You can only cast this once.")
        case _:
            print(f"Deals {damage[0]['Min']} to {damage[0]['Max']} damage")
    print("-------------------------------------------------------------------\n")

def cast_spell(spell_data,caster):
    #lógica para castear un spell
    #CHECK SI HAY LETRAS TRAPPEADAS
    crit_modifier = 1
    #spell_data = format_to_prolog(spell) #formateo nombre del spell para hacer consultas de prolog
    target_list = [target["Target"] for target in prolog.query(f"target({spell_data}, {caster}, Target)")] #oponente o todos en la batalla
    print(f"\n{format_to_print(caster)} casted {format_to_print(spell_data)}")
    # check si es crítico
    crit_chance = list(prolog.query(f"crit_chance({spell_data}, Chance)"))[0]["Chance"]
    if randint(0, 100) < crit_chance:
        print("Critical hit!")
        if spell_data == "summon_frog": #easter egg, si el usuario hace un critico con SUMMON FROG, se invoca un dragon
            print("That's a big frog!")
            cast_spell("summon_dragon", caster)
            return
        else:
            crit_modifier = 2
    #calculo daño
    damage_range = list(prolog.query(f"damage_range({spell_data}, Min, Max)"))[0]
    damage = randint(damage_range["Min"], damage_range["Max"]) * crit_modifier 
    #handle daño a los objetivos
    for target in target_list:
        #query vida actual
        current_health = list(prolog.query(f"warrior({target}, Health)"))[0]["Health"]
        #actualizo vida del objetivo e imprimo
        prolog.retract(f"warrior({target}, {current_health})")
        if spell_data == "heal":
            prolog.assertz(f"warrior({target}, {current_health + damage})")
            print(f"{format_to_print(target)} healed {damage} hp!")
        else:
            prolog.assertz(f"warrior({target}, {current_health - damage})")
            print(f"Dealt {damage} damage to {format_to_print(target)}")
        #imprimo resultado
        print(f"{format_to_print(target)} health: {list(prolog.query(f'warrior({target}, Health)'))[0]['Health']}\n")
        if list(prolog.query(f"warrior({target}, Health)"))[0]["Health"] < 0:
            print(f"O V E R K I L L")

def cast_trap(trap_data, caster, letter):
    valid = False
    #trap_data = format_to_prolog(trap)
    target = list(prolog.query(f"target({trap_data}, {caster}, Target)"))[0]["Target"]
    print(f"{format_to_print(caster)} casted {format_to_print(trap_data)} on letter {letter.upper()}\n")

def check_trap(spell_data, caster):
    #spell_data = format_to_prolog(spell)
    #check si el spell tiene una letra trappeada
    for trap in trap_dictionary[caster]:
        if trap[0] == "trap_key" and trap[1] in spell_data: #si el spell tiene una letra trappeada
            damage = list(prolog.query(f"damage_range({trap[0]}, Min, Max)"))[0]["Min"] * spell_data.count(trap[1])
            #query vida actual
            current_health = list(prolog.query(f"warrior({caster}, Health)"))[0]["Health"]
            #actualizo vida del objetivo e imprimo
            prolog.retract(f"warrior({caster}, {current_health})")
            prolog.assertz(f"warrior({caster}, {current_health - damage})")
            print(f"The letter {format_to_print(trap[1])} was trapped!")
            print(f"Dealt {damage} damage to {format_to_print(caster)}")
            print(f"{format_to_print(caster)} health: {list(prolog.query(f'warrior({caster}, Health)'))[0]['Health']}\n")
            trap_dictionary[caster].remove(trap)
            if list(prolog.query(f"warrior({caster}, Health)"))[0]["Health"] <= 0:
                print(f"Did {caster} just die to a trap?\n")

def boss_turn():
    #lógica de turno del enemigo
    print("BOSS' TURN")
    #lista de spells que el boss puede usar
    visible_spells = []
    secret_spells = []
    traps = []
    load_spell_lists("boss",visible_spells,secret_spells,traps)
    #spells
    '''if randint(0,100) < 10:
        spell = secret_spells[randint(0,len(secret_spells)-1)]
    else:
        spell = visible_spells[randint(0,len(visible_spells)-1)]
    check_trap(spell_data, "boss") #check si el spell tiene una letra trappeada
    cast_spell(spell_data,"boss")'''
    #traps
    letter = input_trap_letter("you")
    cast_trap(format_to_prolog(traps[0]), "boss", letter)
    #cast_trap(format_to prolog(traps[1]), "boss", letter)
    return
    
def main():
    warriors = list(prolog.query(f"warrior(Warrior, Health)"))
    first_turn()
    warriors = list(prolog.query(f"warrior(Warrior, Health)")) #actualizo vida de los jugadores
    #loop de juego hasta que alguien se quede sin vida
    while(warriors[0]["Health"] > 0 and warriors[1]["Health"] > 0):
        boss_turn()
        warriors = list(prolog.query(f"warrior(Warrior, Health)")) #actualizo vida de los jugadores
        if warriors[0]["Health"] > 0 and warriors[1]["Health"] > 0: #si ambos siguen vivos, turno del usuario
            user_turn()
            warriors = list(prolog.query(f"warrior(Warrior, Health)")) #actualizo vida de los jugadores
    end_game()
main()