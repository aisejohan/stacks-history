# Printing functions


# print env with a proof
def print_with(With):
	print(With.name + '.tex, ' + With.label + ', ' + With.tag)
	print(With.text.rstrip())
	print(With.proof.rstrip())


# print env without a proof
def print_without(Without):
	print(Without.name + '.tex, ' + Without.label + ', ' + Without.tag)
	print(Without.text.rstrip())


# print env
def print_env(env):
	if hasattr(env, "proof"):
		print_with(env)
	else:
		print_without(env)


# Print identifiers env on one line
def print_one_line(env):
	if not hasattr(env, "proof"):
		print((env.name + ', ' + env.type + ', ' + env.label + ', ' + env.tag +
			', ' + str(env.b) + ', ' + str(env.e)))
	else:
		print((env.name + ', ' + env.type + ', ' + env.label + ', ' + env.tag +
			', ' + str(env.b) + ', ' + str(env.e) + ', ' + str(env.bp) + ', ' + str(env.ep)))


# Print a history
def print_env_history(env_h):
	print("Commit: ")
	print(env_h.commit)
	print("Environment: ")
	print_env(env_h.env)
	print("Commits: ")
	for commit in env_h.commits:
		print(commit)
	print("Environments: ")
	for env in env_h.envs:
		print_env(env)


# latex printing of a history
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
		print('\\bigskip\\noindent')
		print('{\\bf Commit:} ' + env_h.commits[i] + '\\hfill\\break')
		print_env(env_h.envs[i])
		i = i + 1
	print('\\end{document}')


# Print all commits affecting each piece of history
def print_all_of_histories(History):
	print("We are at commit: " + History.commit)
	print("We have done " + str(len(History.commits)) + " previous commits:")
	for commit in History.commits:
		print(commit)
	print("We have " + str(len(History.env_histories)) + " histories")
	for env_h in History.env_histories:
		print('--------------------------------------------------------------------------')
		envs = env_h.envs
		commits = env_h.commits
		if not len(commits) == len(envs):
			print("Error: Unequal lengths of commits and envs!")
			exit(1)
		i = 0
		while i < len(commits):
			commit = commits[i]
			print("Commit: " + commit)
			i = i + 1
		print('Current commit: ' + env_h.commit)
		i = 0
		while i < len(envs):
			print_one_line(envs[i])
			i = i + 1
		print_one_line(env_h.env)
		if not env_h.env.text == envs[-1].text:
			print('Different texts (should not happen).')


# print stats of all histories
def print_history_stats(History):
	print("We are at commit: " + History.commit)
	print("We have done " + str(len(History.commits)) + " previous commits:")
	print("We have " + str(len(History.env_histories)) + " histories")
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
	print()
	print("Maximum depth is: " + str(d))
	print()
	for name in names:
		print("We have " + str(names[name]) + " in " + name)
	print()
	for type in types:
		print("We have " + str(types[type]) + " of type " + type)


# print a diff
def print_diff(diff):
	for line in diff:
		print(line)


# Print changes
def print_changes(changes):
	lines_removed = changes[0]
	lines_added = changes[1]
	print("Removed:")
	for line, count in lines_removed:
		print(line, count)
	print("Added:")
	for line, count in lines_added:
		print(line, count)

# print all changes
def print_all_changes(all_changes):
	for name in all_changes:
		print("In file " + name + ".tex:")
		print_changes(all_changes[name])

# print changes in tags
def print_tag_changes(tag_changes):
	print('Removed:')
	for tag, label in tag_changes[0]:
		print(tag + ',' + label)
	print('Added:')
	for tag, label in tag_changes[1]:
		print(tag + ',' + label)
	print('Changed:')
	tag_mod = tags_changed_labels(tag_changes)
	for tag, oldlabel, newlabel in tag_mod:
		print(tag + ' : ' + oldlabel + ' ---> ' + newlabel)


