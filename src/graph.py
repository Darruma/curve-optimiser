import requests
from constants import CURVE_API
from swaps import get_best_swap_output


class Token:
    def __init__(self, token):
        self.token = token
        self.neighbours = {}

    def __repr__(self) -> str:
        return f"Token({self.token})"

    def add_neighbour(self, token, pool):
        if token not in self.neighbours:
            self.neighbours[token] = [pool]
        else:
            self.neighbours[token].append(pool)

    def get_neighbours(self):
        return self.neighbours.keys()

    def get_pools(self, token):
        return self.neighbours[token]


class TokenGraph:
    def __init__(self) -> None:
        self.vertices = {}

    def add_vertex(self, token_addr):
        if token_addr not in self.vertices:
            self.vertices[token_addr] = Token(token_addr)

    def get_vertex(self, token_addr):
        return self.vertices.get(token_addr, None)

    def add_edge(self, token_from, token_to, pool):
        self.add_vertex(token_from)
        self.add_vertex(token_to)
        self.vertices[token_from].add_neighbour(
            self.vertices[token_to],
            pool
        )
        self.vertices[token_to].add_neighbour(
            self.vertices[token_from],
            pool
        )

    def get_vertices(self):
        return self.vertices.keys()

    def find_paths_between_tokens(self, token_from, token_to, max_length=5):
        visited = {v.token: False for v in self.vertices.values()}
        current_path = []
        paths = []

        def dfs(fr, to):
            if visited[fr.token] or len(current_path) > max_length:
                return
            else:
                visited[fr.token] = True
                current_path.append(fr.token)
            if fr == to:
                paths.append(current_path.copy())
                visited[fr.token] = False
                current_path.pop()
                return
            else:
                for neighbour in fr.get_neighbours():
                    dfs(neighbour, to)
            current_path.pop()
            visited[fr.token] = False

        dfs(token_from, token_to)
        return sorted(paths, key=len)

    def get_pools_from_path(self, path):
        pool_path = []
        for index, p in enumerate(path):
            pools = []
            if index != 0:
                token = self.get_vertex(p)
                prev_token = self.get_vertex(path[index - 1])
                pools = token.get_pools(prev_token)
            pool_path.append((p, pools))
        return pool_path

    def get_best_path(self, paths, initial_input):
        max_output = 0
        max_path = []
        for path in paths:
            output, new_best_path = get_best_swap_output(initial_input, path)
            if output > max_output:
                max_output = output
                max_path = new_best_path
        return max_path

    def print_token_connections(self, token_addr):
        token = self.get_vertex(token_addr)
        if token:
            print(f"\nToken: {token_addr} \n")
            for neighbour_token, pools in token.neighbours.items():
                print(f"Token to: {neighbour_token.token}")
                print(f"Pools: {pools} \n")
            print("=" * 50)

    def print_graph_tokens(self):
        for token_addr in self.get_vertices():
            self.print_token_connections(token_addr)

    def print_pools_paths(self, paths):
        token_names = get_token_names("ethereum")
        for path in paths:
            pools_path = self.get_pools_from_path(path)
            for p in pools_path:
                print(token_names[p[0]], p[1])
            print("" * 50)


def get_token_names(chain):
    token_names = {}
    response = requests.get(f"{CURVE_API}/api/getPools/{chain}")
    data = response.json()["data"]["poolData"]
    for pool in data:
        for coin in pool["coins"]:
            if not coin["address"] in token_names:
                token_names[coin["address"]] = coin["symbol"]
    return token_names
