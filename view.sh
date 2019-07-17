#!/usr/bin/env bash

feh --reload 2 output.png &
./get_album_cover.py > /dev/null
