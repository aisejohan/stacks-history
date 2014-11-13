# Get detailed information out of the Stacks project history
import subprocess
import re
import Levenshtein

# For the moment we only look at these environments in the latex source files
with_proofs = ['lemma', 'proposition', 'theorem']
without_proofs = ['definition', 'example', 'exercise', 'situation', 'remark', 'remarks']


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

# Get tex file names out of list of files
def get_names(temp):
	names = []
	# Get rid of files in subdirectories
	# Get rid of non-tex files
	# Get rid of the .tex ending
	for i in range(0, len(temp)):
		file_name = temp[i]
		if file_name.find('/') >= 0:
			continue
		if '.tex' not in file_name:
			continue
		names.append(file_name[:-4])
	return names


# List files in given commit
def get_names_commit(commit):
	temp = subprocess.check_output(["git", "-C", "stacks-project", "ls-tree", "--name-only", commit])
	return get_names(temp.splitlines())


# Does a file exist at a given commit in stacks-project
def exists_file(filename, commit):
	if subprocess.check_output(["git", "-C", "stacks-project", "ls-tree", '--name-only', commit, '--', filename]):
		return True
	return False

# Get a file at given commit in stacks-project
# Assumes the file exists
def get_file(filename, commit):
	return subprocess.check_output(["git", "-C", "stacks-project", "cat-file", '-p', commit + ':' + filename])

# Finds all environments in stacks-project/name.tex at given commit
# and returns it as a pair [envs_with_proofs, envs_without_proofs]
# of lists of classes as above
def get_envs(name, commit):

	# We will store all envs in the following list
	envs = []

	# Check if the file exists, if not exit
	if not exists_file(name + '.tex', commit):
		return []

	# Initialize an empty environment with proof
	With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
	# Initialize an empty environment without proof
	Without = env_without_proof('', '', '', '', 0, 0, '')

	# Use splitlines(True) to keep line endings
	texfile = get_file(name + '.tex', commit).splitlines(True)

	line_nr = 0
	in_with = 0
	need_proof = 0
	in_proof = 0
	in_without = 0
	for line in texfile:
		line_nr = line_nr + 1

		if in_proof:
			With.proof += line
			if line.find('end{proof}') >= 0:
				With.ep = line_nr
				in_proof = 0
				envs.append(With)
				With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')

		if in_with:
			With.text += line
			if line.find('end{' + With.type + '}') >= 0:
				With.e = line_nr
				need_proof = 1
				in_with = 0

		if in_without:
			Without.text += line
			if line.find('end{' + Without.type + '}') >= 0:
				Without.e = line_nr
				in_without = 0
				envs.append(Without)
				Without = env_without_proof('', '', '', '', 0, 0, '')

		if line.find('begin{') >= 0:

			# Ignore a proof if we do not need one
			if need_proof and line.find('begin{proof}') >= 0:
				With.proof = line
				With.bp = line_nr
				in_proof = 1
				need_proof = 0

			for type in with_proofs:
				if line.find('begin{' + type + '}') >= 0:
					# wipe out unfinished environment
					if in_with:
						With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
						in_with = 0
					# no proof present, but finished
					elif need_proof:
						envs.append(With)
						With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
						need_proof = 0
					# unfinished proof for finished environment
					elif in_proof:
						With.bp = 0
						With.ep = 0
						With.proof = ''
						envs.append(With)
						With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
						in_proof = 0
					# wipe out unfinished environment
					if in_without:
						Without = env_without_proof('', '', '', '', 0, 0, '')
						in_without = 0
					With.name = name
					With.type = type
					if not With.label == '':
						print "Label with already present"
						exit(1) # check logic
					With.b = line_nr
					With.text = line
					in_with = 1

			for type in without_proofs:
				if line.find('begin{' + type + '}') >= 0:
					# wipe out unfinished environment
					if in_with:
						With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
						in_with = 0
					# no proof yet but a definition or such in between lemma and proof allowed
					elif need_proof:
						pass
					# unfinished proof for finished environment
					elif in_proof:
						With.bp = 0
						With.ep = 0
						With.proof = ''
						envs.append(With)
						With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
						in_proof = 0
					# wipe out unfinished environment
					if in_without:
						Without = env_without_proof('', '', '', '', 0, 0, '')
						in_without = 0
					Without.name = name
					Without.type = type
					if not Without.label == '':
						print "Label without already present"
						exit(1) # check logic
					Without.text = line
					Without.b = line_nr
					in_without = 1

		# Only first label gets picked
		if (in_with and With.label == '') or (in_without and Without.label == ''):
			n = line.find('\\label{')
			if n >= 0:
				n = n + 6
				m = line.find('}', n)
				label = line[n + 1 : m]
				if in_with:
					With.label = label
				else:
					Without.label = label

	# Clean up
	# wipe out unfinished environment
	if in_with:
		With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
		in_with = 0
	# no proof
	elif need_proof:
		envs.append(With)
		With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
		need_proof = 0
	# unfinished proof for finished environment
	elif in_proof:
		With.bp = 0
		With.ep = 0
		With.proof = ''
		envs.append(With)
		With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
		in_proof = 0
	# wipe out unfinished environment
	if in_without:
		Without = env_without_proof('', '', '', '', 0, 0, '')
		in_without = 0
	return envs


