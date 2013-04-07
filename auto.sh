#!/bin/bash

echo [start] `date` >> log
python bot.py cmd.everytime.py cmd.schedule.py &> tmp/log
cat tmp/log >> log
echo [end] `date` >> log

exit 0 
