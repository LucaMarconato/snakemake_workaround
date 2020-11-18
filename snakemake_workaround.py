import click
import shutil
import os
import re
import subprocess
from collections import defaultdict
from typing import List, Dict, FrozenSet
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms.simple_paths import all_simple_paths


class Node:
    pass


class FileNode(Node):
    def __init__(self, filename):
        self.filename = filename
        self.id = self.filename
        self.label = os.path.basename(self.filename)
        if self.label == '':
            assert os.path.dirname(self.filename) == os.path.normpath(self.filename)
            self.label = os.path.split(os.path.normpath(self.filename))[1]
        self.color = (0., 1., 0.)


class InputsNode(Node):
    def __init__(self, inputs: FrozenSet[FileNode]):
        self.inputs = inputs
        self.id = str(hash(self.inputs))
        self.label = ''
        self.color = (0., 0., 0.)


class RuleNode(Node):
    def __init__(self, name):
        self.name = name
        self.id = self.name
        self.label = self.name
        self.color = (1., 0., 0.)


nodes: Dict[str, Node] = dict()
edges: Dict[Node, List[Node]] = defaultdict(list)
graph = nx.DiGraph()
label_dict: Dict[str, str] = dict()


def build_graph(rule):
    os.chdir('/data/l989o/deployed/spatial_uzh')

    try:
        s = subprocess.check_output(f'/data/l989o/miniconda3/envs/spatial_uzh2/bin/snakemake {rule} --forceall --rerun-incomplete -n', shell=True).decode('utf-8')
        # print(s)
    except subprocess.CalledProcessError as grepexc:
        print('error code', grepexc.returncode, grepexc.output)
        raise subprocess.CalledProcessError(grepexc)

    r0 = re.compile(r'Building DAG of jobs...\nJob counts:\n\tcount\tjobs\n((?:\t[0-9]+\t[_a-zA-Z0-9]+\n)+)\t[0-9]+\n([\s\S]*?)\nThis was a dry-run \(flag -n\). The order of jobs does not reflect the order of execution.')
    m0 = re.match(r0, s)
    g0, g1 = m0.groups()

    lines = g0.split('\n')
    lines = [s.strip() for s in lines]
    lines = [s for s in lines if s != '']
    r1 = re.compile('[0-9]+\t([_a-zA-Z0-9]+)')
    for line in lines:
        m1 = re.match(r1, line)
        rule_name = m1.groups()[0]
        # graph.add_node(rule_name)
        # print(rule_name)
        # v = RuleNode(rule_name)
        # rule_nodes[v] = rule_name
        # rule_nodes.append(v)

    lines = g1.split('\n\n')
    assert lines[-1].startswith('Job counts:')
    del lines[-1]
    for line in lines:
        ss = line.split('\n')
        ss = [s.strip() for s in ss]
        rule_node = None
        for s in ss:
            if s.startswith('rule'):
                assert rule_node is None
                rule_name = re.match(r'rule\ ([_a-zA-Z0-9]+):', s).groups()[0]
                rule_node = RuleNode(rule_name)
                graph.add_node(rule_node.id)
                nodes[rule_node.id] = rule_node
                label_dict[rule_node.id] = rule_node.label
                # print(rule_name)
            elif s.startswith('localrule'):
                assert rule_node is None
                rule_name = re.match(r'localrule\ ([_a-zA-Z0-9]+):', s).groups()[0]
                rule_node = RuleNode(rule_name)
                graph.add_node(rule_node.id)
                nodes[rule_node.id] = rule_node
                label_dict[rule_node.id] = rule_node.label
            elif s.startswith('input: '):
                inputs = s[len('input: '):].split(', ')
                inputs = sorted(inputs)
                # print(inputs)
                assert rule_node is not None
                # inputs_node = InputsNode(frozenset(inputs))
                # edges[inputs_node].append(rule_node)
                # graph.add_edge(inputs_node.id, rule_node.id)
                # nodes[inputs_node.id] = inputs_node
                # label_dict[inputs_node.id] = inputs_node.label
                for x in inputs:
                    file_node = FileNode(x)
                    edges[file_node].append(rule_node)
                    graph.add_edge(file_node.id, rule_node.id)
                    # edges[file_node].append(inputs_node)
                    # graph.add_edge(file_node.id, inputs_node.id)
                    nodes[file_node.id] = file_node
                    label_dict[file_node.id] = file_node.label
                    # file_nodes[file_node] = x
            elif s.startswith('output: '):
                outputs = s[len('output: '):].split(', ')
                assert rule_node is not None
                for x in outputs:
                    file_node = FileNode(x)
                    edges[rule_node].append(file_node)
                    graph.add_edge(rule_node.id, file_node.id)
                    nodes[file_node.id] = file_node
                    label_dict[file_node.id] = file_node.label
                # print(outputs)