# Finds all tags if there are any
def find_tags(commit):
	tags = []

	# Check if there are tags
	if not exists_file('tags/tags', commit):
		return tags

	tagsfile = get_file('tags/tags', commit).splitlines()

	for line in tagsfile:
		if not line.find('#') == 0:
			tags.append(line.split(","))

	return tags


# Finds all commits in stacks-project
def find_commits():
	commits = subprocess.check_output(["git", "-C", "stacks-project", "log", "--pretty=format:%H", "master"])
	# Reverse the list so that 0 is the first one
	return commits.splitlines()[::-1]


# gets next commit
def next_commit(commit):
	commits = find_commits()
	i = 0
	while i < len(commits) - 1:
		if commit == commits[i]:
			return commits[i + 1]
		i = i + 1
	print "There is no next commit!"
	return ''


# Get diff between two commits in a given file
# commit_before should be prior in history to commit_after
def get_diff_in(name, commit_before, commit_after):
	diff = subprocess.check_output(["git", "-C", "stacks-project", "diff", "--patience", "-U0", commit_before + '..' + commit_after, '--', name + '.tex'])
	return diff.splitlines()


# Regular expressions to parse diffs
two_commas = re.compile('\@\@\ \-([0-9]*)\,([0-9]*)\ \+([0-9]*)\,([0-9]*)\ \@\@')
first_comma = re.compile('\@\@\ \-([0-9]*)\,([0-9]*)\ \+([0-9]*)\ \@\@')
second_comma = re.compile('\@\@\ \-([0-9]*)\ \+([0-9]*)\,([0-9]*)\ \@\@')
no_comma = re.compile('\@\@\ \-([0-9]*)\ \+([0-9]*)\ \@\@')


# Gets a list of line_nr changes between two commits
# in a given file
# commit_before should be prior in history to commit_after
def get_changes_in(name, commit_before, commit_after):

	diff = get_diff_in(name, commit_before, commit_after)

	lines_removed = []
	lines_added = []

	for line in diff:
		if line.find('@@') == 0:
			# The line looks like
			# @@ -(old line nr),d +(new line nr),a @@
			# meaning 5 lines where removed from old file starting at
			# old line nr and a lines were added started at new line nr
			# Variant: ',d' is missing if d = 1
			# Variant: ',a' is missing if a = 1
			# total of 4 cases matching the regular expressions compiled above

			result = two_commas.findall(line)

			if len(result) == 1 and len(result[0]) == 4:
				lines_removed.append([int(result[0][0]), int(result[0][1])])
				lines_added.append([int(result[0][2]), int(result[0][3])])
				continue

			result = first_comma.findall(line)

			if len(result) == 1 and len(result[0]) == 3:
				lines_removed.append([int(result[0][0]), int(result[0][1])])
				lines_added.append([int(result[0][2]), 1])
				continue

			result = second_comma.findall(line)

			if len(result) == 1 and len(result[0]) == 3:
				lines_removed.append([int(result[0][0]), 1])
				lines_added.append([int(result[0][1]), int(result[0][2])])
				continue

			result = no_comma.findall(line)

			if len(result) == 1 and len(result[0]) == 2:
				lines_removed.append([int(result[0][0]), 1])
				lines_added.append([int(result[0][1]), 1])
				continue

			print "Unexpected format of following diff line: "
			print line
			exit(1)

	return [lines_removed, lines_added]


