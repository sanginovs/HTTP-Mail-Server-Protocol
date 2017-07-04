#invoke this script like this:
# chmod 755 stressor.bash
# (You have to do that once.)
# Then:
# 
# ./stressor.bash 20 30 50
# 
# which will run
#
# 20 copies in parallel of the rpyc-stressor.py script
# and each one with 30 users, and each user will request 50 quotes.
#
# That's what the numbers mean. 

source venv/bin/activate

	for (( c=0; c<=$1; c++ ))
	do
	(python rpyc-stressor.py $c $1 $2 $3 2>&1 ) &
	done
