"""Community Detection (Leiden Algorithm)"""
from ..graph import GraphBuilder
from ..schema.models import Community, Entity
from collections import defaultdict
import networkx as nx
import logging

logger = logging.getLogger(__name__)

try:
    from graspologic.partition import hierarchical_leiden
    HAS_GRASPOLOGIC = True
except ImportError:
    HAS_GRASPOLOGIC = False
    logger.warning("graspologic not available, using networkx community")

class CommunityDetector:
    def __init__(self, graph: GraphBuilder = None):
        self.graph = graph or GraphBuilder()

    def detect(self):
        G = self._build_networkx_graph()
        if len(G) == 0:
            return []

        if HAS_GRASPOLOGIC:
            communities = self._leiden_detect(G)
        else:
            communities = self._networkx_detect(G)

        return self._build_community_objects(G, communities)

    def _build_networkx_graph(self):
        G = nx.Graph()
        with self.graph._driver.session() as session:
            result = session.run(
                "MATCH (a:Entity)-[r:RELATED_TO]->(b:Entity) "
                "RETURN a.name, b.name, r.weight"
            )
            for record in result:
                G.add_edge(record["a.name"], record["b.name"],
                          weight=record.get("r.weight", 1.0))
        return G

    def _leiden_detect(self, G):
        adj = nx.to_numpy_array(G)
        result = hierarchical_leiden(adj, max_cluster_size=50)
        node_list = list(G.nodes())
        comm_map = defaultdict(list)
        for node_idx, comm_id in enumerate(result):
            comm_map[comm_id].append(node_list[node_idx])
        return list(comm_map.values())

    def _networkx_detect(self, G):
        from networkx.algorithms.community import greedy_modularity_communities
        comms = greedy_modularity_communities(G)
        return [list(c) for c in comms]

    def _build_community_objects(self, G, communities):
        result = []
        for i, members in enumerate(communities):
            cid = "comm-" + str(i)
            title = ", ".join(members[:5])
            if len(members) > 5:
                title += "..."
            result.append(Community(
                community_id=cid, title=title, entities=members, weight=len(members)
            ))
        return result
