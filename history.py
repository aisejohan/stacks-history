# List the stems of the TeX files in the project
# in the correct order
def list_text_files():
	Makefile_file = open("stacks-project/Makefile", 'r')
	for line in Makefile_file:
		n = line.find("LIJST = ")
		if n == 0:
			break
	lijst = ""
	while line.find("\\") >= 0:
		line = line.rstrip()
		line = line.rstrip("\\")
		lijst = lijst + " " + line
		line = Makefile_file.next()
	Makefile_file.close()
	lijst = lijst + " " + line
	lijst = lijst.replace("LIJST = ", "")
	lijst = lijst + " fdl"
	return lijst.split()

lijstje = list_text_files()

with_proofs = ['lemma', 'proposition', 'theorem']
without_proofs = ['definition', 'example', 'exercise', 'situation', 'remark', 'remarks']

# We will store lemmas, propositions, theorems in the following list
envs_with_proofs = []
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

With = env_with_proof('', '', '', '', 0, 0, '', 0, 0, '')

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

# We will store definitions, examples, exercises, situations, remarks,
# and remarks's in the following list
envs_without_proofs = []
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

Without = env_without_proof('', '', '', '', 0, 0, '')

def print_without(Without):
	print Without.name
	print Without.type
	print Without.label
	print Without.tag
	print Without.b
	print Without.e
	print Without.text.rstrip()

for name in lijstje:
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

for With in envs_with_proofs:
	print_with(With)

for Without in envs_without_proofs:
	print_without(Without)


tags = []
try:
	tagsfile =  open("stacks-project/tags/tags", 'r')
	for line in tagsfile:
		if not line.find('#') == 0:
			tags.append(line.rstrip().split(","))
except:
	pass