# Gets a list of files changed between two commits
# commit_before should be prior in history to commit_after
def get_names_changed(commit_before, commit_after):
	temp = subprocess.check_output(["git", "-C", "stacks-project", "diff", "--name-only", commit_before + '..' + commit_after])
	return get_names(temp.splitlines())


# Gets a list of line_nr changes between two commits
# commit_before should be prior in history to commit_after
def get_all_changes(commit_before, commit_after):

	all_changes = {}

	files_changed = get_names_changed(commit_before, commit_after)

	for name in files_changed:
		all_changes[name] = get_changes_in(name, commit_before, commit_after)

	return all_changes


# Regular expression matching removed and added tags
deleted_tag = re.compile('^\-([0-9A-Z]{4})\,(.*)')
added_tag = re.compile('^\+([0-9A-Z]{4})\,(.*)')


# Gets a list of tag changes between two commits
# commit_before should be prior in history to commit_after
def get_tag_changes(commit_before, commit_after):

	tags_removed = []
	tags_added = []

	diff = subprocess.check_output(["git", "-C", "stacks-project", "diff", "--patience", "-U0", commit_before + '..' + commit_after, '--', 'tags/tags'])
	diff = diff.splitlines()

	for line in diff:
		deleted = deleted_tag.findall(line)
		if len(deleted) > 0:
			tags_removed.append([deleted[0][0], deleted[0][1]])
		added = added_tag.findall(line)
		if len(added) > 0:
			tags_added.append([added[0][0], added[0][1]])

	return [tags_removed, tags_added]


# Find tags whose labels got changed
def tags_changed_labels(tag_changes):
	tags_changed = []
	tags_removed = tag_changes[0]
	tags_added = tag_changes[1]
	n = len(tags_removed)
	m = len(tags_added)
	i = 0
	j = 0
	while (i < n) and (j < m):
		if tags_removed[i][0] == tags_added[j][0]:
			tags_changed.append([tags_removed[i][0], tags_removed[i][1], tags_added[i][1]])
			i = i + 1
			continue
		if tags_removed[i][0] < tags_added[j][0]:
			i = i + 1
			continue
		j = j + 1
	return tags_changed


# Print changes functions
def print_diff(diff):
	for line in diff:
		print line

def print_changes(changes):
	lines_removed = changes[0]
	lines_added = changes[1]
	print "Removed:"
	for line, count in lines_removed:
		print line, count
	print "Added:"
	for line, count in lines_added:
		print line, count

def print_all_changes(all_changes):
	for name in all_changes:
		print "In file " + name + ".tex:"
		print_changes(all_changes[name])

def print_tag_changes(tag_changes):
	print 'Removed:'
	for tag, label in tag_changes[0]:
		print tag + ',' + label
	print 'Added:'
	for tag, label in tag_changes[1]:
		print tag + ',' + label
	print 'Changed:'
	tag_mod = tags_changed_labels(tag_changes)
	for tag, oldlabel, newlabel in tag_mod:
		print tag + ' : ' + oldlabel + ' ---> ' + newlabel


# Add tags to a list of environments
# Overwrites already existing tags
def add_tags(envs, tags):
	for env in envs:
		long_label = env.name + '-' + env.label
		for tag, label in tags:
			if label == long_label:
				env.tag = tag
				continue


# Get all envs from a commit
# Should only be used for the initial commit
def get_all_envs(commit):

	all_envs = {}

	# get names
	names = get_names_commit(commit)

	# loop through tex files and add envs
	for name in names:
		all_envs[name] = get_envs(name, commit)

	return all_envs


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

# Initialize an env_history
def initial_env_history(commit, env):
	return env_history(commit, env, [commit], [env])

# Update an env_history with a given commit and env
# This replaces the current state as well!
def update_env_history(env_h, commit, env):
	# Move commit and env to the end of the lists
	env_h.commits.append(commit)
	env_h.envs.append(env)
	env_h.commit = commit
	env_h.env = env

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

