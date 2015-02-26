__author__ = 'Blake'

class Action(object):
    def __init__(self):
        self.description = 'DefaultAction'

    def help(self):
        raise NotImplementedError

    def go(self):
        raise NotImplementedError

    def __str__(self):
        return self.description

    def __repr__(self):
        return self.__str__