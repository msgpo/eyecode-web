#/bin/bash

if [ -z "$1" ]
then
    print "Usage: invert_image.sh <path>"
    exit 1
fi

convert -negate "$1" "$1"
