import subprocess
import re

commits = subprocess.check_output(["git", "-C", "stacks-project", "log", "--pretty=format:%H", "master"])

commits = commits.splitlines()

# To checkout commit
# subprocess.call(["git", "-C", "stacks-project", "checkout", commit])

n = len(commits)

commit_before = commits[60]
commit_after = commits[59]

files_changed = subprocess.check_output(["git", "-C", "stacks-project", "diff", "--name-only", commit_before + '..' + commit_after])

print files_changed

diff = subprocess.check_output(["git", "-C", "stacks-project", "diff", "--patience", "-U0", commit_before + '..' + commit_after])

diff = diff.splitlines()


lines_removed = []
lines_added = []

two_commas = re.compile('\@\@\ \-([0-9]*)\,([0-9]*)\ \+([0-9]*)\,([0-9]*)\ \@\@')
first_comma = re.compile('\@\@\ \-([0-9]*)\,([0-9]*)\ \+([0-9]*)\ \@\@')
second_comma = re.compile('\@\@\ \-([0-9]*)\ \+([0-9]*)\,([0-9]*)\ \@\@')
no_comma = re.compile('\@\@\ \-([0-9]*)\ \+([0-9]*)\ \@\@')

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

print "Lines removed: "
print lines_removed
print "Lines added: "
print lines_added


#
# git diff --name-only
