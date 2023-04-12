from __future__ import annotations
import ldmud, sys

class deklin_message:
    """
    Wrapper around /lwo/deklin_message that adds an addition operator.
    """
    def __init__(self, text: (str, ldmud.Mapping, ldmud.LWObject,)):
        if isinstance(text, ldmud.LWObject):
            self.lwo = text
        else:
            self.lwo = ldmud.efuns.new_lwobject("/lwo/deklin_message", text)

    def __repr__(self):
        if self.lwo:
            return repr(self.lwo.functions.query_text_other())
        else:
            return "empty";

    def __iadd__(self, other: (str, ldmud.Mapping, deklin_message,)) -> deklin_message:
        if not isinstance(other, deklin_message):
            other = deklin_message(other)
        ldmud.efuns.call_strict(self.lwo,"add",other.lwo)
        return self

    def __add__(self, other: (str, ldmud.Mapping, deklin_message,)) -> deklin_message:
        result = deklin_message(ldmud.efuns.deep_copy(self.lwo))
        result += other
        return result

    def __radd__(self, other: (str, ldmud.Mapping, deklin_message,)) -> deklin_message:
        result = deklin_message(other)
        result += self
        return result

    def __efun_call_strict__(self, fun: str, *args):
        return ldmud.efuns.call_strict(self.lwo, fun, *args)

    def __efun_call_other__(self, fun: str, *args):
        return ldmud.efuns.call_other(self.lwo, fun, *args)

    def __copy__(self):
        return deklin_message(ldmud.efuns.deep_copy(self.lwo))

    def __save__(self):
        return self.lwo

    @staticmethod
    def __restore__(val):
        if isinstance(val, ldmud.LWObject):
            return deklin_message(val)
        else:
            return NotImplemented

def create_deklin_message(text: (str, ldmud.Mapping,)) -> deklin_message:
    """
    SYNOPSIS
            deklin_message create_deklin_message(string|mapping msg)

    DESCRIPTION
            Creates a message, containing a specific text for certain recipients.
            Parameter can either be a string (a text for all recipients) or
            a mapping ([ recipient: text ]) containing specific texts.
            A recipient of 0 means everybody not explicitely mentioned.
    """
    return deklin_message(text)

def eval_annotations(ob):
    def eval_anno(val):
        nonlocal ns
        if isinstance(val, str):
            return eval(val, ns, {})

    def process_fun(fun):
        anno = getattr(fun, '__annotations__', None)
        if anno:
            evaluated = { name: eval_anno(value) for name, value in anno.items() }
            setattr(fun, '__annotations__', evaluated)

    if isinstance(ob, type):
        ns = sys.modules[ob.__module__].__dict__

        for funname in dir(ob):
            process_fun(getattr(ob, funname))
    else:
        nsob = ob
        while hasattr(nsob, '__wrapped__'):
            nsob = nsob.__wrapped__
        ns = getattr(nsob, '__globals__', {})

        process_fun(ob)

    return ob

eval_annotations(deklin_message)
eval_annotations(create_deklin_message)

def register():
    ldmud.register_type("deklin_message", eval_annotations(deklin_message))
    ldmud.register_efun("create_deklin_message", efun_create_deklin_message)
