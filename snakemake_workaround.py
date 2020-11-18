import click
import os
import re
import subprocess
from collections import defaultdict
from typing import List, Dict, FrozenSet
from bidict import bidict
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms.simple_paths import all_simple_paths


# function smk_out () {
#         files=`snakemake $1 --force --rerun-incomplete -n | perl -0777pe "s/[\s\S]*rule $1:\n[[:space:]]+input: (.*)[\s\S]*/\1/g" | tr "," " " | xargs`
#         echo $files
# }


# @click.command()
# def (instance_hash, compute, visualize):
#
#
# @click.group()
# def cli():
#     pass
#
#
# cli.add_command(benchmark_neighbors_reconstruction)
#
# if __name__ == '__main__':
#     cli()

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


#
# class Edge:
#     def __init__(self, input_node, output_node):
#         self.input_node = input_node
#         self.output_node = output_node


# file_nodes: bidict[FileNode, str] = bidict()
# rule_nodes: bidict[RuleNode, str] = bidict()
nodes: Dict[str, Node] = dict()
edges: Dict[Node, List[Node]] = defaultdict(list)
graph = nx.DiGraph()
label_dict: Dict[str, str] = dict()

if __name__ == '__main__':
    os.chdir('/data/l989o/deployed/spatial_uzh')
    rule = 'short'
    node0 = 'precompute_global_cell_indices'
    node1 = 'short'
    # subprocess.run('bash -c "source activate spatial_uzh2; python -V"', shell=True)
    # s = subprocess.check_output(f'snakemake {rule} --force --rerun-incomplete -n', shell=True)

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
                inputs_node = InputsNode(frozenset(inputs))
                edges[inputs_node].append(rule_node)
                graph.add_edge(inputs_node.id, rule_node.id)
                nodes[inputs_node.id] = inputs_node
                label_dict[inputs_node.id] = inputs_node.label
                for x in inputs:
                    file_node = FileNode(x)
                    # e = Edge(file_node, inputs_node)
                    edges[file_node].append(inputs_node)
                    graph.add_edge(file_node.id, inputs_node.id)
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
    assert nx.algorithms.is_directed_acyclic_graph(graph)

    node1 = None
    if node1 is None:
        nodes_of_paths = nx.algorithms.descendants(graph, node0)
    else:
        paths = all_simple_paths(graph, node0, node1)
        nodes_of_paths = []
        for path in paths:
            nodes_of_paths.extend(list(path))
    subgraph = graph.subgraph(nodes_of_paths)

    plt.figure(figsize=(20, 11))
    # pos = nx.spring_layout(graph)
    colors = [nodes[node_id].color for node_id in graph.nodes()]
    pos = graphviz_layout(graph)
    nx.draw_networkx(graph, pos, with_labels=True, labels=label_dict, font_size=7, arrowstyle='-|>', arrowsize=20, arrows=True, node_color=colors)
    orange = (1.0, 0.6823529411764706, 0.25882352941176473, 0.8)
    nx.draw_networkx_edges(subgraph, pos, edge_color=orange, width=3)
    # plt.savefig('simple_path.png')
    plt.show()
    print('ehi')
