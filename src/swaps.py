from web3 import Web3
import json
from decouple import config

web3 = Web3(
    Web3.HTTPProvider(config("RPC_URL"))
)


def load_abi(abi):
    with open(f"abis/{abi}.json") as fp:
        abi = json.load(fp)
    return abi


def curve_pool_contract(pool_address):
    return web3.eth.contract(address=pool_address, abi=load_abi("Pool")).functions


def get_swap_output(amount, token_in, token_out, curve_pool):
    pool = curve_pool_contract(curve_pool)
    coins_indexes = {}
    i = 0
    while True:
        try:
            coins_indexes[pool.coins(i).call()] = i
            i = i + 1
        except:
            break

    in_index = coins_indexes[token_in]
    out_index = coins_indexes[token_out]
    return pool.get_dy(in_index, out_index, amount).call()


def get_best_swap_output(initial_input, path):
    swap_output = initial_input
    best_swap_output = 0
    best_path = []
    for i in range(0, len(path) - 2):
        (token_in, _) = path[i]
        (token_out, pools) = path[i+1]
        for pool in pools:
            swap_output = get_swap_output(
                swap_output,
                token_in,
                token_out,
                pool
            )
            if swap_output > best_swap_output:
                best_swap_output = swap_output
                best_path.append(pool)
    return best_swap_output, best_path
