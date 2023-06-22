import ctypes
import sys
import os
from collections import defaultdict

CGROUP_PATH = '/sys/fs/cgroup/memory'

SYS_RESET_SWAP_STAT = 451
SYS_GET_SWAP_STATS = 452
SYS_SET_ASYNC_PREFETCH = 453
SYS_SET_SWAPCACHE_MODE = 454
SYS_SET_SWAP_BW_CONTROL = 455
SYS_GET_ALL_PROCS_TOTAL_PKTS = 456
SYS_SET_BYPASS_SWAP_CACHE = 457
SYS_SET_READAHEAD_WIN = 458
SYS_SET_CUSTOMIZED_PREFETCH = 459
SYS_SET_SLOTCACHE_CPUMASK = 460
SYS_SET_CPU_TO_SWAP_PARTITION = 464

DISABLE_SYSCALL = False

# syscalls
def reset_swap_stats():
    if DISABLE_SYSCALL:
        return
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int

    return syscall(SYS_RESET_SWAP_STAT)


def get_swap_stats():
    if DISABLE_SYSCALL:
        return 0,0,0
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int
    syscall.argtypes = ctypes.c_long, ctypes.POINTER(
        ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)

    c_ondemand_swap_num = ctypes.c_int()
    c_prefetch_swap_num = ctypes.c_int()
    c_hiton_swap_cache_num = ctypes.c_int()
    syscall(SYS_GET_SWAP_STATS, ctypes.byref(c_ondemand_swap_num), ctypes.byref(
        c_prefetch_swap_num), ctypes.byref(c_hiton_swap_cache_num))

    ondemand_swap_num = c_ondemand_swap_num.value
    prefetch_swap_num = c_prefetch_swap_num.value
    hiton_swap_cache_num = c_hiton_swap_cache_num.value
    print(ondemand_swap_num, prefetch_swap_num, hiton_swap_cache_num)
    return ondemand_swap_num, prefetch_swap_num, hiton_swap_cache_num


def set_aysnc_prefetch(enable):
    if DISABLE_SYSCALL:
        return
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int
    syscall.argtypes = ctypes.c_long, ctypes.c_int

    return syscall(SYS_SET_ASYNC_PREFETCH, ctypes.c_int(enable))


def set_swapcache_mode(enable, capacity=8192): # default capacity 32MB
    if DISABLE_SYSCALL:
        return
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int
    syscall.argtypes = ctypes.c_long, ctypes.c_int, ctypes.c_int

    return syscall(SYS_SET_SWAPCACHE_MODE, ctypes.c_int(enable), ctypes.c_int(capacity))


def set_swap_bw_control(enable):
    if DISABLE_SYSCALL:
        return
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int
    syscall.argtypes = ctypes.c_long, ctypes.c_int

    return syscall(SYS_SET_SWAP_BW_CONTROL, ctypes.c_int(enable))


def set_bypass_swap_cache(enable):
    if DISABLE_SYSCALL:
        return
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int
    syscall.argtypes = ctypes.c_long, ctypes.c_int

    return syscall(SYS_SET_BYPASS_SWAP_CACHE, ctypes.c_int(enable))


def set_readahead_win(win):
    if DISABLE_SYSCALL:
        return
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int
    syscall.argtypes = ctypes.c_long, ctypes.c_int

    return syscall(SYS_SET_READAHEAD_WIN, ctypes.c_int(win))


def set_customized_prefetch(enable):
    if DISABLE_SYSCALL:
        return
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int
    syscall.argtypes = ctypes.c_long, ctypes.c_int

    return syscall(SYS_SET_CUSTOMIZED_PREFETCH, ctypes.c_int(enable))


def set_readahead_mode(mode):
    with open(constants.VMA_RA_ENABLED_FILE, 'w') as f:
        if mode == 'VMA' or mode == 'vma' or mode == 'true':
            f.write("true")
        elif mode == 'BLK' or mode == 'blk' or mode == 'false':
            f.write("false")


def set_slotcache_cpumask(cpus):
    if DISABLE_SYSCALL:
        return
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int
    syscall.argtypes = ctypes.c_long, ctypes.POINTER(ctypes.c_int)

    NUM_CORES = 96
    c_mask = (ctypes.c_int * NUM_CORES)()
    for i in range(NUM_CORES):
        c_mask[i] = 1

    for cpu in cpus:
        c_mask[cpu] = 0

    syscall(SYS_SET_SLOTCACHE_CPUMASK, ctypes.cast(c_mask, ctypes.POINTER(ctypes.c_int)))

