#!/usr/bin/env python3

"""
Replacement-policy support for Lobo-VM-Sim.

This module is adapted closely from the policy logic in OSTEP's
vm-beyondphys-policy/paging-policy.py simulator.

STUDENTS SHOULD NOT MODIFY THIS FILE.

The original OSTEP simulator receives page-number references directly.
Lobo-VM-Sim instead receives virtual addresses, so OPT/UNOPT convert
future virtual addresses into VPNs before comparing them.
"""

import random


class ReplacementPolicy:
    def __init__(self, name, capacity, clockbits=2):
        self.name = name.upper()
        self.capacity = capacity
        self.clockbits = clockbits

        if self.name not in (
            'FIFO', 'LRU', 'MRU', 'OPT', 'UNOPT', 'RAND', 'CLOCK'
        ):
            raise ValueError('unknown replacement policy: %s' % self.name)

        if self.capacity <= 0:
            raise ValueError('capacity must be positive')

        if self.clockbits <= 0:
            raise ValueError('clockbits must be positive')

        # As in OSTEP's paging-policy.py, memory stores the resident
        # page numbers used by the replacement policy.
        self.memory = []

        # CLOCK reference counters.
        self.ref = {}

    def _future_distance(self, vpn, addr_list, addr_index, pagebits):
        distance = 0

        for i in range(addr_index + 1, len(addr_list)):
            distance += 1
            future_vpn = addr_list[i] >> pagebits

            if future_vpn == vpn:
                return distance

        return None

    def hit(self, vpn):
        """Update policy state after a reference to a resident page."""
        if vpn not in self.memory:
            raise RuntimeError('policy hit on nonresident VPN %s' % vpn)

        if self.name in ('LRU', 'MRU'):
            self.memory.remove(vpn)
            self.memory.append(vpn)

        if self.name == 'CLOCK':
            if vpn not in self.ref:
                self.ref[vpn] = 1
            else:
                self.ref[vpn] += 1
                if self.ref[vpn] > self.clockbits:
                    self.ref[vpn] = self.clockbits

    def page_fault(self, vpn, addr_list, addr_index, pagebits):
        """
        Record a page fault for vpn.

        If a free resident-page slot remains, add vpn and return None.
        If replacement is necessary, choose and remove a victim page,
        add vpn, and return the victim VPN.

        This method decides WHICH virtual page is evicted. The calling
        VM simulator remains responsible for updating page-table and
        physical-frame state.
        """
        if vpn in self.memory:
            raise RuntimeError('policy page_fault on resident VPN %s' % vpn)

        victim = None

        if len(self.memory) >= self.capacity:
            if self.name in ('FIFO', 'LRU'):
                victim = self.memory.pop(0)

            elif self.name == 'MRU':
                victim = self.memory.pop(len(self.memory) - 1)

            elif self.name == 'RAND':
                victim_index = int(random.random() * len(self.memory))
                victim = self.memory.pop(victim_index)

            elif self.name in ('OPT', 'UNOPT'):
                best_vpn = None
                best_distance = None

                for candidate in self.memory:
                    distance = self._future_distance(
                        candidate, addr_list, addr_index, pagebits
                    )

                    if self.name == 'OPT':
                        if distance is None:
                            best_vpn = candidate
                            break
                        if best_distance is None or distance > best_distance:
                            best_vpn = candidate
                            best_distance = distance
                    else:
                        if distance is not None:
                            if best_distance is None or distance < best_distance:
                                best_vpn = candidate
                                best_distance = distance

                if best_vpn is None:
                    best_vpn = self.memory[0]

                victim = best_vpn
                self.memory.remove(victim)

            elif self.name == 'CLOCK':
                # Preserve the structure of OSTEP's simulator: repeatedly
                # choose a random resident page. If its reference count is
                # positive, decrement it and give it another chance.
                while victim is None:
                    victim_index = int(random.random() * len(self.memory))
                    candidate = self.memory[victim_index]

                    if self.ref.get(candidate, 0) >= 1:
                        self.ref[candidate] -= 1
                    else:
                        victim = candidate
                        self.memory.pop(victim_index)

                if victim in self.ref:
                    del self.ref[victim]

        self.memory.append(vpn)

        if self.name == 'CLOCK':
            if vpn not in self.ref:
                self.ref[vpn] = 1
            else:
                self.ref[vpn] += 1
                if self.ref[vpn] > self.clockbits:
                    self.ref[vpn] = self.clockbits

        return victim
