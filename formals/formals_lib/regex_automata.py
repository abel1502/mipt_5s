from __future__ import annotations
import typing
import dataclasses
from collections import deque
import itertools

from .automata import *
from .automata_ops import *
from .regex import *
from .itree import TreeVisitor
from .automata_determ import make_edges_1, unify_term


class RegexToAutomataConverter(TreeVisitor[Regex]):
    warn_on_generic: typing.ClassVar[bool] = True
    
    @TreeVisitor.handler(Letter)
    def visit_letter(self, node: Letter) -> Automata:
        result = Automata(node.letter)
        
        result.link(result.start, result.make_node(term=True), node.letter)
        
        return result
    
    @TreeVisitor.handler(Zero)
    def visit_zero(self, node: Zero) -> Automata:
        result = Automata("")
        
        return result
    
    @TreeVisitor.handler(One)
    def visit_one(self, node: One) -> Automata:
        result = Automata("")
        
        result.start.is_term = True
        
        return result
    
    @TreeVisitor.handler(Concat)
    def visit_concat(self, node: Concat) -> Automata:
        children: typing.Iterable[Regex] = node.get_children()
        
        if len(children) == 0:
            return self.visit(One())
        
        children: typing.Iterator[Regex] = iter(children)
        
        result: Automata = self.visit(next(children))
        for child in children:
            result = concat(result, self.visit(child))
        
        return result

    @TreeVisitor.handler(Star)
    def visit_star(self, node: Star) -> Automata:
        return star(self.visit(node.get_children()[0]))

    @TreeVisitor.handler(Either)
    def visit_either(self, node: Either) -> Automata:
        children: typing.Iterable[Regex] = node.get_children()
        
        if len(children) == 0:
            return self.visit(Zero())
        
        children: typing.Iterator[Regex] = iter(children)
        
        result: Automata = self.visit(next(children))
        for child in children:
            result = join(result, self.visit(child))
        
        return result


# TODO: Maybe implement later
class AutomataToRegexConverter:
    aut: Automata
    
    def __init__(self, aut: Automata):
        self.aut = aut
    
    def _convert_to_re_automata(self) -> None:
        # Very dirty, but works:
        # Internally, we simply use Regex'es for
        # automata edge labels. Have to be careful with 
        
        # Copying to avoid messing up the iteration
        for edge in list(self.aut.get_edges()):
            self.aut.unlink(edge)
            self.aut.link(edge.src, edge.dst, Letter(edge.label))
        
        for node in self.aut.get_nodes():
            self._add_loop(node)
    
    def _add_loop(self, node: Node) -> None:
        for edge in node.get_edges():
            if edge.dst is node:
                return
        
        self.aut.link(node, node, Zero())
    
    def apply(self) -> Regex:
        self._prepare()
        
        self._merge_parallel_edges()
        
        while len(self.aut) > 2:
            self._step()
        
        return self._finalize()
    
    def _prepare(self) -> None:
        self.aut = make_edges_1(self.aut)
        self.aut = unify_term(self.aut)
        
        self._convert_to_re_automata()
    
    def _step(self) -> None:
        target: Node = self._find_target()
        
        edges_in: typing.Iterable[Edge] = (
            e for e in self.aut.get_edges()
            if e.dst is target and e.src is not target
        )
        edges_out: typing.Iterable[Edge] = target.out
        
        for edge_in, edge_out in itertools.product(edges_in, edges_out):
            edge_in: Edge
            edge_out: Edge
            
            ...
    
    def _find_target(self) -> Node:
        raise NotImplementedError()
    
    def _finalize(self) -> Regex:
        raise NotImplementedError()
    
    def _merge_parallel_edges(self) -> None:
        raise NotImplementedError()

       
def regex_to_automata(regex: Regex) -> Automata:
    return RegexToAutomataConverter().visit(regex)


def automata_to_regex(aut: Automata) -> Regex:
    return AutomataToRegexConverter(aut).apply()
