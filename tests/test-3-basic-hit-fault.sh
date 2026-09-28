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
Distinguish first-reference page faults from later hits, without replacement.

Command:
--------
python3 ./lobo-vm-sim.py -s 0 -a 32 -P 8 -C 3 -p FIFO -A 0,1,8,9
--------
EOF

#
# Test with LOBO
#
$PYTHON $LOBO -s 0 -a 32 -P 8 -C 3 -p FIFO -A 0,1,8,9 >$OUT 2>&1

#
# Expected output
#
cat >$EOUT << 'EOF'
ARG address space size 32
ARG page size 8
ARG frames 3
ARG policy FIFO
ARG addresses 0,1,8,9

VA 0x00000000 VPN    0 offset 0x0000 PAGEFAULT -> PFN   0 PA 0x00000000 Replaced:-
VA 0x00000001 VPN    0 offset 0x0001 HIT -> PFN   0 PA 0x00000001 Replaced:-
VA 0x00000008 VPN    1 offset 0x0000 PAGEFAULT -> PFN   1 PA 0x00000008 Replaced:-
VA 0x00000009 VPN    1 offset 0x0001 HIT -> PFN   1 PA 0x00000009 Replaced:-

FINALSTATS hits 2 faults 2 hitrate 50.00
EOF

#
# Analyze results
#
diff $EOUT $OUT >> $LOG
echo "---------" >> $LOG

diff $EOUT $OUT >/dev/null && echo "PASS $TEST" || echo "FAIL $TEST"
