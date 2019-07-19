import abc
import logging
from typing import Dict, List
from enum import IntEnum
import operator
import json


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
    def preprocess(self, members: Dict):
        for l in members['leaders']:
            self.leaders.append(l.email)
        pass

    @abc.abstractmethod
    def build_groups(self, volunteers: Dict) -> str:
        pass

    def add_group(self, x: int):
        if x not in self.groups:
            self.groups[x] = {'members': list(), 'leader': None, 'expertise': set()}

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

    def preprocess(self, members: Dict):
        super().preprocess(members)

    def build_groups(self, volunteers: Dict) -> str:
        self.preprocess(volunteers)

        x = 0
        y = 0
        self.add_group(y)
        while x < len(volunteers['members'])-1:
            while len(self.groups[y]['members']) < self.size and x < len(volunteers['members']):
                self.groups[y]['members'].append(volunteers['members'][x].email)
                x += 1
            self.groups[y]['expertise'].add("I don't know!?")
            y += 1
            self.add_group(y)

        return self.to_json()


class LanguageHeuristic(Heuristic):
    """
    This builds the groups by languages.
    """
    def __init__(self, size: int):
        super().__init__(size, HeuristicEnum.LANGUAGE)
        self.buckets = dict()
        self.unassigned = set()

    def preprocess(self, volunteers: Dict):
        super().preprocess(volunteers)
        for m in volunteers['members']:
            self.unassigned.add(m.email)
            for l in m.ranking['languages']:
                if l not in self.buckets:
                    self.buckets[l] = set()
                self.buckets[l].add(m)

    def build_groups(self, volunteers: Dict) -> str:
        self.preprocess(volunteers)
        x = 0
        self.add_group(x)
        assigned = set()
        for k, v in self.buckets.items():
            for m in volunteers['members']:
                if m.email not in assigned and k in m.ranking['languages'] and \
                        len(self.groups[x]['members']) < self.size:
                    self.groups[x]['members'].append(m.email)
                    assigned.add(m.email)
                    self.unassigned.remove(m.email)
                if len(self.groups[x]['members']) == self.size:
                    self.groups[x]['expertise'] = k.name
                    x += 1
                    self.add_group(x)
        # Clean up the last few that might exist.
        # At this point we dont' have a cohesive group,
        # so we will blindly add them to any group.
        for u in self.unassigned:
            if len(self.groups[x]['members']) < self.size:
                self.groups[x]['members'].append(u)
            else:
                x += 1
                self.add_group(x)
        return self.to_json()


class FrameworkHeuristic(Heuristic):
    """
    This will assign groups by the framework familiarity.
    """
    def __init__(self, size: int):
        super().__init__(size, HeuristicEnum.FRAMEWORK)
        self.buckets = dict()
        self.unassigned = set()

    def preprocess(self, members: Dict):
        # Build the leaders.
        super().preprocess(members)
        for m in members['members']:
            self.unassigned.add(m.email)
            for f in m.ranking['frameworks']:
                if f not in self.buckets:
                    self.buckets[f] = set()
                self.buckets[f].add(m)

    def build_groups(self, volunteers: Dict) -> str:
        self.preprocess(volunteers)
        x = 0
        self.add_group(x)
        assigned = set()
        for k, v in self.buckets.items():
            for m in volunteers['members']:
                if m.email not in assigned and k in m.ranking['frameworks'] and \
                        len(self.groups[x]['members']) < self.size:
                    self.groups[x]['members'].append(m.email)
                    assigned.add(m.email)
                    self.unassigned.remove(m.email)
                if len(self.groups[x]['members']) == self.size:
                    self.groups[x]['expertise'] = k
                    x += 1
                    self.add_group(x)
        # Clean up the last few that might exist.
        # At this point we dont' have a cohesive group,
        # so we will blindly add them to any group.
        for u in self.unassigned:
            if len(self.groups[x]['members']) < self.size:
                self.groups[x]['members'].append(u)
            else:
                x += 1
                self.add_group(x)

        return self.to_json()


class ExperienceHeuristic(Heuristic):
    """
    This will attempt to match people with lots of
    experience with those that don't have as much.
    """
    def __init__(self, size: int):
        super().__init__(size, HeuristicEnum.EXPERIENCE)
        self.buckets = dict()

    def preprocess(self, members: Dict):
        super().preprocess(members)

    def build_groups(self, volunteers: Dict) -> str:
        self.preprocess(volunteers)
        sorted_members = sorted(volunteers['members'], key=operator.attrgetter('experience'))
        forward = 0
        backward = len(sorted_members)-1
        x = 0
        y = 0
        total = 0
        self.add_group(x)
        while forward != backward:
            if len(self.groups[x]['members']) < self.size:
                self.groups[x]['members'].append(sorted_members[forward].email)
                self.groups[x]['members'].append(sorted_members[backward].email)
                backward -= 1
                forward += 1
                total += sorted_members[forward].experience + sorted_members[backward].experience
            else:
                self.groups[x]['expertise'] = total
                x += 1
                total = 0
                self.add_group(x)

            y += 1
        # add the last person to the group.
        self.groups[x]['members'].append(sorted_members[backward].email)
        self.groups[x]['expertise'] = total

        return self.to_json()


class MagicHeuristic(Heuristic):
    """
    This does dark magic!
    """
    def __init__(self, size: int):
        super().__init__(size, HeuristicEnum.MAGIC)

    def preprocess(self, members: Dict):
        super().preprocess(members)

    def build_groups(self, volunteers: Dict) -> str:
        self.log.warning("This isn't implemented yet, using " + self.heuristic.NAIVE.name)
        naive = NaiveHeuristic(self.size)
        naive.build_groups(volunteers)
        return naive.to_json()
