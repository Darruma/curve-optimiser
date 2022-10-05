from pools import build_graph_pool


graph = build_graph_pool("ethereum")


paths = graph.find_paths_between_tokens(
    graph.get_vertex("0x853d955aCEf822Db058eb8505911ED77F175b99e"),
    graph.get_vertex("0x0316EB71485b0Ab14103307bf65a021042c6d380"),
    max_length=3
)
graph.print_token_connections("0x853d955aCEf822Db058eb8505911ED77F175b99e")
graph.print_token_connections("0x0316EB71485b0Ab14103307bf65a021042c6d380")

# graph.print_pools_paths(paths)
paths = list(map(lambda x: graph.get_pools_from_path(x), paths))
best_path = graph.get_best_path(paths, 1e18)
print(best_path)
