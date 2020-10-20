#!/bin/bash
set -eE

setup_version="$(python setup.py -V)"
commit_count="$(git rev-list --count --since=yesterday HEAD)"
commit_date="$(date "+%d")"

commit_version="${setup_version}.dev${commit_date}${commit_count}"

sed -i "s/SUPERVISOR_VERSION .*/SUPERVISOR_VERSION = \"${commit_version}\"/g" supervisor/const.py
echo "$commit_version"
