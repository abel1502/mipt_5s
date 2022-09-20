from __future__ import annotations
from os import stat
import typing
import pydotplus as dot
import pathlib
import copy
import itertools

from .automata import *


class BaseAutomataBinOp:
    auts: typing.Tuple[Automata, Automata]


    def __init__(self, aut1: Automata, aut2: Automata):
        self.auts = (aut1, aut2)
    
    @property
    def aut1(self) -> Automata:
        return self.auts[0]
    
    @property
    def aut2(self) -> Automata:
        return self.auts[1]
    
    def apply(self) -> Automata:
        raise NotImplementedError()
    
    def common_alphabet(self) -> str:
        return ''.join(set(self.aut1.alphabet) | set(self.aut2.alphabet))
    
    def raw_merge(self) -> Automata:
        """
        Merges aut1 and aut2, removing term markers and introducing a new, unconnected starting node.
        The keys are created as tuples of (aut.id, node.id), aut.id being 0 or 1
        """

        result = Automata(self.common_alphabet())
        
        for i in range(2):
            for node in self.auts[i].get_nodes():
                result.make_node(key=(i, node.id))

            for edge in self.auts[i].get_edges():
                result.link(
                    (i, edge.src.id),
                    (i, edge.dst.id),
                    edge.label
                )
    
    def raw_cross(self) -> Automata:
        """
        Makes the cross product of aut1 and aut2,
        using the (0, 0) node as the starting one and
        marking only those nodes as term, which are term in both automatas
        The keys are created as tuples of (node1.id, node2.id)
        """

        result = Automata(self.common_alphabet())

        result.set_key(result.start.id, (0, 0))
        
        for node1 in self.aut1.get_nodes():
            for node2 in self.aut2.get_nodes():
                result.make_node(
                    key=(node1.id, node2.id),
                    term=node1.is_term and node2.is_term
                )
        
        for edge1 in self.aut1.get_edges():
            for node2 in self.aut2.get_nodes():
                result.link(
                    (edge1.src.id, node2.id),
                    (edge1.dst.id, node2.id),
                    edge1.label
                )
        
        for node1 in self.aut1.get_nodes():
            for edge2 in self.aut2.get_edges():
                result.link(
                    (node1.id, edge2.src.id),
                    (node1.id, edge2.dst.id),
                    edge2.label
                )


class BaseAutomataTransform:
    aut: Automata


    def __init__(self, aut: Automata):
        self.aut = aut
    
    def apply(self) -> Automata:
        raise NotImplementedError()
    
    def raw_copy(self) -> Automata:
        """
        Just copies the automata
        """

        return self.aut.copy()


# End of base classes, begin specific optimizations

class AutomataConcat(BaseAutomataBinOp):
    def apply(self) -> Automata:
        result: Automata = self.raw_merge()

        result.link(result.start.id, (0, 0), "")

        for node in self.aut1.get_terms():
            result.link((0, node.id), (1, 0), "")
        
        for node in self.aut2.get_terms():
            result.node((1, node.id)).is_term = True
        
        return result


class AutomataJoin(BaseAutomataBinOp):
    def apply(self) -> Automata:
        result: Automata = self.raw_merge()

        result.link(result.start.id, (0, 0), "")
        result.link(result.start.id, (1, 0), "")

        end: Node = result.make_node(term=True)

        for i in range(2):
            for node in self.aut[i].get_terms():
                result.link((i, node.id), end, "")
        
        return result


class AutomataIntersect(BaseAutomataBinOp):
    def apply(self) -> Automata:
        result: Automata = self.raw_cross()

        # No more work needed, actually
        
        return result


class AutomataStar(BaseAutomataTransform):
    def apply(self) -> Automata:
        result: Automata = self.raw_copy()

        # TODO: Finish!
        
        return result

        
