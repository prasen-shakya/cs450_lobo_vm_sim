#
# Behavior tested: 
# This test picks a trace where LRU and FIFO would evict different
# pages so a policy mix up actually shows up in the output
#

TEST=$(basename "${0%.sh}")
OUTPUT=$(realpath $(dirname $0))/output
OUT=$OUTPUT/$TEST.out
EOUT=$OUTPUT/$TEST.eout
LOG=$OUTPUT/$TEST.log
LOBO="./lobo-vm-sim.py"
PYTHON=`which python3`

test "tests" != "$(basename $(dirname $(realpath $0)))" && { echo "FAIL: $0 not in 'tests'"; exit 1; }
! test -f $LOBO && { echo "FAIL: $LOBO must exist"; exit 2; }
mkdir -p $OUTPUT
rm -f $OUT $EOUT

#
# Test case
#
cat >$LOG << 'EOF'
Description:
------------
A hit on the oldest resident page flips LRU's victim choice: VPN 1 is
evicted instead of VPN 0 (which FIFO would have picked).

Command:
--------
python3 ./lobo-vm-sim.py -s 0 -a 32 -P 8 -C 3 -p LRU -A 0,8,16,0,24
--------
EOF

#
# Test with LOBO
#
$PYTHON $LOBO -s 0 -a 32 -P 8 -C 3 -p LRU -A 0,8,16,0,24 >$OUT 2>&1

#
# Expected output
#
cat >$EOUT << 'EOF'
ARG address space size 32
ARG page size 8
ARG frames 3
ARG policy LRU
ARG addresses 0,8,16,0,24

VA 0x00000000 VPN    0 offset 0x0000 PAGEFAULT -> PFN   0 PA 0x00000000 Replaced:-
VA 0x00000008 VPN    1 offset 0x0000 PAGEFAULT -> PFN   1 PA 0x00000008 Replaced:-
VA 0x00000010 VPN    2 offset 0x0000 PAGEFAULT -> PFN   2 PA 0x00000010 Replaced:-
VA 0x00000000 VPN    0 offset 0x0000 HIT -> PFN   0 PA 0x00000000 Replaced:-
VA 0x00000018 VPN    3 offset 0x0000 PAGEFAULT -> PFN   1 PA 0x00000008 Replaced:1

FINALSTATS hits 1 faults 4 hitrate 20.00
EOF

#
# Expected output
#
diff $EOUT $OUT >> $LOG
echo "---------" >> $LOG

diff $EOUT $OUT >/dev/null && echo "PASS $TEST" || echo "FAIL $TEST"
