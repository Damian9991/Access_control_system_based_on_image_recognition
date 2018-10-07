a = [1,2]
try:
	print(a[5])
except IndexError as err:
	print(str(err))
