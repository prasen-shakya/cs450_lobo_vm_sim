#
# Behavior tested:
# This test proves that chained evictions keep the page table and frame array 
# consistent. two FIFO evictions must recycle the two victims PFNs in the correct order 
# and a later HIT on the first replacement VPN must still resolve to that recycled PFN.
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
# Test Case
#
cat >$LOG << 'EOF'
Description:
------------
Fill 2 frames with VPNs 0,1 (phase 1), then reference VPN 2 to force
FIFO eviction #1 (evicts VPN 0, recycles PFN 0), then reference VPN 3
to force eviction #2 (evicts VPN 1, recycles PFN 1). The two evictions
must reuse different PFNs in the right order. The trailing re-reference
of VPN 2 must HIT at PFN 0 -- confirming the first-eviction bookkeeping
survived the second eviction. Mixed offsets 2,3,1 also exercise correct
offset preservation.

Command:
--------
python3 ./lobo-vm-sim.py -s 0 -a 32 -P 4 -C 2 -p FIFO -A 2,6,11,13,11
--------
EOF

#
# Test with LOBO
#
$PYTHON $LOBO -s 0 -a 32 -P 4 -C 2 -p FIFO -A 2,6,11,13,11 >$OUT 2>&1

#
# Expected output
#
cat >$EOUT << 'EOF'
ARG address space size 32
ARG page size 4
ARG frames 2
ARG policy FIFO
ARG addresses 2,6,11,13,11

VA 0x00000002 VPN    0 offset 0x0002 PAGEFAULT -> PFN   0 PA 0x00000002 Replaced:-
VA 0x00000006 VPN    1 offset 0x0002 PAGEFAULT -> PFN   1 PA 0x00000006 Replaced:-
VA 0x0000000b VPN    2 offset 0x0003 PAGEFAULT -> PFN   0 PA 0x00000003 Replaced:0
VA 0x0000000d VPN    3 offset 0x0001 PAGEFAULT -> PFN   1 PA 0x00000005 Replaced:1
VA 0x0000000b VPN    2 offset 0x0003 HIT -> PFN   0 PA 0x00000003 Replaced:-

FINALSTATS hits 1 faults 4 hitrate 20.00
EOF

#
# Chekc results
#
diff $EOUT $OUT >> $LOG
echo "---------" >> $LOG

diff $EOUT $OUT >/dev/null && echo "PASS $TEST" || echo "FAIL $TEST"
