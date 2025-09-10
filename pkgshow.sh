#!/usr/bin/env bash
set -euo pipefail

# take first arg or stdin
if [[ -n "${1-}" ]]; then
    pkname="$1"
else
    read -r pkname
fi

pushd /tmp >/dev/null

if [[ ! -d "$pkname" ]]; then
    yay -G "$pkname"
fi

cat "$pkname/PKGBUILD"

popd >/dev/null
