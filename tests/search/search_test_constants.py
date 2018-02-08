import random
import string

array_range=50

snpsarray = ['rs' + str(i) for i in range(array_range)]
pvalsarray = [str(random.uniform(0.0000000003, 0.01)) for _ in range(array_range)]
bparray = [random.randint(0, 100000000) for _ in range(array_range)]
effectarray = [random.choice(string.ascii_uppercase) for _ in range(array_range)]
otherarray = [random.choice(string.ascii_uppercase) for _ in range(array_range)]
frequencyarray = [random.uniform(0.0000000003, 0.01) for _ in range(array_range)]
orarray = [random.uniform(0.0000000003, 0.01) for _ in range(array_range)]
