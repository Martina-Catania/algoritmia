:- dynamic warrior/2.
:- dynamic opponent/2.
:- dynamic spell/1.
:- dynamic description/2.
:- dynamic damage_range/3.
:- dynamic crit_chance/2.
:- dynamic can_cast/2.
:- dynamic secret/2.
:- dynamic can_cast_trap/3. 

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
