:- dynamic warrior/2.
:- dynamic opponent/2.
:- dynamic spell/1.
:- dynamic description/2.
:- dynamic damage_range/3.
:- dynamic crit_chance/2.
:- dynamic can_cast/2.
:- dynamic secret/2.

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

description(fireball, 'Shoot a fireball at your enemy.').
description(ice, 'Shoot an ice shard at your enemy').
description(lightning, 'Shoot lightning at your enemy.').
description(summon_frog, 'Summon a frog, ribbit!').
description(summon_dragon, 'Thats not a frog!').
description(nuke, 'Uh oh! You shouldnt use this.').

damage_range(fireball, 20, 50).
damage_range(ice, 15, 40).
damage_range(lightning, 25, 60).
damage_range(summon_frog, 5, 15).
damage_range(summon_dragon, 99, 99).
damage_range(nuke, 500, 1000).

crit_chance(fireball, 20).
crit_chance(ice, 10).
crit_chance(lightning, 30).
crit_chance(summon_frog, 15).
crit_chance(summon_dragon, 50).
crit_chance(nuke, 100).

target(Spell,Warrior,Opponent) :- spell(Spell), warrior(Warrior,_), opponent(Warrior,Opponent).
target(nuke,Warrior,Warrior) :- opponent(Warrior,_), warrior(Warrior,_).

secret(you,nuke).
secret(you,summon_dragon).
secret(boss,nuke).