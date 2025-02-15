:- dynamic warrior/2.
:- dynamic opponent/2.
:- dynamic spell/1.
:- dynamic description/2.
:- dynamic damage_range/3.
:- dynamic crit_chance/2.
:- dynamic can_cast/2.
:- dynamic secret/2.
:- dynamic can_cast_trap/3. 
:- dynamic current_cooldown/3.
:- dynamic initialize_cooldowns/0.
:- dynamic update_cooldowns/0.
:- dynamic can_cast_spell/2.

warrior(you,100).
warrior(boss,100).
opponent(you,boss).
opponent(boss,you).

spell(fireball).
spell(ice).
spell(lightning).
spell(summon_frog).
spell(summon_dragon).
spell(nuke).
spell(heal).

trap(trap_key).
trap(disable_key).

description(fireball, 'Shoot a fireball at your enemy.').
description(ice, 'Shoot an ice shard at your enemy.').
description(lightning, 'Shoot lightning at your enemy.').
description(summon_frog, 'Summon a frog, ribbit!').
description(summon_dragon, 'Thats not a frog!').
description(nuke, 'Uh oh! You shouldnt use this.').
description(heal, 'Heal yourself a little bit.').
description(trap_key, 'Lays a trap on one of your opponents keys.\nOnly two traps can be active at once.').
description(disable_key, 'Disables one of your opponents keys!.\nOnly one key can be disabled at once.').

damage_range(fireball, 20, 50).
damage_range(ice, 15, 40).
damage_range(lightning, 25, 60).
damage_range(summon_frog, 5, 15).
damage_range(summon_dragon, 99, 99).
damage_range(nuke, 500, 1000).
damage_range(heal, 10, 15).
damage_range(trap_key, 15,15).
damage_range(disable_key, 0, 0).

crit_chance(fireball, 20).
crit_chance(ice, 10).
crit_chance(lightning, 30).
crit_chance(summon_frog, 10).
crit_chance(summon_dragon, 0).
crit_chance(nuke, 100).
crit_chance(heal, 15).

target(Spell,Caster,Opponent) :- spell(Spell), Spell \= heal, warrior(Caster,_), opponent(Caster,Opponent).
target(nuke,Caster,Caster) :- opponent(Caster,_), warrior(Caster,_).
target(heal,Caster,Caster) :- warrior(Caster,_),warrior(Caster,_).
target(Trap,Caster,Opponent) :- trap(Trap), warrior(Caster,_), opponent(Caster,Opponent).

secret(you,nuke).
secret(you,summon_dragon).
secret(boss,nuke).
secret(boss,summon_dragon).

is_one_hp(Warrior) :- warrior(Warrior,1).

can_die(Warrior) :-
    warrior(Warrior, HP),
    damage_range(Spell, _, Max_Dmg),
    Spell \= heal,
    \+ secret(Warrior,Spell),
    HP =< Max_Dmg.

boss_choice(nuke, 1, _, _, _).

boss_choice(heal, 0, 1, _, _).

boss_choice(trap_key, 0, 0, 0, _). 

boss_choice(disable_key, 0, _, _, 0).

boss_choice(Spell, 0, _, _, _) :- 
    spell(Spell),
    Spell \= nuke,
    Spell \= heal.

cooldown(fireball, 2).
cooldown(ice, 3).
cooldown(lightning, 4).
cooldown(summon_frog, 5).
cooldown(summon_dragon, 10).
cooldown(nuke, 20).
cooldown(heal, 3).
cooldown(trap_key, 5).
cooldown(disable_key, 10).

initialize_cooldowns :-
    forall(spell(Spell), (assertz(current_cooldown(you, Spell, 0)), assertz(current_cooldown(boss, Spell, 0)))).

update_cooldowns :-
    forall(current_cooldown(User, Spell, CD), (
        (CD > 0 -> NewCD is CD - 1; NewCD is 0),
        retract(current_cooldown(User, Spell, CD)),
        assertz(current_cooldown(User, Spell, NewCD))
    )).

update_single_cooldown(User, Spell) :-
    current_cooldown(User, Spell, CD),
    (CD > 0 -> NewCD is CD - 1; cooldown(Spell, DefaultCD), NewCD is DefaultCD),
    retract(current_cooldown(User, Spell, CD)),
    assertz(current_cooldown(User, Spell, NewCD)).

can_cast_spell(User, Spell) :-
    current_cooldown(User, Spell, CD),
    CD =:= 0.