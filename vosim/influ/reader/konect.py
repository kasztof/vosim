import csv
import os
import pathlib
import shutil
import tarfile
from collections import ChainMap
from itertools import islice
from typing import List, Optional

import igraph as ig
import yaml
import requests

from .direct import read_graph

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class DownloadFailure(Exception):
    pass


def konect_to_csv(source_path: str, dest_path: str, edge_attrs: List[str] = None) -> None:
    """
    Converts konect dataset to format readable by influ.

    :param source_path: path to the out file downloaded from konect
    :param dest_path: path to destination where to save a file
    :param edge_attrs: optional edge attributes that are known to exists in out file
        if this parameter is missing or there are more attributes then unnamed attributes will be named as attr{index}
    """
    edge_attrs = edge_attrs or []

    with open(source_path, 'r') as source_file:
        with open(dest_path, 'w') as dest_file:
            dest_writer = csv.writer(dest_file)
            source_file = islice(source_file, 2, None)
            first_line = next(source_file).split()

            cattrs = len(edge_attrs)
            header = ['source', 'target'] + edge_attrs + [f'attr{i}' for i in range(cattrs, len(first_line) - 2)]

            dest_writer.writerow(header)
            dest_writer.writerow(first_line)

            for line in source_file:
                dest_writer.writerow(line.split())


class KonectReader:
    def __init__(self, config: Optional[str] = None) -> None:
        """
        Initialize reader object.

        :param config: path to yaml file with config
        """
        self.datasets = ChainMap()
        self.list = []

        self.add_config(f'{DIR_PATH}/datasets.yaml')
        if config:
            self.add_config(config)

        self.archive_dir = './datasets/archive'
        self.extracted_dir = './datasets/extracted'

    def add_config(self, path: str) -> None:
        """
        Update available datasets

        :param path: path to config file
        """
        with open(path) as f:
            self.datasets = self.datasets.new_child(yaml.load(f))
        self.list = list(self.datasets.keys())

    def load(self, dataset_name: str) -> ig.Graph:
        """
        Loads dataset from http://konect.uni-koblenz.de

        :type dataset_name: name of the dataset to load; available datasets are in 'list' attribute
        :return: loaded graph
        """
        self.download(dataset_name)
        self.extract_tbz2(dataset_name)
        dest_path = self.convert_to_csv(dataset_name)
        graph = read_graph(dest_path, 'events', directed=self.datasets[dataset_name])
        graph['name'] = self.datasets[dataset_name]['name']
        self.apply_vs_attributes(dataset_name, graph)
        return graph

    def download(self, dataset_name: str) -> None:
        """Downloads dataset from konect"""
        pathlib.Path(self.archive_dir).mkdir(parents=True, exist_ok=True)

        donwload_url = self.datasets[dataset_name]['download']
        file_path = self.arch_path(dataset_name)

        if not pathlib.Path(file_path).exists():
            try:
                response = requests.get(donwload_url)
            except requests.ConnectionError:
                raise DownloadFailure("Cannot connect to Konect")

            with open(file_path, "wb") as file:
                file.write(response.content)

    def extract_tbz2(self, dataset_name: str) -> None:
        """Extracts downloaded dataset"""
        dir_path = self.extr_path(dataset_name)
        path = pathlib.Path(dir_path)
        if path.exists():
            shutil.rmtree(dir_path)
        path.mkdir(parents=True)

        file = tarfile.open(name=self.arch_path(dataset_name))
        file.extractall(path=dir_path)
        inner = f'{dir_path}/{os.listdir(dir_path)[0]}'
        for filename in os.listdir(inner):
            shutil.move(src=f'{inner}/{filename}', dst=f'{dir_path}/{filename}')
        shutil.rmtree(inner)

    def convert_to_csv(self, dataset_name: str) -> str:
        extrp = self.extr_path(dataset_name)
        source_path = f'{extrp}/{self.datasets[dataset_name]["file"]}'
        dest_path = f'{extrp}/{dataset_name}.csv'
        konect_to_csv(source_path, dest_path, self.datasets[dataset_name]['edge_attributes'])

        return dest_path

    def apply_vs_attributes(self, dataset_name: str, graph: ig.Graph) -> None:
        for attr in self.datasets[dataset_name]['vertex_attributes']:
            source_file = f'{self.extr_path(dataset_name)}/{attr["file"]}'
            with open(source_file) as f:
                csv_f = csv.reader(f)
                graph.vs[attr['name']] = [values[-1] for values in csv_f]

    def arch_path(self, dataset_name: str) -> str:
        """Path to archive file with dataset"""
        file_type = self.datasets[dataset_name].get('file_type', 'tar.bz2')
        return f'{self.archive_dir}/{dataset_name}.{file_type}'

    def extr_path(self, dataset_name: str) -> str:
        """Path to extracted dataset"""
        return f'{self.extracted_dir}/{dataset_name}'
