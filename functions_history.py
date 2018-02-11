# Functions used in multiple scripts
import pickle

def load_back(commit):
	path = 'histories/' + commit
	fd = open(path, 'rb')
	History = pickle.load(fd)
	fd.close()
	return History