def print_all_of_histories(History):
	print "We are at commit: " + History.commit
	print "We have done " + str(len(History.commits)) + " previous commits:"
	print "We have " + str(len(History.env_histories)) + " histories"
	for env_h in History.env_histories:
		print '--------------------------------------------------------------------------'
		envs = env_h.envs
		commits = env_h.commits
		if not len(commits) == len(envs):
			print "Error: Unequal lengths of commits and envs!"
			exit(1)
		print 'LENGTH = ' + str(len(envs))
		print '--------------------------------------------------------------------------'
		i = 0
		while i < len(commits):
			commit = commits[i]
			env = envs[i]
			print "Commit: " + commit
			print_env(env)
			i = i + 1

# Initialize history
def initial_history():
	initial_commit = '3d32323ff9f1166afb3ee0ecaa10093dc764a50d'
	all_envs = get_all_envs(initial_commit)
	env_histories = []
	# there are no tags present so we do not need to add them
	for name in all_envs:
		for env in all_envs[name]:
			env_h = initial_env_history(initial_commit, env)
			env_histories.append(env_h)
	return history(initial_commit, env_histories, [])

# Logic for pairs: return
#	-1 if start + nr - 1 < b
#	0  if intervals meet
#	1  if e < start
def logic_of_pairs(start, nr, b, e):
	# If nr = 0, then change starts at start + 1
	if nr == 0:
		if start < b:
			return -1
		if e <= start:
			return 1
		return 0
	# now nr > 0 so change starts at start and ends at start + nr - 1
	if e < start:
		return 1
	if start + nr - 1 < b:
		return -1
	return 0

# Compute shift
def compute_shift(lines_removed, lines_added, i):
	if lines_removed[i][1] > 0 and lines_added[i][1] > 0:
		return lines_added[i][0] + lines_added[i][1] - lines_removed[i][0] - lines_removed[i][1]
	if lines_removed[i][1] == 0:
		return lines_added[i][0] + lines_added[i][1] - lines_removed[i][0] - 1
	if lines_added[i][1] == 0:
		return lines_added[i][0] + 1 - lines_removed[i][0] - lines_removed[i][1]
	print "Should not happen!"
	exit(1)

# See if env from commit_before is changed
# If not changed, but moved inside file, then update line numbers
def env_before_is_changed(env, all_changes):
	if not env.name in all_changes:
		return False
	lines_removed = all_changes[env.name][0]
	lines_added = all_changes[env.name][1]
	i = 0
	while i < len(lines_removed):
		start =  lines_removed[i][0]
		nr = lines_removed[i][1]
		position = logic_of_pairs(start, nr, env.b, env.e)
		if position == 0:
			return True
		if position == 1:
			break
		i = i + 1

	# adjust line numbers; i is index of chunk just beyond env
	if i > 0:
		shift = compute_shift(lines_removed, lines_added, i - 1)
		env.b = env.b + shift
		env.e = env.e + shift

	if env.type in without_proofs:
		return False
	if env.proof == '':
		return False

	# The proof could still be after the chunk we are at
	while i < len(lines_removed):
		start =  lines_removed[i][0]
		nr = lines_removed[i][1]
		position = logic_of_pairs(start, nr, env.bp, env.ep)
		if position == 0:
			return True
		if position == 1:
			break
		i = i + 1

	# adjust line numbers; i is the index of chunk just beyond proof of env
	if i > 0:
		shift = compute_shift(lines_removed, lines_added, i - 1)
		env.bp = env.bp + shift
		env.ep = env.ep + shift

	return False

# See if env from commit_after is new or changed
def env_after_is_changed(env, all_changes):
	if not env.name in all_changes:
		return False
	lines_added = all_changes[env.name][1]
	for start, nr in lines_added:
		if logic_of_pairs(start, nr, env.b, env.e) == 0:
			return True
	if env.type in without_proofs:
		return False
	if env.proof == '':
		return False
	for start, nr in lines_added:
		if logic_of_pairs(start, nr, env.bp, env.ep) == 0:
			return True
	return False


# Simplest kind of match: name, label, type all match
def label_match(env_b, env_a):
	if (env_b.name == env_a.name and env_b.type == env_a.type and env_b.label == env_a.label and not env_a.label == ''):
		print "MATCH name, type, label!"
		return True
	return False

