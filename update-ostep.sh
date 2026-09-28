#!/bin/sh
set -eu

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

OSTEP_REPO="https://github.com/remzi-arpacidusseau/ostep-homework.git"

echo "Fetching OSTEP homework..."
git clone --depth 1 "$OSTEP_REPO" "$TMPDIR/ostep-homework"

echo "Updating vm-paging..."
rm -rf vm-paging
cp -R "$TMPDIR/ostep-homework/vm-paging" ./vm-paging

echo "Updating vm-paging-policy..."
rm -rf vm-paging-policy
cp -R "$TMPDIR/ostep-homework/vm-beyondphys-policy" ./vm-paging-policy

echo
echo "Done."
echo "Review changes with:"
echo "  git status"
echo "  git diff"

