import numpy as np
import secrets

def check_unique_seeds(seeds):
    # if the seeds array are unique, return True
    seen = {}
    for seed in seeds:
        if seed in seen:
            return False  # Duplicate found
        seen[seed] = True
    return True

seeds_number = 2000
seeds = [secrets.randbits(32) for _ in range(seeds_number)]
print(f'{seeds=}')
np.save('../seeds_fg_2k.npy', np.array(seeds))

seeds_arr = np.load('../seeds_fg_2k.npy', allow_pickle=True)
print(f'{seeds_arr.shape=}')

# print(f'{type(seeds_arr[0])=}')

# np.random.seed(seed=seeds_arr[0])

print(check_unique_seeds(seeds_arr))

