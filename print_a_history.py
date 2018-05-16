# Get detailed information out of the Stacks project history
import subprocess
import re
import Levenshtein
import copy
import cPickle as pickle
import os

with_proofs = ['lemma', 'proposition', 'theorem']
without_proofs = ['definition', 'example', 'exercise', 'situation', 'remark', 'remarks']

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

class env_without_proof:
	def __init__(self, name, type, label, tag, b, e, text):
		self.name = name
		self.type = type
		self.label = label
		self.tag = tag
		self.b = b
		self.e = e
		self.text = text

class env_history:
	def __init__(self, commit, env, commits, envs):
		self.commit = commit
		self.env = env
		self.commits = commits
		self.envs = envs

class history:
	def __init__(self, commit, env_histories, commits):
		self.commit = commit
		self.env_histories = env_histories
		self.commits = commits


def load_back(commit):
	path = 'histories/' + commit
	fd = open(path, 'rb')
	History = pickle.load(fd)
	fd.close()
	return History

def print_with(With):
	print With.name + '.tex, ' + With.label + ', ' + With.tag
	print With.text.rstrip()
	print With.proof.rstrip()

def print_without(Without):
	print Without.name + '.tex, ' +  Without.label + ', ' + Without.tag
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

def print_particular_history(History, name, label):
	print ('\\documentclass{amsart}'
		'\\usepackage{verbatim}'
		'\\newenvironment{reference}{\\comment}{\\endcomment}'
		'\\newenvironment{slogan}{\\comment}{\\endcomment}'
		'\\newenvironment{history}{\\comment}{\\endcomment}'
		'\\usepackage[all]{xy}'
		'\\xyoption{2cell}'
		'\\UseAllTwocells'
		'\\theoremstyle{plain}'
		'\\newtheorem{theorem}[subsection]{Theorem}'
		'\\newtheorem{proposition}[subsection]{Proposition}'
		'\\newtheorem{lemma}[subsection]{Lemma}'
		'\\theoremstyle{definition}'
		'\\newtheorem{definition}[subsection]{Definition}'
		'\\newtheorem{example}[subsection]{Example}'
		'\\newtheorem{exercise}[subsection]{Exercise}'
		'\\newtheorem{situation}[subsection]{Situation}'
		'\\theoremstyle{remark}'
		'\\newtheorem{remark}[subsection]{Remark}'
		'\\newtheorem{remarks}[subsection]{Remarks}'
		'\\numberwithin{equation}{subsection}'
		'\\def\\lim{\\mathop{\\rm lim}\\nolimits}'
		'\\def\\colim{\\mathop{\\rm colim}\\nolimits}'
		'\\def\\Spec{\\mathop{\\rm Spec}}'
		'\\def\\Hom{\\mathop{\\rm Hom}\\nolimits}'
		'\\def\\SheafHom{\\mathop{\\mathcal{H}\\!{\\it om}}\\nolimits}'
		'\\def\\Sch{\\textit{Sch}}'
		'\\def\\Mor{\\mathop{\\rm Mor}\\nolimits}'
		'\\def\\Ob{\\mathop{\\rm Ob}\\nolimits}'
		'\\def\\Sh{\\mathop{\\textit{Sh}}\\nolimits}'
		'\\def\\NL{\\mathop{N\\!L}\\nolimits}'
		'\\def\\proetale{{pro\\text{-}\\acute{e}tale}}'
		'\\def\\etale{{\\acute{e}tale}}'
		'\\def\\QCoh{\\textit{QCoh}}'
		'\\def\\Ker{\\text{Ker}}'
		'\\def\\Im{\\text{Im}}'
		'\\def\\Coker{\\text{Coker}}'
		'\\def\\Coim{\\text{Coim}}'
		'\\begin{document}')
	for env_h in History.env_histories:
		if env_h.env.name == name and env_h.env.label == label:
			break
	i = 0
	while i < len(env_h.commits):
		print '\\bigskip\\noindent'
		print '{\\bf Commit:} ' + env_h.commits[i] + '\\hfill\\break'
		print_env(env_h.envs[i])
		i = i + 1
	print '\\end{document}'


user_input_commit = raw_input("Which commit do you want to print?\n")

if not os.path.isfile("histories/" + user_input_commit):
       print "ERROR: This commit does not exist in histories/"
       exit(1)

History = load_back(user_input_commit)
print_particular_history(History, 'algebra', 'lemma-NAK')
