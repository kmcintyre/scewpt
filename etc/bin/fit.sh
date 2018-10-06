#!/bin/bash
for f in *.svg
do
	echo `basename $f`	 
	rsvg-convert `basename $f` -h 25 -f svg -o '../logo/'`basename $f`
done