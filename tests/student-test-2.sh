#
# Behavior tested: 
# This test proves that eviction clears properly.
# After an eviction, rereferencing the evicted VPN must cause a page fault
# if the stale page table entry was left as present=true it would HIT which would be wrong.
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
Fill 3 frames with VPNs 0,1,2 (phase 1), then reference VPN 3 to
force a FIFO eviction of VPN 0 (phase 2), then re-reference VPN 0
(phase 3). The re-reference must PAGEFAULT -- a HIT here would mean
the evictor forgot to clear page_table[victim].present. Mid-page
offset 5 also confirms the offset is preserved on the re-fault.

Command:
--------
python3 ./lobo-vm-sim.py -s 0 -a 64 -P 8 -C 3 -p FIFO -A 5,13,21,29,5
--------
EOF

#
# Test with LOBO
#
$PYTHON $LOBO -s 0 -a 64 -P 8 -C 3 -p FIFO -A 5,13,21,29,5 >$OUT 2>&1

#
# Expected output
#
cat >$EOUT << 'EOF'
ARG address space size 64
ARG page size 8
ARG frames 3
ARG policy FIFO
ARG addresses 5,13,21,29,5

VA 0x00000005 VPN    0 offset 0x0005 PAGEFAULT -> PFN   0 PA 0x00000005 Replaced:-
VA 0x0000000d VPN    1 offset 0x0005 PAGEFAULT -> PFN   1 PA 0x0000000d Replaced:-
VA 0x00000015 VPN    2 offset 0x0005 PAGEFAULT -> PFN   2 PA 0x00000015 Replaced:-
VA 0x0000001d VPN    3 offset 0x0005 PAGEFAULT -> PFN   0 PA 0x00000005 Replaced:0
VA 0x00000005 VPN    0 offset 0x0005 PAGEFAULT -> PFN   1 PA 0x0000000d Replaced:1

FINALSTATS hits 0 faults 5 hitrate 0.00
EOF

#
# Check results
#
diff $EOUT $OUT >> $LOG
echo "---------" >> $LOG

diff $EOUT $OUT >/dev/null && echo "PASS $TEST" || echo "FAIL $TEST"
