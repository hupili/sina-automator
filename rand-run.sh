#!/bin/bash

while [[ 1 ]] ; do
	python bot.py
	ret=$?
	if [[ $ret != 0 ]] ; then
		exit 255
	fi
	delay=`expr $RANDOM % 5`
	echo Delay: $delay
	sleep $delay
done
