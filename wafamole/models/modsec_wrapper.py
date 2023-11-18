"""
    Wrapper model for (py)ModSecurity
"""
from ModSecurity import ModSecurity
from ModSecurity import RulesSet
from ModSecurity import Transaction
from ModSecurity import LogProperty

from wafamole.models import Model

from functools import partial

import re
from pathlib import Path
from urllib.parse import urlparse, urlencode
from enum import Enum

class Severity(Enum):
  def __new__(cls, *args, **kwds):
    value = len(cls.__members__)
    obj = object.__new__(cls)
    obj._value_ = value
    return obj
  def __init__(self, severity_id, score):
    self.id = severity_id
    self.score = score
 
  EMERGENCY = 0, 0 # not used in CRS
  ALERT     = 1, 0 # not used in CRS
  CRITICAL  = 2, 5
  ERROR     = 3, 4
  WARNING   = 4, 3
  NOTICE    = 5, 2
  INFO      = 6, 0 # not used in CRS
  DEBUG     = 7, 0 # not used in CRS

def get_paranoia_level(rule):
    return next((int(tag.split('/')[1]) for tag in rule.m_tags if 'paranoia-level' in tag), 1)

def at_least_paranoia_level(rule, paranoia_level=1):
    if not any(paranoia_tag in rule.tags for paranoia_tag in PARANOIA_TAGS):
        rule_paranoia = 1

    for tag in rule.tags:
        if 'paranoia-level' in tag:
            rule_paranoia = int(tag.split("/")[1])

    # filter out rules that have a higher paranoia level than expected
    return rule_paranoia > paranoia_level



def overall_score(matched_rules):

    pl2 = partial(at_least_paranoia_level, paranoia_level=2)

    matched_rules = list(filter(pl2, matched_rules))

    return sum(rule.severity for rule in matched_rules)


class PyModSecurityWrapper(Model):

    def __init__(self, rules_path):
        self.rules_path = Path(rules_path)
        self.modsec = ModSecurity()
        self.paranoia_level = 4

        self.rules = RulesSet()

        configs = ['modsecurity.conf', 'crs-setup.conf']
        for rule in configs:
            if (self.rules_path / rule).exists():
                self.rules.loadFromUri(str(self.rules_path / rule))
            else:
                raise FileNotFoundError(f"{rule} not found in Rules path")


        for rule in sorted((self.rules_path / "rules").glob("*.conf")):
            self.rules.loadFromUri(str(self.rules_path / "rules" / rule))

        self.modsec.setServerLogCb2(lambda x, y: None, LogProperty.RuleMessageLogProperty)


    def extract_features(self, value):
        return value

    # TODO add request body evaluation if needed
    # Currently only supports GET evaluation
    # See https://github.com/AvalZ/modsecurity-cli for more details
    def classify(self, value):

        method = "GET"
        base_uri = "http://www.modsecurity.org/test",
        encoded_query = urlencode({'q': value})
        full_url = f"{base_uri}?{encoded_query}"
        parsed_url = urlparse(full_url)

        transaction = Transaction(self.modsec, self.rules)

        transaction.processURI(full_url, method, "2.0")
        
        # Headers
        headers = {
            "Host": parsed_url.netloc, # Avoid matching rule 920280
            "Accept": "text/html", # Avoid matching rule 920280
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0" # Avoid matching rule 920280
        }
        for name, value in headers.items():
            transaction.addRequestHeader(name, value)
        transaction.processRequestHeaders()

        transaction.processRequestBody()

        # Decorate RuleMessages
        for rule in transaction.m_rulesMessages:
            rule.m_severity = Severity(rule.m_severity).score

        total_score = sum([ rule.m_severity for rule in transaction.m_rulesMessages if get_paranoia_level(rule) <= self.paranoia_level])
        return total_score
