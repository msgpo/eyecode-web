#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: echojava.sh file.java"
    exit 1
fi

javac -nowarn "$1" &> /dev/null || exit 1
java Program
rm *.class
