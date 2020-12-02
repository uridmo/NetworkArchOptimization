import pickle

dc_arch_1 = 1
dc_arch_2 = 1
dc_arch_3 = 1
dc_tie_1 = 1
dc_tie_2 = 1
dc_tie_3 = 1
dc_hangers = 1

dc = [dc_arch_1, dc_arch_2, dc_arch_3,
      dc_tie_1, dc_tie_2, dc_tie_3, dc_hangers]

f = open('Base case/store.pckl', 'wb')
pickle.dump(dc, f)
f.close()

f = open('Base case/store.pckl', 'rb')
dc = pickle.load(f)

f.close()

print(dc)
