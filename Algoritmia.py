from pyswip import Prolog
from random import randint

def setupProlog():
    prolog = Prolog( )
    #spellDamage(spell, minDamage, maxDamage, description)
    #spells a disposición del jugador/ataques básicos del enemigo
    prolog. assertz("spellDamage(fireball, 10, 15, 'Shoot a fireball at your enemy')")
    prolog. assertz("spellDamage(ice, 4, 12, 'Shoot an ice shard at your enemy')")
    prolog. assertz("spellDamage(lightning, 7, 14, 'Shoot a lightning bolt at your enemy')")
    prolog. assertz("spellDamage(summonfrog, 3, 5, 'Summon a frog to attack your enemy, ribbit!')")
    prolog. assertz("spellDamage(summondragon, 10, 25, 'Summon a fierce dragon to attack your enemy')")
    prolog. assertz("spellDamage(nuke, 100, 200, 'Hey! Why are you using this?')")
   
    return prolog

def prologSpellAux(prolog, spell):
    #formateo string para consultar y retorno información de la base de conocimiento
    spellProlog = "".join(spell.split()) #elimino espacios (summon frog -> summonfrog)
    for result in prolog.query(f"spellDamage({spellProlog.lower()}, MinDamage, MaxDamage, Description)"):
        return result

def userTurn(prolog):
    #lógica de turno del jugador
    spellList = ["FIREBALL", "ICE", "LIGHTNING", "SUMMON FROG", "SUMMON DRAGON"]
    valid = False
    #loop hasta que el usuario seleccione un spell válido
    while(valid == False):
        print("YOUR TURN")
        print("Available spells: ", spellList)
        print("Type HELP to check a spell's description")
        spell = input().upper()
        if spell in spellList: #si el spell es válido
            valid = True
        elif spell == "NUKE": #easter egg
            print("Hey that's a secret!")
            valid = True
        elif spell == "HELP": #ayuda
            helpHandler(prolog)
        else: #spell inválido
            print("Invalid spell, please try again\n")
    
    spellData = prologSpellAux(prolog, spell)
    castSpell(spell, "YOU", spellData)

def castSpell(spell, turn, spellData):
    #lógica de lanzamiento de spell
    damage = randint(spellData['MinDamage'],spellData['MaxDamage']) #daño aleatorio entre min y max
    print("YOU casted", spell)
    print("Dealt", damage, "damage")
    #IMPLEMENTAR LÓGICA DE DAÑO AL ENEMIGO/USUARIO

def helpHandler(prolog):
    #descripcion de un spell
    print("Select a spell to see its description")
    spell = input().upper()
    spellData = prologSpellAux(prolog, spell)

    print(spell,"-"*(32-len(spell))) #formato lindo pq me gusta sufrir :D
    print(spellData['Description'])
    print("Deals", spellData['MinDamage'], "to", spellData['MaxDamage'], "damage")
    print("---------------------------------\n")

def main():
    prolog = setupProlog()
    '''
    for spell in prolog.query("spellDamage(Spell, MinDamage, MaxDamage, Description)"):
        if spell['Spell'] != "nuke":
            print(f"Spell: {spell['Spell']}, Min Damage: {spell['MinDamage']}, Max Damage: {spell['MaxDamage']}")
    '''
    userTurn(prolog)

main()
