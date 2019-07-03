# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 21:00:50 2019

@author: theoldestnoob
"""

from itertools import product
from itertools import combinations
from collections import deque

from map_objects.geometry import coords_ortho_adjacent
from map_objects.geometry import Space
from map_objects.geometry import Rect


class MapGraph():
    '''
    Derives a graph structure from:
        an array of grid tiles (2d list of bools where walkable tiles are True)
        a list of rooms (instances of map_objects.geometry.Space)
    '''
    def __init__(self, walkable_array, rooms=[], debug=False):
        self.debug = debug
        self.walkable = walkable_array
        self.hyperedges = []
        self.edges = []
        self.vertices = self.create_vertices(rooms)
        # self.graph.find_vertex_neighbors()
        self.find_hyperedges()
        self.find_edges_from_hyperedges()
        self.vertex_neighbors_from_hyperedges()
        self.find_vertex_hyperedges()
        self.find_vertex_edges()

    def __repr__(self):
        return f"MapGraph({self.walkable}, {self.vertices})"

    def __str__(self):
        outstr = "=====MapGraph=====\n===Vertices===:\n"
        for vertex in self.vertices:
            outstr += f"{vertex}\n"
        outstr += "===Hyperedges===:\n"
        for h_edge in self.hyperedges:
            outstr += f"{h_edge}\n"
        outstr += "===Edges===:\n"
        for edge in self.edges:
            outstr += f"{edge}\n"
        return outstr

    def create_vertices(self, rooms):
        '''Build a set of MapVertex objects from a list of Space objects.'''
        if self.debug:
            print("Creating Vertices...")
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        rnum = len(rooms) // len(alphabet) + 1
        vertices = []
        for room, idtuple in zip(rooms, product(alphabet, repeat=rnum)):
            ident = "".join(idtuple)
            vertex = MapVertex(room, ident)
            vertices.append(vertex)
        return vertices

    def find_vertex_neighbors(self):
        '''Find all neighbors of a MapVertex using flood fill. Inefficient,
        do not use unless you can not find hyperedges for some reason.
        '''
        if self.debug:
            print("Finding Vertex Neighbors...")
        for vertex in self.vertices:
            room_x, room_y = vertex.space.center()
            others = [k for k in self.vertices if k is not vertex]
            width = len(self.walkable)
            height = len(self.walkable[0])
            neighbors = self.find_vertex_neigh_iter(vertex, others,
                                                    width, height)
            vneigh = sorted(list(set(neighbors)), key=lambda x: x.ident)
            vertex.neighbors = vneigh

    def vertex_neighbors_from_hyperedges(self):
        '''Find all neighbors of a MapVertex by getting the information from
        hyperedges, which already know which vertices they connect. Must be
        called after MapGraph.find_hyperedges() or it will not do anything
        useful.
        '''
        if self.debug:
            print("Finding Vertex Neighbors from Hyperedges...")
        for vertex in self.vertices:
            vlist = []
            nlist = []
            for edge in self.hyperedges:
                if vertex in edge.vertices:
                    vlist.extend(edge.vertices)
            nlist = sorted(list(set(vlist)), key=lambda x: x.ident)
            if nlist:
                nlist.remove(vertex)
            vertex.neighbors = nlist

    def find_vertex_neigh_iter(self, vertex, others, width, height):
        '''Flood Fill helper method to find vertex neighbors. Called by
        MapGraph.find_vertex_neighbors(). Inefficient, do not use unless
        you can not find hyperedges for some reason.'''
        # vertex: vertex to find neighbors of
        # others: other vertices that may be neighbors
        # we assume no overlapping vertices on graph
        x0, y0 = vertex.space.center()
        searched = [[False for y in range(height)]
                    for x in range(width)]
        neighbors = []
        searchq = deque([(x0, y0)])

        while searchq:
            x, y = searchq.popleft()
            searched[x][y] = True

            for z in others:
                if z.space.contains(x, y):
                    neighbors.append(z)
                    break
            else:
                if (not searched[x + 1][y]
                        and self.walkable[x + 1][y]
                        and not (x + 1, y) in searchq):
                    searchq.append((x + 1, y))
                if (not searched[x - 1][y]
                        and self.walkable[x - 1][y]
                        and not (x - 1, y) in searchq):
                    searchq.append((x - 1, y))
                if (not searched[x][y + 1]
                        and self.walkable[x][y + 1]
                        and not (x, y + 1) in searchq):
                    searchq.append((x, y + 1))
                if (not searched[x][y - 1]
                        and self.walkable[x][y - 1]
                        and not (x, y - 1) in searchq):
                    searchq.append((x, y - 1))

        return neighbors

    def find_vertex_hyperedges(self):
        '''Find all hyperedges connected to a MapVertex.'''
        if self.debug:
            print("Finding Vertex Hyperedges...")
        for vertex in self.vertices:
            elist = []
            for edge in self.hyperedges:
                if vertex in edge.vertices:
                    elist.append(edge)
            vertex.hyperedges = elist

    def find_vertex_edges(self):
        '''Find all edges connected to a MapVertex that are not hyperedges.'''
        if self.debug:
            print("Finding Vertex Edges...")
        for vertex in self.vertices:
            elist = []
            for edge in self.edges:
                if vertex in edge.vertices:
                    elist.append(edge)
            vertex.edges = elist

    def find_hyperedges(self):
        '''Find all hyperedges in graph using floodfill helper method and store
        as MapHyperedge objects.
        '''
        if self.debug:
            print("Finding Hyperedges...")
        # find tiles that aren't walls and aren't in a vertex
        width = len(self.walkable)
        height = len(self.walkable[0])
        edgetiles = [[True for y in range(height)]
                     for x in range(width)]
        for y in range(height):
            for x in range(width):
                if not self.walkable[x][y]:
                    edgetiles[x][y] = False
                for vertex in self.vertices:
                    if vertex.space.contains(x, y):
                        edgetiles[x][y] = False
                        break
        # flood fill all edge tiles to find vertices they connect
        captured = [[False for y in range(height)]
                    for x in range(width)]
        elist = []
        for y in range(height):
            for x in range(width):
                if edgetiles[x][y]:
                    edge = self.find_hyperedge_iter(x, y, captured,
                                                    width, height)
                    if edge:
                        for ex, ey in edge.space:
                            captured[ex][ey] = True
                        elist.append(edge)
        # assign identifiers to all hyperedges
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        rnum = len(elist) // len(alphabet) + 1
        for edge, idtuple in zip(elist, product(alphabet, repeat=rnum)):
            edge.ident = "#"
            edge.ident += "".join(idtuple)

        self.hyperedges = elist

    def find_hyperedge_iter(self, x0, y0, captured, width, height):
        '''Flood Fill helper method to find all hyperedges in a graph.Called by
        MapGraph.find_hyperedges().
        '''
        if captured[x0][y0]:
            return []
        searched = [[False for y in range(height)]
                    for x in range(width)]
        neighbors = []
        tiles = []
        searchq = deque([(x0, y0)])

        while searchq:
            x, y = searchq.popleft()
            searched[x][y] = True

            for z in self.vertices:
                if z.space.contains(x, y):
                    neighbors.append(z)
                    break
            else:
                if (not searched[x + 1][y]
                        and self.walkable[x + 1][y]
                        and not (x + 1, y) in searchq):
                    searchq.append((x + 1, y))
                if (not searched[x - 1][y]
                        and self.walkable[x - 1][y]
                        and not (x - 1, y) in searchq):
                    searchq.append((x - 1, y))
                if (not searched[x][y + 1]
                        and self.walkable[x][y + 1]
                        and not (x, y + 1) in searchq):
                    searchq.append((x, y + 1))
                if (not searched[x][y - 1]
                        and self.walkable[x][y - 1]
                        and not (x, y - 1) in searchq):
                    searchq.append((x, y - 1))
                tiles.append((x, y))

        nlist = sorted(list(set(neighbors)), key=lambda x: x.ident)
        edge = MapHyperedge(Space(tiles), nlist)
        return edge

    def find_edges_from_hyperedges(self):
        '''Find all edges on graph that connect 2 vertices. These are contained
        in hyperedges, so MapGraph.find_hyperedges() must be called first.
        '''
        if self.debug:
            print("Finding Edges from Hyperedges...")
        elist = []
        for hyperedge in self.hyperedges:
            vids = []
            for vertex in hyperedge.vertices:
                vids.append(vertex.ident)
            for pair in combinations(hyperedge.vertices, 2):
                # find shortest path between v0 and v1 in hyperedge.space
                v0, v1 = pair
                s = self.find_spath_in_coords(hyperedge.space, v0, v1)
                edge = MapEdge(Space(s), [v0, v1], hyperedge=hyperedge)
                elist.append(edge)
                edge.hyperedge.edges.append(edge)
        # assign identifiers to all edges
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        rnum = len(elist) // len(alphabet) + 1
        for edge, idtuple in zip(elist, product(alphabet, repeat=rnum)):
            ident = "".join(idtuple)
            edge.ident = ident

        self.edges = elist

    def find_spath_in_coords(self, coord_list, v0, v1):
        '''Find the shortest path between two Space objects v0 and v1 that
        only traverses the coordinates in coord_list. Used to help find edges
        from hyperedges.
        '''
        # build a list of coordinates with distance from v0 as (x, y, distance)
        distance = []
        searched = []
        stack = deque()
        for x, y in coord_list:
            # check adjacency against a 1x1 Rect for speed
            if v0.space.adjacent_ortho(Rect(x, y, 0, 0)):
                distance.append((x, y, 1))
                stack.append((x, y, 1))
                searched.append((x, y))
        count = 0
        while stack:
            x, y, z = stack.popleft()
            if (x + 1, y) in coord_list and (x + 1, y) not in searched:
                distance.append((x + 1, y, z + 1))
                stack.append((x + 1, y, z + 1))
                searched.append((x + 1, y))
            if (x - 1, y) in coord_list and (x - 1, y) not in searched:
                distance.append((x - 1, y, z + 1))
                stack.append((x - 1, y, z + 1))
                searched.append((x - 1, y))
            if (x, y + 1) in coord_list and (x, y + 1) not in searched:
                distance.append((x, y + 1, z + 1))
                stack.append((x, y + 1, z + 1))
                searched.append((x, y + 1))
            if (x, y - 1) in coord_list and (x, y - 1) not in searched:
                distance.append((x, y - 1, z + 1))
                stack.append((x, y - 1, z + 1))
                searched.append((x, y - 1))
            # exit if we've searched 5000 spaces
            # because we're probably in an infinite loop
            count += 1
            if count > 5000:
                break
        # find the shortest path from v1 back to v0
        # start at v1 and always pick the tile with the lowest distance
        distance.sort(key=lambda z: z[2], reverse=True)
        x_end, y_end, z_end = distance[0]
        for x, y, z in distance:
            # check adjacency against a fake Rect for speed
            if v1.space.adjacent_ortho(Rect(x, y, 0, 0)):
                if z < z_end:
                    x_end = x
                    y_end = y
                    z_end = z
        spath = [(x_end, y_end)]
        for (x, y, z) in distance:
            if z < z_end and coords_ortho_adjacent(x, y, x_end, y_end):
                spath.append((x, y))
                x_end, y_end, z_end = x, y, z

        return spath

    def get_metrics(self):
        '''Generate a set of measures about the graph.'''
        v_count = len(self.vertices)
        e_count = len(self.edges)
        he_count = len(self.hyperedges)
        len_2_he = 0
        true_he = he_count
        he_rank = 0
        he_k_degree = 0
        he_uniform = True
        for he in self.hyperedges:
            he_card = len(he.vertices)
            if he_rank < he_card:
                he_rank = he_card
            if he_k_degree == 0:
                he_k_degree = he_card
            elif he_k_degree != he_card:
                he_uniform = False
            if he_card == 2:
                len_2_he += 1
                true_he -= 1
        outstr = "===Graph Metrics===\n"
        outstr += f" Vertices: {v_count}\n"
        outstr += f" Edges: {e_count}\n"
        outstr += f" Hyperedges: {he_count}\n"
        outstr += f" Cardinality 2 Hyperedges (Edges): {len_2_he}\n"
        outstr += f" Cardinality >2 Hyperedges: {true_he}\n"
        outstr += f" Hypergraph rank: {he_rank}\n"
        if he_uniform:
            outstr += f" Hypergraph is k-uniform.\n"
        else:
            outstr += f" Hypergraph is not k-uniform.\n"
        if he_uniform and he_rank == 2:
            outstr += f" 2-uniform Hypergraph: just a normal graph!\n"

        return outstr


class MapVertex():
    '''Vertex in MapGraph. Contains a Space and identifier and lists of
    connected hyperedges, connected edges, and neighbor vertices.
    '''
    def __init__(self, space=None, ident=None, hyperedges=None, edges=None,
                 neighbors=None):
        self.space = space
        self.ident = ident
        if hyperedges is None:
            self.hyperedges = []
        else:
            self.hyperedges = hyperedges
        if edges is None:
            self.edges = []
        else:
            self.edges = edges
        if neighbors is None:
            self.neighbors = []
        else:
            self.neighbors = neighbors

    def __repr__(self):
        outstr = f"MapVertex(space={self.space}, ident={self.ident}, "
        outstr += f"hyperedges={self.hyperedges}, edges={self.edges}, "
        outstr += f"neighbors={self.neighbors})"
        return outstr

    def __str__(self):
        outstr = f"Vertex '{self.ident}': {self.space}\nNeighbors: "
        nids = []
        for neighbor in self.neighbors:
            nids.append(neighbor.ident)
        outstr += ", ".join(nids)
        outstr += "\nHyperedges: "
        eids = []
        for edge in self.hyperedges:
            eids.append(edge.ident)
        outstr += ", ".join(eids)
        outstr += "\nEdges: "
        eids = []
        for edge in self.edges:
            eids.append(edge.ident)
        outstr += ", ".join(eids)
        outstr += "\n"
        return outstr


class MapEdge():
    '''Edge in MapGraph. Contains a Space, identifier, list of connected
    vertices, and its parent hyperedge.
    '''
    def __init__(self, space, vertices, ident=None, hyperedge=None):
        self.space = space
        self.vertices = vertices
        self.hyperedge = hyperedge
        if ident is None:
            vlist = []
            for vertex in vertices:
                vlist.append(vertex.ident)
            self.ident = ""
            self.ident += "".join(sorted(list(set(vlist))))
        else:
            self.ident = ident
        self.cost = len(self.space)

    def __repr__(self):
        repstr = f"MapEdge({self.space}, {self.vertices}, ident={self.ident}, "
        repstr += f"hyperedge={self.hyperedge})"
        return repstr

    def __str__(self):
        outstr = f"Edge '{self.ident}'\n"
        outstr += f"Parent Hyperedge: '{self.hyperedge.ident}'\n"
        outstr += f"Vertices: "
        vids = []
        for vertex in self.vertices:
            vids.append(f"{vertex.ident}")
        outstr += ", ".join(vids)
        outstr += f"\nCost: {self.cost}\n"
        return outstr


class MapHyperedge(MapEdge):
    '''Hyperedge in MapGraph. A MapEdge that contains a list of all of its
    child edges.
    '''
    def __init__(self, *args, edges=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hyperedge = None
        if edges is None:
            self.edges = []
        else:
            self.edges = edges

    def __repr__(self):
        repstr = f"MapHyperedge({self.space}, {self.vertices}, "
        repstr += f"ident={self.ident}, edges={self.edges})"
        return repstr

    def __str__(self):
        outstr = f"Hyperedge '{self.ident}'\n"
        outstr += f"Vertices: "
        vids = []
        for vertex in self.vertices:
            vids.append(f"{vertex.ident}")
        outstr += ", ".join(vids)
        eids = []
        for edge in self.edges:
            eids.append(f"{edge.ident}")
        outstr += "\nEdges: "
        outstr += ", ".join(eids)
        outstr += "\n"
        return outstr


if __name__ == "__main__":
    import doctest
    doctest.testfile("tests/map_graph.txt")
