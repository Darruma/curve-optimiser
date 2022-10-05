from dataclasses import dataclass
import requests
from constants import CURVE_API, ZERO_ADDR
from typing import List
from graph import TokenGraph


@dataclass
class PoolData:
    name: str
    addr: str
    coins: List[str]


def filter_zero_addr(addrs):
    return list(filter(lambda c: c != ZERO_ADDR, addrs))


def fetch_pool_data(chain: str) -> List[PoolData]:
    response = requests.get(f"{CURVE_API}/api/getPools/{chain}")
    data = response.json()["data"]["poolData"]
    lp_token_to_coins = {}
    for pool in data:
        if "lpTokenAddress" in pool and not pool["isMetaPool"]:
            lp_token_to_coins[pool["lpTokenAddress"]] = filter_zero_addr(pool["coinsAddresses"])

    def make_pool_data(pool):
        pool_name = pool.get("name", "")
        addr = pool.get("address", "")
        if pool["isMetaPool"]:
            coins = []
            for c in pool.get("coins", []):
                if c["isBasePoolLpToken"]:
                    base_pool_coins = lp_token_to_coins[c["address"].lower()]
                    coins.extend(base_pool_coins)
                else:
                    coins.append(c["address"])
        else:
            coins = filter_zero_addr(pool["coinsAddresses"])
        return PoolData(
            pool_name,
            addr,
            coins
        )
    return map(make_pool_data, data)


def build_graph_pool(chain: str) -> TokenGraph:
    pool_data = fetch_pool_data(chain)
    graph = TokenGraph()
    for data in pool_data:
        for i, coin in enumerate(data.coins):
            graph.add_vertex(coin)
            for j in range(0, len(data.coins) - 1):
                if coin != data.coins[j]:
                    graph.add_edge(coin, data.coins[j], data.addr)
    return graph
