#!/bin/env python2

class NonexistentError(Exception):
    def __init__(self, message=None, data=None, *args):
        super(NonexistentError, self).__init__()
        self.message = message
        self.data = data
        self.args = args

    def __str__(self):
        def filter_dict(dict_in):
            return {k:v for k, v in dict_in.iteritems()
                    if not (k.startswith('__') and k.endswith('__'))}

        message = []
        if self.message is not None:
            message.append(self.message)
        message += list(self.args)
        if self.data is not None and not isinstance(self.data, dict):
            message.append(self.data)
        if isinstance(self.data, dict):
            data = filter_dict(self.data)
            for k, v in data.iteritems():
                if k == 'predicates':
                    data[k] = [predicate.debugName for predicate in v]
                elif k == 'predicate':
                    data[k] = v.debugName
                else:
                    data[k] = str(v)
            message.append(data)

        if len(message) == 0:
            return ""
        elif len(message) == 1:
            return str(message[0])
        else:
            return str(tuple(message))

    def __repr__(self):
        return (self.__class__.__name__ + ": "
                + str(tuple([self.message, self.data, self.args])))

class TimeoutError(NonexistentError):
    pass
