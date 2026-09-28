#!/usr/bin/env python3

from optparse import OptionParser
import random
import math
import sys

from paging_policy import ReplacementPolicy


def random_seed(seed):
    random.seed(seed)


def convert(size):
    """Convert strings such as 16, 4k, 64K, 2m into bytes."""
    lastchar = size[-1]
    if lastchar in ('k', 'K'):
        return int(size[:-1]) * 1024
    elif lastchar in ('m', 'M'):
        return int(size[:-1]) * 1024 * 1024
    elif lastchar in ('g', 'G'):
        return int(size[:-1]) * 1024 * 1024 * 1024
    else:
        return int(size)


def must_be_power_of_two(size, msg):
    if size <= 0 or (size & (size - 1)) != 0:
        print('Error in argument: %s' % msg)
        sys.exit(1)


def must_be_multiple_of(big, small, msg):
    if big % small != 0:
        print('Error in argument: %s' % msg)
        sys.exit(1)


class PageTableEntry:
    def __init__(self):
        self.present = False
        self.pfn = None


# Student TODO 1

def split_virtual_address(vaddr, pagebits, pagemask):
    """
    Split a virtual address into its virtual page number (VPN)
    and page offset.

    HINT: OSTEP's paging-linear-translate.py contains analogous logic.
    """
    vpn = None       # TODO
    offset = None    # TODO
    return vpn, offset


# Student TODO 2

def make_physical_address(pfn, offset, pagebits):
    """Construct a physical address from PFN and page offset."""
    return None      # TODO


# Student TODO 3

def find_free_frame(frames):
    """
    frames[pfn] is None if the frame is free; otherwise it contains
    the VPN currently stored in that frame.

    Return a free PFN, or None if all frames are occupied.
    """
    return None      # TODO


def access_string(hit):
    return 'HIT' if hit else 'PAGEFAULT'


def victim_string(victim):
    return '-' if victim is None else str(victim)


parser = OptionParser()
parser.add_option('-A', '--addresses', default='-1',
                  help='comma-separated virtual addresses; -1 means randomly generate',
                  action='store', type='string', dest='addresses')
parser.add_option('-f', '--addressfile', default='',
                  help='file containing virtual addresses',
                  action='store', type='string', dest='addressfile')
parser.add_option('-n', '--numaddrs', default=10,
                  help='number of virtual addresses to generate',
                  action='store', type='int', dest='numaddrs')
parser.add_option('-a', '--asize', default='16k',
                  help='virtual address-space size (e.g., 16k, 64k)',
                  action='store', type='string', dest='asize')
parser.add_option('-P', '--pagesize', default='4k',
                  help='page size (e.g., 1k, 4k)',
                  action='store', type='string', dest='pagesize')
parser.add_option('-C', '--frames', default=3,
                  help='number of physical page frames',
                  action='store', type='int', dest='frames')
parser.add_option('-p', '--policy', default='FIFO',
                  help='replacement policy: FIFO, LRU, MRU, OPT, UNOPT, RAND, CLOCK',
                  action='store', type='string', dest='policy')
parser.add_option('-b', '--clockbits', default=2,
                  help='for CLOCK policy, maximum reference count per page',
                  action='store', type='int', dest='clockbits')
parser.add_option('-s', '--seed', default=0,
                  help='random number seed',
                  action='store', type='int', dest='seed')
parser.add_option('-N', '--notrace', default=False,
                  help='do not print detailed trace',
                  action='store_true', dest='notrace')

(options, args) = parser.parse_args()

asize = convert(options.asize)
pagesize = convert(options.pagesize)
numframes = options.frames

must_be_power_of_two(asize, 'address space must be a power of two')
must_be_power_of_two(pagesize, 'page size must be a power of two')
must_be_multiple_of(asize, pagesize,
                    'address space must be a multiple of page size')

if pagesize > asize:
    print('Error: page size cannot exceed address-space size')
    sys.exit(1)
