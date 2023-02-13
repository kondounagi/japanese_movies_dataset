#!/bin/sh

_readlink () {
	perl -MCwd -le 'print Cwd::realpath shift' "$0"
}

cd "$(dirname "$(_readlink "$0")")" || exit 1


if ! command -v mecab 2>/dev/null; then
	(
		echo "Please install MeCab";
	) >&2
	exit 1;
fi

if ! command -v lightgbm 2>/dev/null; then
	(
		echo "Please install lightgbm";
	) >&2
	exit 1;
fi

# https://github.com/neologd/mecab-ipadic-neologd#how-to-installupdate-mecab-ipadic-neologd
echo 'Installing mecab-ipadic-neologd...'
neologd_repo="https://github.com/neologd/mecab-ipadic-neologd.git"
git clone --depth 1 "$neologd_repo" 2>/dev/null
( cd mecab-ipadic-neologd && ./bin/install-mecab-ipadic-neologd -n -y; )

echo 'Creating local venv...'
python3 -m venv ./local || exit 1
. ./local/bin/activate || exit 1

trap 'deactivate' 0 1 2 3 15
pip install -U pip
pip install -r "requirements.txt"

echo 'Complete🎉'
echo "Now you can activate venv by: . $PWD/local/bin/activate"