# Match text statement exactly when no labels present
# We also need to match the file as there is an example
# where the exact same statement occurs in different files.
def text_match(env_b, env_a):
	if env_b.label == '' and env_a.name == env_b.name and env_a.text == env_b.text:
		print "Match name, text, no label!"
		return True
	return False
	

# Match where label got changed and we recorded this in the tags file
# This should be very rare and mostly work
def tag_mod_match(env_b, env_a, tag_mod):
	for tag, label_b, label_a in tag_mod:
		if (env_b.name + '-' + env_b.label == label_b and env_a.name + '-' + env_a.label == label_a):
			print "MATCH by label change in tags/tags!"
			if not env_b.tag == tag:
				print "Warning: nonexistent or incorrect tag where there should be one!"
				print tag
				print env_b.tag
				print env_a.tag
				print label_b
				print label_a
				print "Guess: due to a double label!"
				return False
			return True
	return False

# Closeness score
def closeness_score(env_b, env_a):
	score = 0
	if env_b.name == env_a.name:
		score = score + 0.05
	if env_b.type == env_a.type:
		score = score + 0.05
	if env_b.label == env_a.label and not env_b.label == '':
		score = score + 0.1
	return(score + Levenshtein.ratio(env_b.text, env_a.text))

# Checking similarity of histories with the same label
def too_similar(History, name, label):
	i = 0
	while i < len(History.env_histories):
		i_env = History.env_histories[i].env
		if i_env.name == name and i_env.label == label:
			j = i + 1
			while j < len(History.env_histories):
				j_env = History.env_histories[j].env
				if j_env.name == name and j_env.label == label:
					if i_env.b <= j_env.b and j_env.b <= i_env.e:
						return True
					if i_env.b <= j_env.e and j_env.e <= i_env.e:
						return True
					# Can add test for overlap proofs too
				j = j + 1
		i = i + 1
	return False

# Check line numbers agree
def same_line_nrs(A, B):
	if not (A.b == B.b and A.e == B.e):
		return False
	if A.type in without_proofs:
		return True
	if not (A.bp == B.bp and A.ep == B.ep):
		return False
	return True

# Types we do not look at for history
def wrong_type(label, names):
	for type in ['equation', 'section', 'subsection', 'subsubsection', 'item']:
		if label.find(type) >= 0:
			for name in names:
				if label.find(name + '-' + type) == 0:
					return True
	return False


# Find doubles
def find_doubles(word, word_list, double):
	if word in word_list:
		double.append(word)
		return True
	word_list.append(word)
	return False

# Quick test
def env_in_history(env, History):
	for env_h in History.env_histories:
		e = env_h.env
		if env.name == e.name and env.b == e.b:
			return True
	return False

# Insert a score in list of scores
def insert_score(score, i, j, scores):
	a = 0
	while a < len(scores) and score < scores[a][0]:
		a = a + 1
	scores.insert(a, [score, i, j])

# User interface
def do_these_match(env_b, env_a):
	print '----------------------------------------'
	print_without(env_b)
	print '----------------------------------------'
	print_without(env_a)
	while True:
		choice = raw_input('Do these match? (y/n): ')
		if choice == 'n':
			return False
		if choice == 'y':
			return True


