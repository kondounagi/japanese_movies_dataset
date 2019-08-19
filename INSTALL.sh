#!/bin/sh

_readlink () {
	perl -MCwd -le 'print Cwd::realpath shift' "$0"
}

V () {
	# shellcheck disable=SC2183,SC2046
	printf "%03d%03d%03d" $(echo "$1" | tr '.' ' ');
}

cd "$(dirname "$(_readlink "$0")")" || exit 1


py_version=$(python -c 'import platform; print(platform.python_version())')
if test "$(V "$py_version")" -lt "$(V 3)"; then
	(
		echo "This script requires at least Python3";
		echo "Your python version: $py_version";
	) >&2
	exit 1
fi

if ! command -v mecab 2>/dev/null; then
	(
		echo "Please install MeCab";
	) >&2
	exit 1;
fi


# https://github.com/neologd/mecab-ipadic-neologd#how-to-installupdate-mecab-ipadic-neologd
echo 'Installing mecab-ipadic-neologd...'
neologd_repo="https://github.com/neologd/mecab-ipadic-neologd.git"
git clone --depth 1 "$neologd_repo" 2>/dev/null
( cd mecab-ipadic-neologd && ./bin/install-mecab-ipadic-neologd -n -y; )

echo 'Creating local venv...'
python -m venv ./local || exit 1
. ./local/bin/activate || exit 1

trap 'deactivate' 0 1 2 3 15
pip install -U pip
pip install -r "requirements.txt"

echo 'Complete🎉'
echo "Now you can activate venv by: . $PWD/local/bin/activate"
