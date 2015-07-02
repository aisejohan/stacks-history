from history import *

# Uncomment the next two lines if you want to start from scratch
#do_it_all()
#exit(0)

commit = raw_input("Which commit do you want to start with?\n")

if not os.path.isfile("histories/" + commit):
	print "ERROR: This commit does not exist in histories/"
else:
	print
	print "Running this script will remove " + commit
	yesno = raw_input("Are you sure you want to continue(yes/no)?\n")
	if not yesno == "yes":
		exit(0)
	do_it_starting_with(commit)
