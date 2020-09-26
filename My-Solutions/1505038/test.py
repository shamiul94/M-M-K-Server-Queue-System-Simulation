#!/home/heisenberg/anaconda3/bin/python
q4 = [3, 5, 6, 7, 8, 3]

q1 = [1, 2]
q3 = [1, 2, 4, 5, 6]

q2 = [1, 2, 3]

q = []
q.append(q1)
q.append(q2)
q.append(q3)
q.append(q4)

print(q)

minLen, p= min([(len(q[i]), i)for i in range(4)], key=lambda tuple: tuple[0])

print(minLen)


a = [4] * 3

print(a)