def find_subgraph(node0, node1):
    assert nx.algorithms.is_directed_acyclic_graph(graph)
    if node0 is None and node1 is None:
        return None
    elif node0 is not None and node1 is None:
        nodes_of_paths = nx.algorithms.descendants(graph, node0)
        nodes_of_paths.add(node0)
    else:
        paths = all_simple_paths(graph, node0, node1)
        nodes_of_paths = []
        for path in paths:
            nodes_of_paths.extend(list(path))
    subgraph = graph.subgraph(nodes_of_paths)
    return subgraph


def _plot(subgraph=None):
    plt.figure(figsize=(20, 11))
    # pos = nx.spring_layout(graph)
    colors = [nodes[node_id].color for node_id in graph.nodes()]
    pos = graphviz_layout(graph)
    nx.draw_networkx(graph, pos, with_labels=True, labels=label_dict, font_size=7, arrowstyle='-|>', arrowsize=20, arrows=True, node_color=colors)
    if subgraph is not None:
        orange = (1.0, 0.6823529411764706, 0.25882352941176473, 0.8)
        nx.draw_networkx_edges(subgraph, pos, edge_color=orange, width=3, arrowstyle='-|>', arrowsize=20, arrows=True)
    # plt.savefig('simple_path.png')
    plt.show()


def _rm_command(subgraph):
    assert len(list(nx.isolates(subgraph))) == 0
    to_rm = []
    for node in subgraph.nodes():
        obj = nodes[node]
        if type(obj) == FileNode:
            to_rm.append(obj.filename)
    assert all([' ' not in f for f in to_rm])

    print('ready to delete the following files:')
    print('\n'.join(sorted(to_rm, key=lambda x: x[::-1])))
    if click.confirm('do you want to continue?', default=True):
        for f in to_rm:
            if os.path.isdir(f):
                print('skipping directory:', f)
            else:
                os.remove(f)
    # print(f'for f in {" ".join(to_rm)}; do rm $f; done')


@click.command()
@click.option('--rule', type=str, required=True, help='snakemake rule used to build the dag')
@click.option('--node0', type=str, required=False,
              help='str (rule name or full path)', default=None)
@click.option('--node1', type=str, required=False,
              help='str (rule name or full path)', default=None)
def plot(rule, node0, node1):
    assert not (node1 is not None and node0 is None)
    build_graph(rule)
    subgraph = find_subgraph(node0, node1)
    _plot(subgraph)


@click.command()
@click.option('--rule', type=str, required=True, help='snakemake rule used to build the dag')
@click.option('--node0', type=str, required=False,
              help='str (rule name or full path)', default=None)
@click.option('--node1', type=str, required=False,
              help='str (rule name or full path)', default=None)
@click.option('--plot', type=bool, required=False, help='plot the graph', default=False)
def rm_command(rule, node0, node1, plot):
    build_graph(rule)
    subgraph = find_subgraph(node0, node1)
    _rm_command(subgraph)
    if plot:
        _plot(subgraph)


@click.group()
def cli():
    pass


cli.add_command(plot)
cli.add_command(rm_command)

if __name__ == '__main__':
    cli()
