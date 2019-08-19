#!/bin/sh

_readlink () {
	perl -MCwd -le 'print Cwd::realpath shift' "$0"
}

_pip () {
	if command -v pip3 >/dev/null; then
		pip3 "$@"
	else
		pip "$@"
	fi
}

cd "$(dirname "$(_readlink "$0")")" || exit 1

# https://github.com/neologd/mecab-ipadic-neologd#how-to-installupdate-mecab-ipadic-neologd
neologd_repo="https://github.com/neologd/mecab-ipadic-neologd.git"
if ! git clone --depth 1 "$neologd_repo" 2>/dev/null; then
	(
		cd mecab-ipadic-neologd && ./bin/install-mecab-ipadic-neologd -n;
	)
fi

_pip install -r "requirements.txt"