def set_cpu_to_swap_partition(cpus):
    if DISABLE_SYSCALL:
        return
    libc = ctypes.CDLL(None)
    syscall = libc.syscall
    syscall.restype = ctypes.c_int
    syscall.argtypes = ctypes.c_long, ctypes.POINTER(ctypes.c_int)

    NUM_CORES = 32
    c_mask = (ctypes.c_int * NUM_CORES)()
    for i in range(NUM_CORES):
        c_mask[i] = cpus[i]

    syscall(SYS_SET_CPU_TO_SWAP_PARTITION, ctypes.cast(c_mask, ctypes.POINTER(ctypes.c_int)))


# util functions
def calc_percentage():
    ondemand, prefetch, hiton_swap = get_swap_stats()
    if (ondemand + prefetch) == 0 or prefetch == 0:
        prefetch_percentage = 0
        prefetch_accuracy = 0
    else:
        prefetch_percentage = prefetch / (ondemand + prefetch)
        prefetch_accuracy = hiton_swap / prefetch

    print("#(On-demand Swapin):", ondemand)
    print("#(Prefetch Swapin): ", prefetch)
    print("#(Hiton Swap Cache):", hiton_swap)
    print("Prefetch Precentage: {:.2f}".format(prefetch_percentage))
    print("Prefetch Accuracy: {:.2f}".format(prefetch_accuracy))

    return prefetch_percentage, prefetch_accuracy


def get_containers():
    return [name for name in os.listdir(CGROUP_PATH) if os.path.isdir(os.path.join(CGROUP_PATH, name))]


def get_container_stats(containers=None, keys=None, tty=True):
    if not containers:
        containers = get_containers()
    if not keys:
        keys = ['ondemand_swapin ',
                'prefetch_swapin ',
                'hiton_swap_cache']

    global_stats = defaultdict(int)
    container_stats = {}
    for container in containers:
        container_stats[container] = {}
        with open(os.path.join(CGROUP_PATH, container, 'memory.stat')) as f:
            lines = f.readlines()
            for line in lines:
                for key in keys:
                    if line[:len(key)] == key:
                        container_stats[container][key] = int(line.split()[-1])
                        global_stats[key] += int(line.split()[-1])

    if tty:
        for c, stats in container_stats.items():
            print(c, ':')
            for k, v in stats.items():
                print('\t' + k, v)
        for k, v in global_stats.items():
            print('total_' + k, v)

    return container_stats


def reset_container_stats(container):
    # return
    with open(os.path.join(CGROUP_PATH, container, 'memory.stat'), 'w') as f:
        f.write('0')


def main():
    if len(sys.argv) == 1:
        calc_percentage()
    elif len(sys.argv) > 1:
        if sys.argv[1] == 'reset':
            reset_swap_stats()
        elif sys.argv[1] == 'reset_container':
            reset_container_stats(sys.argv[2])
        elif sys.argv[1] == 'stats':
            calc_percentage()
            get_container_stats()
        elif sys.argv[1] == 'async':
            set_aysnc_prefetch(int(sys.argv[2]))
        elif sys.argv[1] == 'swapcache_mode':
            set_swapcache_mode(int(sys.argv[2]), int(sys.argv[3]))
        elif sys.argv[1] == 'bw_control':
            set_swap_bw_control(int(sys.argv[2]))
        elif sys.argv[1] == 'bypass_swapcache':
            set_bypass_swap_cache(int(sys.argv[2]))
        elif sys.argv[1] == 'readahead':
            if sys.argv[2] == 'disable':
                set_readahead_win(1)
            elif sys.argv[2] == 'enable':
                set_readahead_win(0)
            else:
                set_readahead_win(int(sys.argv[2]))
        elif sys.argv[1] == 'customized_prefetch':
            if sys.argv[2] == 'leap' or sys.argv[2] == 'LEAP':
                set_customized_prefetch(1);
            else:
                set_customized_prefetch(0);
        elif sys.argv[1] == 'readahead_mode':
            set_readahead_mode(sys.argv[2])
        elif sys.argv[1] == 'slotcache_mask':
            app_cpu_map = {
                'none': [],
                'snappy': [0, 16],
                'kmeans': [2, 18],
                'xgboost': [4, 6, 8, 10, 12, 20, 22, 24, 26, 28],
                'spark': [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31],
                'non-spark': [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30],
                'all': range(0, 96)
            }
            app = sys.argv[2]
            if app in app_cpu_map:
                # set mask cores to 0 to let the app alloc from swap partition
                set_slotcache_cpumask(app_cpu_map[app])
        elif sys.argv[1] == 'cpu_to_swap_partition':
            NUM_CORES = 32
            cpus = []
            for i in range(NUM_CORES):
                cpus.append(sys.argv[i + 2])
            set_cpu_to_swap_partition(cpus)


if __name__ == '__main__':
    main()
