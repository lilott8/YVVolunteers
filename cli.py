import argparse
from argparse import Namespace
import os
from heuristics import *
import json


class Config(object):
    """
    A simple configuration object.
    This houses all the necessary config data
    for the program to run.
    """
    def __init__(self, args: Namespace):
        """
        Build a configuration object to be used in the program.
        :param args: argument namespace, the arguments from the CLI.
        """
        # Save this, jic
        self.args = args
        """
        I/O and path related configurations.
        """
        self.input_file = os.path.normpath(args.input)
        self.input_dir = os.path.normpath(args.input.split("/")[-1].split(".")[0])

        if args.output:
            self.output = os.path.normpath(args.output)
        else:
            self.output = self.input_dir

        """
        Taxonomies of things
        """
        self.taxonomy_path = args.taxonomy
        self.taxonomy = {'js_frameworks': {}, 'programming_languages': {}, 'continuous_integration': {}}
        with open(self.taxonomy_path, 'r') as f:
            taxonomy = json.load(f)
        self.taxonomy['frameworks'] = taxonomy['frameworks']
        self.taxonomy['languages'] = taxonomy['languages']
        self.taxonomy['continuous_integration'] = taxonomy['continuous_integration']
        self.taxonomy['framework_synonyms'] = taxonomy['framework_synonyms']
        self.taxonomy['design_skills'] = taxonomy['design_skills']

        """
        Group assignment configurations.
        """
        self.group_size = args.size
        self.key = args.key
        self.heuristic = HeuristicEnum.get_heuristic(args.group)

        self.prebuilt_teams = False
        self.teams = None
        if args.teams:
            self.prebuilt_teams = True
            self.teams = os.path.normpath(args.teams)


class CLI(object):
    """
    The Command Line parser object responsible for
    building the parameters a user can configure.
    """
    def __init__(self):
        """
        Build the argparser for our CLI.
        """
        self.parser = argparse.ArgumentParser()
        # I/O and path related arguments.
        self.parser.add_argument('-i', '--input', help='Where is the input?', type=str, required=True)
        self.parser.add_argument('-o', '--output', help="path to write to", type=str)

        # Assignment details.
        self.parser.add_argument('-s', '--size', help='What is the max group size', type=int, default=3)
        self.parser.add_argument('-key', '--key', help='What is the unique identifier for the group member',
                                 type=str, default='email')
        self.parser.add_argument('-g', '--group', help='Which heuristic to use to assign teams', type=str,
                                 choices={'naive', 'language', 'framework', 'experience', 'magic'}, default='naive')
        self.parser.add_argument('-t', '--taxonomy', help="The json taxonomy of things", type=str, required=True)
        self.parser.add_argument('-pbt', '--teams', help='Path to json with pre-built teams', type=str, required=False)

    def build_config(self, args: str) -> Config:
        """
        Build a config object for our program.
        :param args: the raw input from the CLI.
        :return: Config object.
        """
        return Config(self.parser.parse_args(args))
