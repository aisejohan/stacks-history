# Get detailed information out of the Stacks project history
import subprocess
import re
import Levenshtein
import copy
import cPickle as pickle
import os

# For the moment we only look at these environments in the latex source files
with_proofs = ['lemma', 'proposition', 'theorem']
without_proofs = ['definition', 'example', 'exercise', 'situation', 'remark', 'remarks']

# location of the stacks-project folder associated to stacks-website/ (relative to this file)
websiteProject = "../stacks-project"

# each of these will collect the following data
# name texfile, type, latex_label, tag,
# line_nr of begin{env}, line_nr of end{env}, text of env,
# line_nr of begin{proof}, line_nr of end{proof}, text of proof
class env_with_proof:
	def __init__(self, name, type, label, tag, b, e, text, bp, ep, proof):
		self.name = name
		self.type = type
		self.label = label
		self.tag = tag
		self.b = b
		self.e = e
		self.text = text
		self.bp = bp
		self.ep = ep
		self.proof = proof


def print_with(With):
	print With.name
	print With.type
	print With.label
	print With.tag
	print With.b
	print With.e
	print With.text.rstrip()
	print With.bp
	print With.ep
	print With.proof.rstrip()


# each of these will collect the following data
# name texfile, type, latex_label, tag,
# line_nr of begin{env}, line_nr of end{env}, text of env
class env_without_proof:
	def __init__(self, name, type, label, tag, b, e, text):
		self.name = name
		self.type = type
		self.label = label
		self.tag = tag
		self.b = b
		self.e = e
		self.text = text


def print_without(Without):
	print Without.name
	print Without.type
	print Without.label
	print Without.tag
	print Without.b
	print Without.e
	print Without.text.rstrip()


def print_env(env):
	if env.type in with_proofs:
		print_with(env)
		return
	if env.type in without_proofs:
		print_without(env)
		return
	print "Unknown type!"
	exit(1)

# Storing history of an env
# commit and env are current (!)
# commits is a list of the commits that changed our env
# here 'change' means anything except for moving the text
# envs is the list of states of the env during those commits
class env_history:
	def __init__(self, commit, env, commits, envs):
		self.commit = commit
		self.env = env
		self.commits = commits
		self.envs = envs

# overall history
# commit is current commit
# env_histories is a list of env_history objects
# commits is list of previous commits with
# commits[0] the initial one
class history:
	def __init__(self, commit, env_histories, commits):
		self.commit = commit
		self.env_histories = env_histories
		self.commits = commits

def print_history_stats(History):
	print "We are at commit: " + History.commit
	print "We have done " + str(len(History.commits)) + " previous commits:"
	print "We have " + str(len(History.env_histories)) + " histories"
	names = {}
	types = {}
	d = 0
	for env_h in History.env_histories:
		name = env_h.env.name
		if name in names:
			names[name] += 1
		else:
			names[name] = 1
		type = env_h.env.type
		if type in types:
			types[type] += 1
		else:
			types[type] = 1
		if len(env_h.commits) > d:
			d = len(env_h.commits)
	print
	print "Maximum depth is: " + str(d)
	print
	for name in names:
		print "We have " + str(names[name]) + " in " + name
	print
	for type in types:
		print "We have " + str(types[type]) + " of type " + type

# Print identifiers env on one line
def print_one_line(env):
	if env.type in without_proofs:
		print (env.name + ', ' + env.type + ', ' + env.label + ', ' + env.tag +
			', ' + str(env.b) + ', ' + str(env.e))
	if env.type in with_proofs:
		print (env.name + ', ' + env.type + ', ' + env.label + ', ' + env.tag +
			', ' + str(env.b) + ', ' + str(env.e) + ', ' + str(env.bp) + ', ' + str(env.ep))

# Print a history
def print_env_history(env_h):
	print "Commit: "
	print env_h.commit
	print "Environment: "
	print_env(env_h.env)
	print "Commits: "
	for commit in env_h.commits:
		print commit
	print "Environments: "
	for env in env_h.envs:
		print_env(env)

# Just the stats, really
def print_all_of_histories(History):
	print "We are at commit: " + History.commit
	print "We have done " + str(len(History.commits)) + " previous commits:"
	for commit in History.commits:
		print commit
	print "We have " + str(len(History.env_histories)) + " histories"
	for env_h in History.env_histories:
		print '--------------------------------------------------------------------------'
		envs = env_h.envs
		commits = env_h.commits
		if not len(commits) == len(envs):
			print "Error: Unequal lengths of commits and envs!"
			exit(1)
		i = 0
		while i < len(commits):
			commit = commits[i]
			print "Commit: " + commit
			i = i + 1
		print 'Current commit: ' + env_h.commit
		i = 0
		while i < len(envs):
			print_one_line(envs[i])
			i = i + 1
		print_one_line(env_h.env)
		if not env_h.env.text == envs[-1].text:
			print 'Different texts (should not happen).'


# Loading a history from histories/
def load_back(commit):
	path = 'histories/' + commit
	fd = open(path, 'rb')
	History = pickle.load(fd)
	fd.close()
	return History


user_input_commit = raw_input("Which commit do you want to print?\n")

if not os.path.isfile("histories/" + user_input_commit):
	print "ERROR: This commit does not exist in histories/"
	exit(1)

H = load_back(user_input_commit)
print_all_of_histories(H)