# Main function, going from history for some commit to the next
#
# Problem we ignore for now: history is not linear
#
def update_history(History):
	commit_before = History.commit
	commit_after = next_commit(commit_before)
	all_changes = get_all_changes(commit_before, commit_after)

	# List of env_histories which are being changed in this commit
	envs_h_b = []
	for env_h in History.env_histories:
		env = env_h.env
                # The following line
		#	updates line numbers of env if not changed
		#	passes if env is changed
		if env_before_is_changed(env, all_changes):
			envs_h_b.append(env_h)

	# List of new or changed envs in this commit
	envs_a = []
	for name in all_changes:
		envs = get_envs(name, commit_after)
		for env in envs:
			# The following line passes if env is changed
			if env_after_is_changed(env, all_changes):
				envs_a.append(env)

	# Get tag changes
	tag_changes = get_tag_changes(commit_before, commit_after)
	tag_del = tag_changes[0]
	tag_new = tag_changes[1]
	tag_mod = tags_changed_labels(tag_changes)

	# Try to match environments between changes
	# First time through
	matches = []
	matches_b = set()
	matches_a = set()
	i = 0
	while i < len(envs_h_b):
		env_b = envs_h_b[i].env
		j = 0
		while j < len(envs_a):
			if j in matches_a:
				j = j + 1
				continue
			env_a = envs_a[j]
			# Catch the following types of matches:
			#	name + '-' + label
			#	text
			#	change label in tags/tags which also correspond to edit
			if label_match(env_b, env_a):
				matches.append([i, j])
				matches_b.add(i)
				matches_a.add(j)
				break
			j = j + 1
		i = i + 1

	# Second time through compute scores
	scores = []
	i = 0
	while i < len(envs_h_b):
		if i in matches_b:
			i = i + 1
			continue
		env_b = envs_h_b[i].env
		j = 0
		while j < len(envs_a):
			if j in matches_a:
				j = j + 1
				continue
			env_a = envs_a[j]
			score = closeness_score(env_b, env_a)
			if score > 1.00:
				print "MATCH by score: " + str(score)
				matches.append([i, j])
				matches_b.add(i)
				matches_a.add(j)
			else:
				insert_score(score, i, j, scores)
			j = j + 1
		i = i + 1
	
	top = 0
	while top < len(scores) and scores[top][0] > 0.8:
		top = top + 1
	
	a = 0
	while a < top:
		score = scores[a][0]
		i = scores[a][1]
		j = scores[a][2]
		if not (i in matches_b or j in matches_a):
			print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
			print "There are " + str(len(envs_h_b) - len(matches)) + " left before and " + str(top - a) + " choices left."
			print
			print
			print "MATCH by score: " + str(score)
			if do_these_match(envs_h_b[i].env, envs_a[j]):
				matches.append([i, j])
				matches_b.add(i)
				matches_a.add(j)
		a = a + 1

	# Add tags to new envs; this rarely does anything
	add_tags(envs_a, tag_new)

	for i, j in matches:
		# carry over the tag if there is one before and not yet after
		if envs_a[j].tag == '' and not envs_h_b[i].env.tag == '':
			envs_a[j].tag = envs_h_b[i].env.tag
		# update environment history
		update_env_history(envs_h_b[i], commit_after, envs_a[j])
	
	i = 0
	while i < len(envs_h_b):
		if i in matches_b:
			i = i + 1
			continue
		if not envs_h_b[i].env.label == '':
			print "Removing: " + envs_h_b[i].env.name + '-' + envs_h_b[i].env.label
		else:
			print "Removing: " + envs_h_b[i].env.name
		History.env_histories.remove(envs_h_b[i])
		i = i + 1

	# Add left over newly created envs to History
	j = 0
	while j < len(envs_a):
		if j in matches_a:
			j = j + 1
			continue
		env_a = envs_a[j]
		env_h = initial_env_history(commit_after, env_a)
		History.env_histories.append(env_h)
		j = j + 1

	# add tags to envs
	names = get_names_commit(commit_after)
	new_labels = {}
	for tag, label in tag_new:
		if wrong_type(label, names):
			continue
		new_labels[label] = tag

	# add new tags to histories if necessary
	for env_h in History.env_histories:
		env = env_h.env
		label = env.name + '-' + env.label
		if label in new_labels:
			tag = new_labels[label]
			# Already there, then done
			if env.tag == tag:
				continue
			# If there is a tag but it is not the same
			if not env.tag == '':
				print 'Warning: changing' + env.tag + ' to ' + tag
			if not env_h.commit == commit_after:
				# Here a new step in history required
				if not env_h.commit == commit_before:
					print "Warning: incorrect commit in environment history."
				# set or change tag
				env.tag = tag
				update_env_history(env_h, commit_after, env)
			else:
				# Here we need to retroactively update the tag
				env_h.envs[-1].tag = tag
				env_h.env.tag = tag
		else:
			# Finally update commit on environment history
			env_h.commit = commit_after

	# Change current commit
	History.commits.append(commit_before)
	History.commit = commit_after


# Testing, testing

History = initial_history()
print
print_history_stats(History)

for i in range(1000):
	update_history(History)
	print
	print "Finished with commit: " + History.commit
	# print_history_stats(History)

