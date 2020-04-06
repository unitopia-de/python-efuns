import ldmud

class BadArgument(TypeError):
    def __init__(self, fun, number, got, expected):
        TypeError.__init__(self, "Bad arg %d to %s: got '%s', expected '%s'." % (number, fun, got.__name__, "/".join([exp.__name__ for exp in expected]),))

def check_arg(fun, nr, arg, *types):
    for typ in types:
        if isinstance(arg, typ):
            return

    raise BadArgument(fun, nr, type(arg), types)

translittable = {
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "Ä": "AE",
    "Ö": "OE",
    "Ü": "UE",
    "ß": "ss",
    "ẞ": "SS",
}

def efun_add_action(fun: (str, ldmud.Closure,), cmd: str, flag: int = 0) -> None:
    check_arg("add_action()", 1, fun, str, ldmud.Closure)
    check_arg("add_action()", 2, cmd, str)
    check_arg("add_action()", 3, flag, int)

    if flag < 0:
        cmd = cmd[:-flag] + "\0" + cmd[-flag:]

    # Dieser Schritt soll in Zukunft entfallen.
    cmd = cmd.replace("ae", "ä").replace("oe", "ö").replace("ue", "ü").replace("ss", "ß")

    results = [ "" ]
    for ch in cmd:
        repl = translittable.get(ch)
        if repl:
            results = [ result + add for result in results for add in (ch, repl,) ]
        else:
            results = [ result + ch  for result in results ]

    if flag < 0:
        results.sort()
        prefixes = set()

        for result in results:
            pos = result.find("\0")
            result = result[:pos] + result[pos+1:]

            while pos <= len(result) and result[:pos] in prefixes:
                pos += 1

            if pos > len(result):
                continue

            ldmud.efuns.add_action(fun, result, -pos)

            while pos <= len(result):
                prefixes.add(result[:pos])
                pos += 1
    else:
        for result in results:
            ldmud.efuns.add_action(fun, result, flag)

def efun_query_verb_ascii(flag: int = 0) -> str:
    """
    SYNOPSIS
            string query_verb_ascii()
            string query_verb_ascii(int flag)

    DESCRIPTION
            Return the verb of the current command with umlauts replaced by
            their transliterations, or 0 if not executing from a command.

            If <flag> is 0 or not given, the verb as given by the user is returned
            (this is the first word from the line input by the player, up to but
            not including the first space or lineend). If <flag> is non-0, the verb
            as specified in the add_action() statement is returned.

    SEE ALSO
            query_verb(E), add_action(E), query_command(E)
    """

    result = ldmud.efuns.query_verb(flag)
    if result:
        for ch, rep in translittable.items():
            result = result.replace(ch, rep)
    return result
