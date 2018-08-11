import re
from pymq.command.dispatcher.dispatcher import Dispatcher


class RegexDispatcher(Dispatcher):
    def string_matcher(self, matcher):
        return lambda cmd: re.fullmatch(matcher, cmd)
