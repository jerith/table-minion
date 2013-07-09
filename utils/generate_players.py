#!/usr/bin/env python

import os.path
import sys
import random

from table_minion.players import Players


def generate_players(slots, names):
    # TODO: Teams.
    players_by_slot = {}
    slots_by_timeslot = {}
    for slot in slots:
        slots_by_timeslot.setdefault(slot[0], []).append(slot)
        players_by_slot[slot] = {
            'G': random.randint(1, 3),
            'X': random.randint(0, 2),
            'P': random.randint(10, 18),
        }
    max_tables = max(len(v) for v in slots_by_timeslot.values()) * 4
    num_players = random.randint(max_tables * 7,
                                 (max_tables + len(slots) / 2) * 7)
    players = {}
    for name in random.sample(names, num_players):
        players[name] = {}
    gms = random.sample(players.keys(), max_tables)

    for timeslot, slotlist in slots_by_timeslot.iteritems():
        ts_gms = set(gms + random.sample(players, len(slotlist) * 3))
        ts_players = [p for p in players if p not in ts_gms]
        for slot in slotlist:
            for p in random.sample(ts_gms, players_by_slot[slot]['G']):
                players[p][slot] = 'G'
                ts_gms.remove(p)
            for p in random.sample(ts_gms, players_by_slot[slot]['X']):
                players[p][slot] = 'X'
                ts_gms.remove(p)
            for p in random.sample(ts_players, players_by_slot[slot]['P']):
                players[p][slot] = 'P'
                ts_players.remove(p)

    return Players.from_dicts([
        {'name': name, 'team': None, 'slots': pslots}
        for name, pslots in players.iteritems()])


if __name__ == '__main__':
    slots = sys.argv[1:]
    if not slots:
        sys.stderr.write(
            "Usage:\n  %s <slot> [<slot> ...]\n\n" % (sys.argv[0],))
        sys.exit(1)

    names_file = os.path.join(os.path.dirname(__file__), 'names.txt')
    names = [line.strip() for line in open(names_file).readlines()]

    players = generate_players(slots, names)
    players.to_csv(slots, sys.stdout)
