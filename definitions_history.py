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
