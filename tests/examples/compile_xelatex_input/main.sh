#!/usr/bin/env -S bash -x
source ../example.rc

# Run the example
export STEPUP_REPORT_LATEX="xelatex"
sb -w -j 1 & # > current_stdout.txt &

# Get the graph after completion of the pending steps.
stepup wait
stepup graph current_graph

# Reproducibility test
rm paper.aux
sleep 0.1
rm paper.log
sleep 0.1
rm subdir/generated.tex
sleep 0.1
rm subdir/code.txt
sleep 0.1
mv paper.pdf paper1.pdf
stepup wait -d paper.pdf
stepup wait -d subdir/generated.tex
stepup wait -d subdir/code.txt
stepup rebuild
stepup join
cmp paper.pdf paper1.pdf

# Wait for background processes, if any.
wait

# Check files that are expected to be present and/or missing.
[[ -f plan.py ]] || exit 1
[[ -f paper.pdf ]] || exit 1
[[ -f paper.log ]] || exit 1
[[ -f paper.aux ]] || exit 1
[[ -f paper1.pdf ]] || exit 1
