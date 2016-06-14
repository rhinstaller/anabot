#!/bin/env python2

class TimeoutError(Exception):
    def __init__(self, message=None, data=None, *args):
        super(TimeoutError, self).__init__()
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
        if self.data is not None:
            if type(self.data) == dict:
                data = filter_dict(self.data)
                for k, v in data.iteritems():
                    if k == 'predicates':
                        data[k] = [predicate.debugName for predicate in v]
                    elif k == 'predicate':
                        data[k] = v.debugName
                    else:
                        data[k] = str(v)
                message.append(data)
                if len(self.args) > 0:
                    message.append(self.args)
            else:
                if len(self.args) == 0:
                    message.append(str(self.data))
                else:
                    message.append(tuple([self.data] + list(self.args)))

        if len(message) == 0:
            return ""
        elif len(message) == 1:
            return message[0]
        else:
            return str(tuple(message))

    def __repr__(self):
        return (self.__class__.__name__ + ": "
                + str(tuple([self.message, self.data, self.args])))

