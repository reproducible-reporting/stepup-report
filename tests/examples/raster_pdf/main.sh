#!/usr/bin/env -S bash -x
source ../example.rc

# Run the example
sb -w -j 1 & # > current_stdout.txt &

# Get the graph after completion of the pending steps.
stepup wait
stepup graph current_graph

# Reproducibility test
mv rastered/smile.pdf rastered/smile1.pdf
mv rastered/smile.png rastered/smile1.png
mv rastered/double-1-2.png rastered/double1-1-2.png
stepup wait -d rastered/smile.pdf
stepup wait -d rastered/smile.png
stepup wait -d rastered/double-1-2.png
stepup rebuild
stepup join
cmp rastered/smile.pdf rastered/smile1.pdf
cmp rastered/smile.png rastered/smile1.png
cmp rastered/double-1-2.png rastered/double1-1-2.png

# Wait for background processes, if any.
wait

# Check files that are expected to be present and/or missing.
[[ -f plan.py ]] || exit 1
[[ -f smile.pdf ]] || exit 1
[[ -f rastered/smile.pdf ]] || exit 1
[[ -f rastered/smile1.pdf ]] || exit 1
[[ -f rastered/smile.png ]] || exit 1
[[ -f rastered/double-1-2.png ]] || exit 1
[[ -f rastered/double-2-2.png ]] || exit 1
