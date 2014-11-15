import cPickle as pickle


def write_A(A, filename):
	pickle.dump(A, open(filename, 'wb'), -1)

def get_A(filename):
	return pickle.load(open(filename, 'rb'))


A = ['A', 'B', 'C', 'D']

write_A(A, 'tijdelijk.pkl')

B = get_A('tijdelijk.pkl')

A.append('E')

print A
print B
print A == B
print A is B

write_A(A, 'tijdelijk_2.pkl')
