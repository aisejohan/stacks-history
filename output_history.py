# Get detailed information out of the Stacks project history
from definitions_history import *
from functions_history import *
from print_functions_history import *
import os

user_input_commit = input("Which commit do you want to print?\n")
if not os.path.isfile("histories/" + user_input_commit):
	print("ERROR: This commit does not exist in histories/")
	exit(1)

H = load_back(user_input_commit)

#print_history_stats(H)
#print_particular_history(H, 'algebra', 'lemma-NAK')
print_all_of_histories(H)
