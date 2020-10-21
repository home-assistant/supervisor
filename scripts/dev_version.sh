#!/bin/bash
set -eE

commit_count="$(git rev-list --count --since=yesterday HEAD)"
calver_date="$(date "+%Y.%m.dev%d")"

calver_version="${calver_date}${commit_count}"

sed -i "s/SUPERVISOR_VERSION .*/SUPERVISOR_VERSION = \"${calver_version}\"/g" supervisor/const.py
echo "$calver_version"
