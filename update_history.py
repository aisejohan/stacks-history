# Get detailed information out of the Stacks project history
import subprocess
import os
import os.path
import logging
import sys

from definitions_history import *
from functions_history import *

from gerby.database import *
import gerby.configuration

print("We will work with the following website-project directory: ")
print(websiteProject)
print("We will change the following database: ")
print(gerby.configuration.DATABASE)

user_input_commit = input("Which commit do you want to import?\n")
if not os.path.isfile("histories/" + user_input_commit):
	print("ERROR: This commit does not exist in histories/")
	exit(1)

history = load_back(user_input_commit)

# check if database exists
if not os.path.isfile(gerby.configuration.DATABASE):
	print("ERROR: the database %s does not exist!", gerby.configuration.DATABASE)
	exit(1)

db.init(gerby.configuration.DATABASE)
logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# managing history
Change.drop_table() # TODO always drop Change table?
if not Change.table_exists():
	Change.create_table()

if not Commit.table_exists():
	Commit.create_table()

def createChange(commit, tag, env, action, begin, end):
	if not Tag.select().where(Tag.tag == tag).exists():
		log.error("Tag %s does not exist, but it appears in the history", tag)
		return

	if not Commit.select().where(Commit.hash == commit).exists():
		# TODO is it possible for this to happen? It seems to happen on tag 058V, and
		# commit 8a1f3c3754c4470069f73bd5a07e1edc8c0bf04b, which is also the filename I'm using, so maybe that's why
		log.error("Commit %s does not exist, but it appears in the history", commit)
		return

	Change.create(tag=tag,
		commit=commit,
		filename=env.name,
		action=action,
		label=env.label,
		begin=begin,
		end=end)

# Add subject, time, author and put it in database
def createCommit(commit):
	try:
		# TODO make this the whole commit message
		subject = subprocess.check_output(["git --git-dir " + websiteProject + "/.git log " + commit + " --pretty=format:%B -n 1"], stderr=subprocess.STDOUT, shell=True)
		subject = subject.decode("latin-1", "backslashreplace")
		time = subprocess.check_output(["git --git-dir " + websiteProject + "/.git log " + commit + " --pretty=format:%ai -n 1"], stderr=subprocess.STDOUT, shell=True)
		author = subprocess.check_output(["git --git-dir " + websiteProject + "/.git log " + commit + " --pretty=format:%an -n 1"], stderr=subprocess.STDOUT, shell=True)
		Commit.create(hash=commit, author=author, log=subject, time=time)
	except subprocess.CalledProcessError:
		# this can happen when the history file was not created from the repository which is now used (which is not a common situation I guess)
		log.error("There is a discrepancy between the history file and the Git repository")


# Here we create database entries for new commits
with db.atomic():
	for commit in history.commits:
		if not Commit.select().where(Commit.hash == commit).exists():
			print("Adding database entry for commit %s" % commit)
			createCommit(commit)
# Create database entry for current commit if new
if not Commit.select().where(Commit.hash == history.commit).exists():
	print("Adding database entry for commit %s" % history.commit)
	createCommit(history.commit)


with db.atomic():
	for env_h in history.env_histories:
		# if no tag is present the environment isn't tagged yet, so we ignore it
		if env_h.env.tag == "":
			continue

		# tag we have ended up with
		tag_h = env_h.env.tag

		# these track what happens during the history
		label = ""
		tag = ""
		name = ""
		text = ""
		proof = ""

		print("Considering the history of tag %s" % tag_h)

		length = len(env_h.commits)
		i = 0
		while i < length:
			# where we are at now
			commit = env_h.commits[i]
			env = env_h.envs[i]

			if i == 0:
				# Creation of this piece of mathematics
				# line numbers refer to statement and ignore proof if there is a proof
				createChange(commit, tag_h, env, "creation", env.b, env.e)
				label = env.label
				name = env.name
				text = env.text
				if hasattr(env, "proof"):
					proof = env.proof
				# Do not assign tag yet if there is one

			if env.tag != tag:
				# first commit with tag
				# this also triggers when a tag is changed; this is very rare
				createChange(commit, tag_h, env, "tag", env.b, env.e)
				tag = env.tag

			if env.label != label:
				# either creation or change in label
				createChange(commit, tag_h, env, "label", env.b, env.e)
				label = env.label

			if env.name != name:
				# change of file
				createChange(commit, tag_h, env, "move file", env.b, env.e)
				name = env.name

			if env.text != text:
				# change in statement
				# this could be an invisible change such as slogan, reference, historical remark
				if hasattr(env, "proof") and env.proof != proof:
					# line numbers point to beginning of statement and end of proof
					createChange(commit, tag_h, env, "statement and proof", env.b, env.ep)
					proof = env.proof
				else:
					# line numbers of statement
					createChange(commit, tag_h, env, "statement", env.b, env.e)
				text = env.text
			else:
				if hasattr(env, "proof") and env.proof != proof:
					createChange(commit, tag_h, env, "proof", env.bp, env.ep)
					proof = env.proof

			i = i + 1
