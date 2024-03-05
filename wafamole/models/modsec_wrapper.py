"""
    Wrapper model for (py)ModSecurity
"""
from ModSecurity import ModSecurity
from ModSecurity import RulesSet
from ModSecurity import Transaction
from ModSecurity import LogProperty

from wafamole.models import Model

import os
from pathlib import Path
import re
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


class PyModSecurityWrapper(Model):

    def __init__(self, rules_path, pl):
        assert os.path.isdir(rules_path)
        assert isinstance(pl, int) and 1 <= pl <= 4

        self.rules_path = Path(rules_path)
        self.modsec = ModSecurity()
        self.paranoia_level = pl

        # Ensure the right PL level is set in the CRS config file.
        # Here we assume that the PL is explicitely set using the 900000 rule.
        with open(self.rules_path / 'crs-setup.conf', 'r+') as crs_config_file:
            file_content = crs_config_file.read()
            file_content = re.sub(r"setvar:tx.blocking_paranoia_level=\d", "setvar:tx.blocking_paranoia_level={}".format(pl), file_content)
            crs_config_file.seek(0)
            crs_config_file.write(file_content)
            crs_config_file.truncate()

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

    def _get_paranoia_level(self, rule):
        return next((int(tag.split('/')[1]) for tag in rule.m_tags if 'paranoia-level' in tag), 1)

    # TODO add request body evaluation if needed
    # Currently only supports GET evaluation
    # See https://github.com/AvalZ/modsecurity-cli for more details
    def classify(self, value):

        method = "GET"
        base_uri = "http://www.modsecurity.org/test"
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

        total_score = sum([ rule.m_severity for rule in transaction.m_rulesMessages if self._get_paranoia_level(rule) <= self.paranoia_level])
        return total_score
