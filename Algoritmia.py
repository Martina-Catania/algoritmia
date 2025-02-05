from pyswip import Prolog
from random import randint
import time

prolog = Prolog( )
#spells tienen nombre, daño mínimo, daño máximo y descripción
#spell(spell, minDmg, maxDmg, critThresh, description)
prolog.assertz("spell(fireball, 20, 45, 15, 'Shoot a fireball at your enemy')")
prolog.assertz("spell(ice, 15, 50, 25, 'Shoot an ice shard at your enemy')")
prolog.assertz("spell(lightning, 25, 35, 50, 'Shoot a lightning bolt at your enemy')")
prolog.assertz("spell(summon_frog, 3, 15, 15, 'Summon a frog to attack your enemy, ribbit!')")
prolog.assertz("specialSpell(summon_dragon, 50, 90, 0, 'Thats not a frog!')")
prolog.assertz("specialSpell(nuke, 150, 200, 0, 'Hey! Youre not supposed to know this!')")
#USER SPELLS
prolog.assertz("canCast(user, Spell) :- spell(Spell, _, _, _, _)") #usuario puede lanzar cualquier spell normal
prolog.assertz("canCastSpecial(user, summon_dragon)") #easter egg: usuario puede lanzar summon_dragon
prolog.assertz("canCastSpecial(user, nuke)") #easter egg: usuario puede lanzar nuke
#BOSS SPELLS
prolog.assertz("canCast(boss, Spell) :- spell(Spell, _, _, _, _)") #boss puede lanzar cualquier spell normal
prolog.assertz("canCastSpecial(boss, nuke)") #ataque especial si boss queda a 1hp


def printSleep(string):
    print(string)
    time.sleep(0.5)

def firstTurn():
    printSleep("Welcome to the game!")
    printSleep("You're a word wizard!")
    printSleep("Any spells you type will be casted! Pretty neat huh?")
    printSleep("Why don't you give it a try?\n")
    damage = userTurn()
    printSleep("\nSeems you hit someone, whoops!")
    printSleep("Oh well! My job here is done!\nGood luck man!\n")
    return damage

def prologSpellAux(spell):
    #formateo string para consultar y retorno información de la base de conocimiento
    spellProlog = spell.replace(" ", "_")
    for result in prolog.query(f"spell({spellProlog.lower()}, MinDamage, MaxDamage, CritThresh, Description)"):
        ret = result
    for result in prolog.query(f"specialSpell({spellProlog.lower()}, MinDamage, MaxDamage, CritThresh, Description)"):
        ret = result
    return ret

def helpHandler():
    #descripcion de un spell
    printSleep("Select a spell to see its description")
    spell = input().upper()
    spellData = prologSpellAux(spell)
    printSleep("")
    print(spell,"-"*(32-len(spell))) #formato lindo pq me gusta sufrir :D
    print(spellData['Description'])
    print("Deals", spellData['MinDamage'], "to", spellData['MaxDamage'], "damage")
    print("Critical hit chance:", spellData['CritThresh'],"%")
    printSleep("---------------------------------\n")

def userTurn():
    valid = False
    #lista de spells que el usuario conoce
    spellList = [] 
    for result in prolog.query("canCast(user, Spell)"):
        spellList.append(" ".join(result["Spell"].split("_")).upper())
    #lista de spells especiales que el usuario puede usar (easter eggs)
    specialSpellList = [] 
    for result in prolog.query("canCastSpecial(user, Spell)"):
        specialSpellList.append(" ".join(result["Spell"].split("_")).upper())
    printSleep("YOUR TURN")
    #loop hasta que el usuario seleccione un spell válido
    while(valid == False):
        printSleep("Available spells: " + ", ".join(spellList))
        printSleep("Type HELP to check a spell's description")
        spell = input().upper()
        if spell in spellList: #si el spell es válido
            valid = True
        elif spell in specialSpellList: #si el spell es un spell especial
            printSleep("Hey that's a secret!")
            aux = spell.replace(" ", "_")
            prolog.assertz(f"canCast(user, {aux.lower()})") #agregar spell a la lista de spells
            valid = True
        elif spell == "HELP": #ayuda
            helpHandler(prolog)
        else: #spell inválido
            printSleep("That's not a valid spell!\n")
    return castSpell(spell, "YOU", "BOSS")

def enemyTurn():
    #lógica de turno del enemigo
    spellList = [] 
    for result in prolog.query("canCast(boss, Spell)"):
        spellList.append(" ".join(result["Spell"].split("_")).upper())
    spell = spellList[randint(0,len(spellList)-1)]
    spellData = prologSpellAux(spell)
    return castSpell(spell, "BOSS", "YOU")

def castSpell(spell, turn, opponent):
    #lógica de lanzamiento de spell
    spellData = prologSpellAux(spell)
    damage = randint(spellData['MinDamage'], spellData['MaxDamage'])
    if randint(0,100) <= spellData['CritThresh']:
        printSleep("Critical hit!")
        if spell == "SUMMON FROG": #easter egg
            printSleep("That's not a frog!")
            spell = "SUMMON DRAGON"
            spellData = prologSpellAux(prolog, spell)
            damage = randint(spellData['MinDamage'], spellData['MaxDamage'])
        else: #crit = doble daño
            damage = damage*2
    printSleep(f"{turn} casted {spell} dealing {damage} damage to {opponent}!")
    return damage

def main():
    userHealth = 100
    bossHealth = 150
    bossHealth = bossHealth - firstTurn()
    printSleep(f"Boss health: {bossHealth}")
    if bossHealth > 0:
            userHealth = userHealth - enemyTurn()
            printSleep(f"YOUR health: {userHealth}")
    while(userHealth > 0 and bossHealth > 0):
        bossHealth = bossHealth - userTurn()
        printSleep(f"BOSS health: {bossHealth} ")
        printSleep("")
        if bossHealth > 0:
            userHealth = userHealth - enemyTurn()
            printSleep(f"YOUR health: {userHealth}")
            printSleep("")
    print ("Game Over,", "YOU" if userHealth > 0 else "BOSS", "won!")
main()