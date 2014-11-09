# Get detailed information out of the Stacks project history
import subprocess
import re

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


# Finds all environments in stacks-project/name.tex
# and returns it as a pair [withs, withouts] of lists
# of classes as above
def find_envs(name):

	# We will store lemmas, propositions, theorems in the following list
	envs_with_proofs = []
	# Initialize an empty environment with proof
	With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')

	# We will store definitions, examples, exercises, situations, remarks,
	# and remarks's in the following list
	envs_without_proofs = []
	# Initialize an empty environment without proof
	Without = env_without_proof('', '', '', '', 0, 0, '')

	texfile = open('stacks-project/' + name + '.tex', 'r')
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
				envs_with_proofs.append(With)
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
				envs_without_proofs.append(Without)
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
						envs_with_proofs.append(With)
						With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
						need_proof = 0
					# unfinished proof for finished environment
					elif in_proof:
						With.bp = 0
						With.ep = 0
						With.proof = ''
						envs_with_proofs.append(With)
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
						envs_with_proofs.append(With)
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
		envs_with_proofs.append(With)
		With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
		need_proof = 0
	# unfinished proof for finished environment
	elif in_proof:
		With.bp = 0
		With.ep = 0
		With.proof = ''
		envs_with_proofs.append(With)
		With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')
		in_proof = 0
	# wipe out unfinished environment
	if in_without:
		Without = env_without_proof('', '', '', '', 0, 0, '')
		in_without = 0
	# close texfile
	texfile.close()
	return [envs_with_proofs, envs_without_proofs]


# Finds all tags if there are any
def find_tags():
	tags = []
	try:
		tagsfile = open("stacks-project/tags/tags", 'r')
		for line in tagsfile:
			if not line.find('#') == 0:
				tags.append(line.rstrip().split(","))
	except:
		pass
	return tags


# Finds all commits in stacks-project
def find_commits():
	commits = subprocess.check_output(["git", "-C", "stacks-project", "log", "--pretty=format:%H", "master"])
	return commits.splitlines()


# Checks out the given commit in stacks-project
def checkout_commit(commit):
	subprocess.call(["git", "-C", "stacks-project", "checkout", commit])


# Regular expressions to parse diffs
two_commas = re.compile('\@\@\ \-([0-9]*)\,([0-9]*)\ \+([0-9]*)\,([0-9]*)\ \@\@')
first_comma = re.compile('\@\@\ \-([0-9]*)\,([0-9]*)\ \+([0-9]*)\ \@\@')
second_comma = re.compile('\@\@\ \-([0-9]*)\ \+([0-9]*)\,([0-9]*)\ \@\@')
no_comma = re.compile('\@\@\ \-([0-9]*)\ \+([0-9]*)\ \@\@')


# Get diff between two commits in a given file
# commit_before should be prior in history to commit_after
def get_diff_in(commit_before, commit_after, name):
	diff = subprocess.check_output(["git", "-C", "stacks-project", "diff", "--patience", "-U0", commit_before + '..' + commit_after, name + '.tex'])
	return diff.splitlines()


# Gets a list of line_nr changes between two commits
# in a given file
# commit_before should be prior in history to commit_after
def get_changes_in(commit_before, commit_after, name):

	diff = get_diff_in(commit_before, commit_after, name)

	lines_removed = []
	lines_added = []

	for line in diff:
		if line.find('@@') == 0:
			# looks like
			# @@ -(old line nr),d +(new line nr),a @@
			# meaning 5 lines where removed from old file starting at
			# old line nr and a lines were added started at new line nr
			# Variant: ',d' is missing if d = 1
			# Variant: ',a' is missing if a = 1
			# total of 4 cases

			result = two_commas.findall(line)

			if len(result) == 1 and len(result[0]) == 4:
				if not result[0][1] == '0':
					lines_removed.append([int(result[0][0]), int(result[0][1])])
				if not result[0][3] == '0':
					lines_added.append([int(result[0][2]), int(result[0][3])])
				continue

			result = first_comma.findall(line)

			if len(result) == 1 and len(result[0]) == 3:
				if not result[0][1] == '0':
					lines_removed.append([int(result[0][0]), int(result[0][1])])
				lines_added.append([int(result[0][2]), 1])
				continue

			result = second_comma.findall(line)

			if len(result) == 1 and len(result[0]) == 3:
				lines_removed.append([int(result[0][0]), 1])
				if not result[0][2] == '0':
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
def get_files_changed(commit_before, commit_after):
	temp = subprocess.check_output(["git", "-C", "stacks-project", "diff", "--name-only", commit_before + '..' + commit_after])
	temp = temp.splitlines()
	files_changed = []
	# Get rid of files in subdirectories
	# Get rid of non-tex files
	# Get rid of the .tex ending
	for i in range(0, len(temp)):
		file_name = temp[i]
		if file_name.find('/') >= 0:
			continue
		if '.tex' not in file_name:
			continue
		files_changed.append(file_name[:-4])
	return files_changed


# Gets a list of line_nr changes between two commits
# commit_before should be prior in history to commit_after
def get_all_changes(commit_before, commit_after):

	all_changes = {}

	files_changed = get_files_changed(commit_before, commit_after)

	for name in files_changed:
		all_changes[name] = get_changes_in(commit_before, commit_after, name)

	return all_changes


# Regular expression matching removed and added tags
deleted_tag = re.compile('^\-([0-9A-Z]{4})\,(.*)')
added_tag = re.compile('^\+([0-9A-Z]{4})\,(.*)')


# Gets a list of tag changes between two commits
# commit_before should be prior in history to commit_after
def get_tag_changes(commit_before, commit_after):

	tags_removed = []
	tags_added = []

	diff = subprocess.check_output(["git", "-C", "stacks-project", "diff", "--patience", "-U0", commit_before + '..' + commit_after, 'tags/tags'])
	diff = diff.splitlines()

	for line in diff:
		print line
		deleted = deleted_tag.findall(line)
		if len(deleted) > 0:
			tags_removed.append([deleted[0][0], deleted[0][1]])
		added = added_tag.findall(line)
		if len(added) > 0:
			tags_added.append([added[0][0], added[0][1]])

	return [tags_removed, tags_added]


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

# Testing, testing
commits = find_commits()

#
# Between
# 8de7ea347d2e3ec3689aa84041e9d5ced52963cb
# and
# 2799b450a9a7a5a02932033b43f43d406e1a6b33
# have interesting tag changes
#
# get_tag_changes('2799b450a9a7a5a02932033b43f43d406e1a6b33', '8de7ea347d2e3ec3689aa84041e9d5ced52963cb')

def test_finding_changes(commit_before, commit_after):

	names = get_files_changed(commit_before, commit_after)
	print names

	for name in names:
		diff = get_diff_in(commit_before, commit_after, name)
		print_diff(diff)

		changes = get_changes_in(commit_before, commit_after, name)
		print_changes(changes)

	all_changes = get_all_changes(commit_before, commit_after)
	print_all_changes(all_changes)