if numframes <= 0:
    print('Error: number of frames must be positive')
    sys.exit(1)
if options.numaddrs <= 0:
    print('Error: number of addresses must be positive')
    sys.exit(1)
if options.clockbits <= 0:
    print('Error: clockbits must be positive')
    sys.exit(1)

policy_name = options.policy.upper()
valid_policies = ('FIFO', 'LRU', 'MRU', 'OPT', 'UNOPT', 'RAND', 'CLOCK')
if policy_name not in valid_policies:
    print('Error: replacement policy must be one of: %s'
          % ', '.join(valid_policies))
    sys.exit(1)

num_vpages = asize // pagesize
pagebits = int(math.log(pagesize, 2))
pagemask = pagesize - 1

page_table = [PageTableEntry() for _ in range(num_vpages)]
frames = [None for _ in range(numframes)]
policy = ReplacementPolicy(policy_name, numframes, options.clockbits)

random_seed(options.seed)
addr_list = []

if options.addressfile != '':
    with open(options.addressfile) as fd:
        for line in fd:
            line = line.strip()
            if line != '':
                addr_list.append(int(line, 0))
elif options.addresses == '-1':
    for _ in range(options.numaddrs):
        addr_list.append(int(asize * random.random()))
else:
    for addr in options.addresses.split(','):
        addr_list.append(int(addr.strip(), 0))

for vaddr in addr_list:
    if vaddr < 0 or vaddr >= asize:
        print('Error: virtual address %s is outside the address space' % hex(vaddr))
        sys.exit(1)

print('ARG address space size', options.asize)
print('ARG page size', options.pagesize)
print('ARG frames', numframes)
print('ARG policy', policy_name)
if options.addressfile != '':
    print('ARG address file', options.addressfile)
elif options.addresses == '-1':
    print('ARG addresses', ','.join(str(addr) for addr in addr_list))
else:
    print('ARG addresses', options.addresses)
print('')

hits = 0
faults = 0

for addr_index, vaddr in enumerate(addr_list):
    # Student TODO 4: split VA into VPN and offset.
    vpn, offset = split_virtual_address(vaddr, pagebits, pagemask)

    # Student TODO 5: determine hit/page fault from the page table.
    pte = page_table[vpn]
    hit = False      # TODO

    victim = None

    if hit:
        hits += 1
        # PROVIDED POLICY CODE: notify the policy module about the hit.
        policy.hit(vpn)

    else:
        faults += 1

        # Find a free frame, if one exists.
        pfn = find_free_frame(frames)

        # PROVIDED POLICY CODE: if replacement is needed, this returns
        # the victim VPN; otherwise it returns None.
        victim = policy.page_fault(vpn, addr_list, addr_index, pagebits)

        if victim is not None:
            # Student TODO 6: evict victim from the VM model.
            # 1. determine which PFN contains victim
            # 2. mark victim's PTE nonresident
            # 3. clear victim's PFN from its PTE
            # 4. preserve that PFN so the incoming page can reuse it
            # The policy module has already removed victim from its state.
            pass        # TODO

        # Student TODO 7: install vpn into pfn.
        # Update frames[pfn], page_table[vpn].present, and page_table[vpn].pfn.
        # The policy module has already added vpn to its resident-page state.
        pass            # TODO

    # Student TODO 8: complete the physical-address translation.
    pfn = None          # TODO
    paddr = None        # TODO

    if not options.notrace:
        print(
            'VA 0x%08x VPN %4d offset 0x%04x '
            '%s -> PFN %3d PA 0x%08x Replaced:%s'
            %
            (vaddr, vpn, offset, access_string(hit),
             pfn, paddr, victim_string(victim))
        )

print('')
total = hits + faults
hitrate = 0.0 if total == 0 else 100.0 * float(hits) / float(total)
print('FINALSTATS hits %d faults %d hitrate %.2f'
      % (hits, faults, hitrate))
