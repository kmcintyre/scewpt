#!/bin/bash
cd ~/scewpt/python
export PYTHONPATH=`pwd`
python scraper.py $1
if [ $? -eq 0 ]; then
    python twitter/job/compare.py $1
fi
