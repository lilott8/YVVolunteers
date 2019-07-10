import abc
from enum import IntFlag
from typing import Set, List, Dict


class RoleEnums(IntFlag):
    DESIGNER = 1
    DEVELOPER = 2
    LEADER = 4


class Profession(metaclass=abc.ABCMeta):
    """
    The base class for Designer, Developer, and Leader.
    """
    def __init__(self, role: RoleEnums, skills: Set, experience: int, confidence: int):
        self.skills = skills
        self.experience = experience
        self.confidence = confidence
        self.rid = role


class Designer(Profession):
    """
    A designer position.
    """
    def __init__(self, confidence: int = -1, frameworks: Set = Set,
                 js_proficiency: int = -1, experience: int = -1, design_skills: Set = Set):
        super().__init__(RoleEnums.DESIGNER, frameworks, experience, confidence)
        self.js_proficiency = js_proficiency
        self.design_skills = design_skills


class Developer(Profession):
    """
    A developer position.
    """
    def __init__(self, backend_confidence: int = -1, frontend_confidence: int = -1, oss: int = 0, linter: bool = False,
                 tdd: bool = False, code_review: bool = False, ci: bool = False, ci_frameworks: Set = Set,
                 languages: Set = Set, frameworks: Set = Set, dbms: bool = False,
                 data_analytics: bool = False, experience: int = -1):
        super().__init__(RoleEnums.DEVELOPER, frameworks, experience, backend_confidence)
        self.fe_confidence = frontend_confidence
        self.languages = languages
        self.oss = oss
        self.linter = linter
        self.tdd = tdd
        self.code_review = code_review
        self.ci = ci
        self.ci_frameworks = ci_frameworks
        self.dbms = dbms
        self.data_analytics = data_analytics
        self.frameworks = frameworks


class Leader(Profession):
    """
    A leader position.
    """
    def __init__(self, experience: int = -1):
        super().__init__(RoleEnums.LEADER, set(), experience, -1)


class Member(metaclass=abc.ABCMeta):
    """
    A member or volunteer object.
    """
    def __init__(self, uid, email, portfolio: List = list(), professions: Set = set(),
                 ranking: Dict = Dict, experience: int = 0):
        self.confidence = 0
        self.uid = uid
        self.email = email
        self.experience = experience
        self.roles = set()
        self.professions = professions
        self.roles = 0
        for r in professions:
            self.roles += r.rid
        self.portfolio = portfolio
        self.ranking = ranking

    @staticmethod
    def build_ranking(taxonomy: Dict, languages: Set = Set, frameworks: Set = Set, rids: IntFlag = 0) -> Dict:
        ranking = {'frontend': 0, 'backend': 0, 'languages': set(), 'frameworks': set(), 'rids': rids}

        for l in languages:
            ranking['languages'].add(l)

        for f in frameworks:
            fw = f if f not in taxonomy['framework_synonyms'] else taxonomy['framework_synonyms'][f]
            if taxonomy['frameworks'][fw]['classification'] == 'frontend':
                ranking['frontend'] += 1
            else:
                ranking['backend'] += 1
            ranking['languages'].add(taxonomy['frameworks'][fw]['language'])
            ranking['frameworks'].add(fw)

        return ranking

    def __repr__(self):
        output = "{} ({}) -- {}".format(self.uid, self.email, self.roles)

        # for k, v in self.ranking.items():
        #     output += "{}:({})\t".format(k, v)
        # if RoleEnums.DESIGNER & self.role:
        #     output += "\tdesigner"
        # if RoleEnums.DEVELOPER & self.role:
        #     output += "\tdeveloper"
        # if RoleEnums.LEADER & self.role:
        #     output += "\tleader"
        # output += "\n\t"
        #

        # output += "({})".format(self.roles)

        return output
