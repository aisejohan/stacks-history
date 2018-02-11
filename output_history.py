# Get detailed information out of the Stacks project history
from definitions_history import *
from functions_history import *
from print_functions_history import *

H = load_back('9c7d793a723c2b531525ddd55fde6f42220af1af')

#print_history_stats(H)
#print_particular_history(H, 'algebra', 'lemma-NAK')
print_all_of_histories(H)
