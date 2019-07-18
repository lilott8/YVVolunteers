import abc
import logging
from typing import Dict, List
from enum import IntEnum
from member import Member
from member import RoleEnums
import operator
import json
import math


class HeuristicEnum(IntEnum):
    NAIVE = 1
    LANGUAGE = 2
    FRAMEWORK = 4
    EXPERIENCE = 8
    MAGIC = 16

    def get_strategy(self, size: int) -> 'Heuristic':
        if self.value == HeuristicEnum.LANGUAGE:
            return LanguageHeuristic(size)
        elif self.value == HeuristicEnum.FRAMEWORK:
            return FrameworkHeuristic(size)
        elif self.value == HeuristicEnum.EXPERIENCE:
            return ExperienceHeuristic(size)
        elif self.value == HeuristicEnum.MAGIC:
            return MagicHeuristic(size)
        else:
            return NaiveHeuristic(size)

    @staticmethod
    def get_heuristic(heuristic: str = "naive"):
        heuristic.lower()
        if heuristic == 'language':
            return HeuristicEnum.LANGUAGE
        elif heuristic == 'framework':
            return HeuristicEnum.FRAMEWORK
        elif heuristic == 'experience':
            return HeuristicEnum.EXPERIENCE
        elif heuristic == 'magic':
            return HeuristicEnum.MAGIC
        else:
            return HeuristicEnum.NAIVE


class Heuristic(metaclass=abc.ABCMeta):
    """
    The base class for the heuristic.
    This is the base strategy class
    """
    def __init__(self, size: int, heuristic: HeuristicEnum):
        self.log = logging.getLogger(self.__class__.__name__)
        self.size = size
        self.heuristic = heuristic
        self.administrative = dict()
        self.groups = dict()
        self.leaders = list()
        self.log.info("Using " + self.heuristic.name)

    @abc.abstractmethod
    def preprocess(self, members: List):
        # Put the leaders in their own structure.
        x = 0
        while x < len(members):
            if members[x].roles & RoleEnums.LEADER:
                self.leaders.append(members[x].email)
                del members[x]
            x += 1

        # Build the groups required for assignment.
        for x in range(0, math.ceil(len(members)/self.size)+1):
            self.groups[x] = {'members': list(), 'leader': None, 'expertise': set()}

    @abc.abstractmethod
    def build_groups(self, members: List[Member]) -> str:
        pass

    @staticmethod
    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError

    def to_json(self) -> str:
        return json.dumps({"groups": self.groups, "leaders": self.leaders,
                           'admin': self.administrative}, indent=4, sort_keys=True, default=Heuristic.set_default)


class NaiveHeuristic(Heuristic):
    """
    This will fill each group before moving onto the next.
    """
    def __init__(self, size: int):
        super().__init__(size, HeuristicEnum.NAIVE)

    def preprocess(self, members: List):
        super().preprocess(members)

    def build_groups(self, members: List[Member]) -> str:
        self.preprocess(members)

        x = 0
        y = 0
        while x < len(members):
            while len(self.groups[y]) < self.size and x < len(members):
                self.groups[y].append(members[x].email)
                x += 1
            y += 1

        return self.to_json()


class LanguageHeuristic(Heuristic):
    """
    This builds the groups by languages.
    """
    def __init__(self, size: int):
        super().__init__(size, HeuristicEnum.LANGUAGE)
        self.buckets = dict()

    def preprocess(self, members: List):
        super().preprocess(members)
        for m in members:
            for l in m.ranking['languages']:
                if l not in self.buckets:
                    self.buckets[l] = set()
                self.buckets[l].add(m)

    def build_groups(self, members: List[Member]) -> str:
        self.preprocess(members)
        x = 0
        assigned = set()
        for k, v in self.buckets.items():
            for m in v:
                if len(self.groups[x]['members']) < self.size:
                    if m not in assigned and k in m.ranking['languages']:
                        self.groups[x]['members'].append(m.email)
                        assigned.add(m)
                else:
                    x += 1
                self.groups[x]['expertise'].add(k.name)
        return self.to_json()


class FrameworkHeuristic(Heuristic):
    """
    This will assign groups by the framework familiarity.
    """
    def __init__(self, size: int):
        super().__init__(size, HeuristicEnum.FRAMEWORK)
        self.buckets = dict()

    def preprocess(self, members: List):
        # Build the leaders.
        super().preprocess(members)
        for m in members:
            for f in m.ranking['frameworks']:
                if f not in self.buckets:
                    self.buckets[f] = set()
                self.buckets[f].add(m)

    def build_groups(self, members: List[Member]) -> str:
        self.preprocess(members)
        assigned = set()
        x = 0
        for k, v in self.buckets.items():
            for m in v:
                if len(self.groups[x]['members']) < self.size:
                    if m not in assigned and k in m.ranking['frameworks']:
                        self.groups[x]['members'].append(m.email)
                        assigned.add(m)
                else:
                    x += 1
                self.groups[x]['expertise'].add(k)
        return self.to_json()


class ExperienceHeuristic(Heuristic):
    """
    This will attempt to match people with lots of
    experience with those that don't have as much.
    """
    def __init__(self, size: int):
        super().__init__(size, HeuristicEnum.EXPERIENCE)
        self.buckets = dict()

    def preprocess(self, members: List):
        super().preprocess(members)

    def build_groups(self, members: List[Member]) -> str:
        self.preprocess(members)
        sorted_members = sorted(members, key=operator.attrgetter('experience'))
        forward = 0
        backward = len(sorted_members)-1
        x = 0
        y = 0
        while forward != backward and x < len(self.groups):
            if len(self.groups[x]) < self.size:
                self.groups[x].append(sorted_members[forward].email)
                self.groups[x].append(sorted_members[backward].email)
                backward -= 1
                forward += 1
            else:
                x += 1
            y += 1

        return self.to_json()


class MagicHeuristic(Heuristic):
    """
    This does dark magic!
    """
    def __init__(self, size: int):
        super().__init__(size, HeuristicEnum.MAGIC)

    def preprocess(self, members: List):
        super().preprocess(members)

    def build_groups(self, members: List[Member]) -> str:
        self.log.warning("This isn't implemented yet, using " + self.heuristic.NAIVE.name)
        naive = NaiveHeuristic(self.size)
        naive.build_groups(members)
        return naive.to_json()
