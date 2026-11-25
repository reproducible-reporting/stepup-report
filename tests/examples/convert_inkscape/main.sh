#!/usr/bin/env -S bash -x
source ../example.rc

# Run the example
sb -w -j 1 & # > current_stdout.txt &

# Get the graph after completion of the pending steps.
stepup wait
stepup graph current_graph

# Reproducibility test
mv final.pdf final1.pdf
mv glasses.png glasses1.png
stepup wait -d final.pdf
stepup wait -d glasses.png
stepup rebuild
stepup join
cmp glasses.png glasses1.png
cmp final.pdf final1.pdf

# Wait for background processes, if any.
wait

# Check files that are expected to be present and/or missing.
[[ -f plan.py ]] || exit 1
[[ -f smile.svg ]] || exit 1
[[ -f final.pdf ]] || exit 1
[[ -f final1.pdf ]] || exit 1
