import cli
import csv
import logging
from member import Member, Designer, Developer, Leader
from typing import Dict, List, Set
from enums import ProgrammingLanguages as PL
from enums import ContinuousIntegration as CI
import re


class Volunteers(object):

    def __init__(self, config: cli.Config):
        self.log = logging.getLogger(self.__class__.__name__)
        self.config = config

    def build_volunteers(self) -> List:
        """
        This parses the input file and builds the members and their roles.
        :return: List of users
        """
        members = list()
        with open(self.config.input_file, 'r') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            uid = 1
            for row in reader:
                if row['Username'] == 'Iyasu.shinsei@gmail.com':
                    x = 1
                roles = set()
                rids = 0
                frameworks = set()
                languages = set()
                portfolios = list()
                experience = 0
                if row["In general, I would consider myself capable of being a designer volunteer"] == "Yes":
                    if len(row["My portfolio's URL is"]) > 0:
                        portfolios.append(row["My portfolio's URL is"])
                    role = self.build_designer(uid, row)
                    experience += role.experience
                    frameworks.update(role.skills)
                    roles.add(role)
                    rids += role.rid

                if row["In general, I would consider myself capable of being a volunteer developer"] == "Yes":
                    if len(row["Github URL"]) > 0:
                        portfolios.append(row["Github URL"])
                    role = self.build_developer(row)
                    frameworks.update(role.frameworks)
                    languages.update(role.languages)
                    experience += role.experience
                    roles.add(role)
                    rids += role.rid

                if row["I would like to be considered for a team lead role"] == "Yes":
                    roles.add(Leader(Volunteers.parse_experience(
                        row["How long have you been managing people/product(s)"])))
                members.append(Member(uid, row['Username'], portfolios, roles,
                                      Member.build_ranking(self.config.taxonomy, frameworks=frameworks,
                                                           languages=languages, rids=rids), experience=experience))
                uid += 1
        return members

    def parse_frameworks(self, js_fw: str) -> Set:
        """
        Attempts to parse the various frameworks that where inputs from users.
        :param js_fw: The string of frameworks.
        :return: The framework reference from the taxonomy.
        """
        js = set()
        for f in re.split(' |,|;', js_fw.lower()):
            if f in self.config.taxonomy['frameworks']:
                js.add(f)
            elif f in self.config.taxonomy['framework_synonyms']:
                js.add(f)
            else:
                for s in f.split('.'):
                    if s in self.config.taxonomy['frameworks']:
                        js.add(s)
                    elif s in self.config.taxonomy['framework_synonyms']:
                        js.add(s)
                    else:
                        js.add("General Backend")
        return js

    def parse_programming_languages(self, pl_known: str) -> Set:
        """
        Attempts to parse programming languages as input from users.
        :param pl_known: The string of programming languages.
        :return: A set of known programming languages.
        """
        pl = set()
        for f in pl_known.lower().split(';'):
            if f in self.config.taxonomy['languages']:
                pl.add(PL(self.config.taxonomy['languages'][f]))
            else:
                for s in re.split(' |,|;', f):
                    if s in self.config.taxonomy['languages']:
                        pl.add(PL(self.config.taxonomy['languages'][s]))
                    else:
                        pl.add(PL.UNKNOWN)
        return pl

    def parse_ci_frameworks(self, fw: str) -> Set:
        """
        Attempts to parse the continuous integration frameworks.
        :param fw: The string input of CI frameworks.
        :return: A set of CI frameworks the user knows.
        """
        ci = set()
        for f in re.split(" |,|/", fw.lower().replace("(", '').replace(")", '')):
            if f in self.config.taxonomy['continuous_integration']:
                ci.add(CI(self.config.taxonomy['continuous_integration'][f]))
        return ci

    def parse_design_skills(self, ds: List) -> Set:
        """
        Parse the design skills of a user.
        :param ds: The list of skills a user might have.
        :return: set of skills.
        """
        skillz = set()
        for d in ds:
            if d in self.config.taxonomy['design_skills']:
                skillz.add(d)
            else:
                skillz.add('General Frontend')
        return skillz

    @staticmethod
    def parse_experience(exp: str) -> int:
        """
        Identifies the experience a user has.
        :param exp: the selected range of experience.
        :return: the lower bound of experience.
        """
        if exp == '0-1 year':
            return 1
        elif exp == '2-4 years':
            return 2
        elif exp == '5-7 years':
            return 5
        elif exp == '8-10 years':
            return 8
        elif exp == '10+ years':
            return 10
        else:
            return 1

    def build_designer(self, uid: int, row: Dict) -> Designer:
        """
        As of 2019-07-05 the field mappings are:
            portfolio                       =>  "My portfolio's URL is"
            confidence                      =>  "I would rate my design skills as"
            skills                          =>  "My top 3 design skills are"
            confidence                      =>  "I am confident in my front end skills"
            js_framework_proficiency_rating =>  "I am proficient with at least one JS Framework"
            js_framework_proficiency        =>  "The framework I would say I'm most confident in is"
            experience                      =>  "I've been a designer for"
        This will map the row headers to variables and build a role based on the information.
        :param row: full record row of the CSV file.
        :return: Designer role object.
        """
        confidence = row["I would rate my design skills as"]
        skills = self.parse_design_skills(row["My top 3 design skills are"].split(";"))
        js_framework_proficiency_rating = row["I am proficient with at least one JS Framework"]
        js_framework_proficiency = self.parse_frameworks(row["The framework I would say I'm most confident in is"])
        skills.update(js_framework_proficiency)
        experience = Volunteers.parse_experience(row["I've been a designer for"])
        return Designer(confidence=confidence, js_proficiency=js_framework_proficiency_rating, design_skills=skills,
                        frameworks=js_framework_proficiency, experience=experience)

    def build_developer(self, row: Dict) -> Developer:
        """
        As of 2019-07-05 the field mappings are:
            portfolio                   =>  "Github URL"
            backend_confidence          =>  "I am confident in my backend skills"
            frontend_confidence         =>  "I am confident in my front end skills"
            oss_contribution            =>  "I have experience contributing to open source (OSS) projects"
            linter_knowledge            =>  "I know what a Linter is and what purpose it serves"
            tdd_knowledge               =>  "I know Test-Driven Development (TDD)"
            ci_knowledge                =>  "I use Continuous Integration (CI) for my projects"
            ci_frameworks               =>  "If yes, which CI platform(s)"
            code_review_subject         =>  "Code I wrote has been subject to code reviews"
            programming_proficiencies   =>  "My top 3 programming languages are"
            framework_proficiencies     =>  "My top 3 frameworks are"
            experience                  =>  "I've been a programming for"
            dbms_experience             =>  "I have experience with Database Management Systems (DBMS)"
            data_analytics_experience   =>  "I have experience in data analytics"
        :param row: full record row of the CSV file.
        :return: Developer role object.
        """
        backend_confidence = int(row["I am confident in my backend skills"])
        frontend_confidence = int(row["I am confident in my front end skills"])
        oss_contribution = row["I have experience contributing to open source (OSS) projects"]
        linter_knowledge = True if row["I know what a Linter is and what purpose it serves"] == "Yes" else False
        ci_knowledge = True if row["I use Continuous Integration (CI) for my projects"] == "Yes" else False
        ci_frameworks = self.parse_ci_frameworks(row["If yes, which CI platform(s)"])
        tdd_knowledge = int(row["I know Test-Driven Development (TDD)"])
        code_review = True if row["Code I wrote has been subject to code reviews"] == "Yes" else False
        programming_proficiencies = self.parse_programming_languages(row["My top 3 programming languages are"])
        framework_proficiencies = self.parse_frameworks(row["My top 3 frameworks are"])
        experience = Volunteers.parse_experience(row["I've been a programming for"])
        dbms_experience = row["I have experience with Database Management Systems (DBMS)"]
        data_analytics_experience = row["I have experience in data analytics"]
        skills = programming_proficiencies.union(framework_proficiencies)
        return Developer(backend_confidence=backend_confidence, frontend_confidence=frontend_confidence,
                         oss=oss_contribution, linter=linter_knowledge, ci=ci_knowledge, ci_frameworks=ci_frameworks,
                         tdd=tdd_knowledge, code_review=code_review, languages=programming_proficiencies,
                         frameworks=framework_proficiencies, experience=experience, dbms=dbms_experience,
                         data_analytics=data_analytics_experience)
