import ldmud, os, subprocess, io, configparser
import ldmud_asyncio, asyncio

config = configparser.ConfigParser()
config['git'] = {}
config.read(os.path.expanduser('~/.ldmud-efuns'))
gitconfig = config['git']

GIT_DOMAIN = gitconfig.get('domain', 'unitopia.de')

def check_fname(path):
    if not len(path)  or "/.." in path or ' ' in path:
        raise ValueError("Illegal path given '%s'!" % (path,))

def check_path(path, master, euid, this, efun, readonly=True, allowmissing=False):
    """Check the given path and return the resulting path."""
    check_fname(path)

    if path[0] != "/":
        raise ValueError("Illegal path given '%s'!" % (path,))

    if readonly:
        target = master.functions.valid_read(path, euid, efun, this)
    else:
        target = master.functions.valid_write(path, euid, efun, this)
    if not target:
        raise ValueError("Illegal path given '%s'!" % (path,))

    if isinstance(target,int):
        target = path
    target = "." + target

    if not allowmissing and not os.path.exists(target):
        raise ValueError("Path '%s' does not exist." % (path,))

    return target

def check_commitid(commitid):
    if not all(c in "0123456789abcdef" for c in commitid):
        raise ValueError("Illegal commit id '%s'!" % (commitid,))

def get_repo(path, cache):
    if os.path.isdir(path):
        if path[-1] != '/':
            path += '/'

    (base,fname) = path.rsplit(sep='/', maxsplit=1)
    if base in cache:
        return (cache[base], path[len(cache[base])+1:],)

    toadd = []
    elements = base.split('/')
    for pos in range(len(elements), 0, -1):
        pdir = '/'.join(elements[:pos])
        if pdir in cache:
            repo = cache[pdir]
            return (repo, path[len(repo)+1:])

        toadd.append(pdir)

        if os.path.isdir(pdir + "/.git"):
            for found in toadd:
                cache[found] = pdir
            return (pdir, path[len(pdir)+1:])

    raise ValueError("No repository found.")

def call_git(cmd, repo, *, cmd2 = None, zeros = False, outfile = None):
    gotline = False

    proc = subprocess.Popen(cmd, cwd=repo, stdin=subprocess.DEVNULL, stdout=(cmd2 and subprocess.PIPE) or outfile or subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, encoding="UTF-8")

    if cmd2:
        proc2 = subprocess.Popen(cmd2, cwd=repo, stdin=proc.stdout, stdout=outfile or subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, encoding="UTF-8")
        proc.stdout.close()
        output = proc2.stdout
    else:
        output = proc.stdout

    if not outfile:
        remainder = ""
        for line in output:
            gotline = True
            if zeros:
                parts = line.split("\x00")
                for part in parts[:-1]:
                    yield remainder + part
                    remainder = ""
                remainder = parts[-1]
            else:
                yield line
        if zeros and len(remainder):
            yield remainder
        output.close()

    err = proc.stderr.read()
    proc.stderr.close()

    if cmd2:
        err2 = proc2.stderr.read()
        proc2.stderr.close()

    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    if proc.returncode:
        raise RuntimeError(err.rstrip("\n"))

    if cmd2:
        try:
            proc2.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc2.kill()
            proc2.wait()

        if proc2.returncode:
            raise RuntimeError(err2.rstrip("\n"))

async def async_call_git(cmd, repo, *, cmd2 = None, zeros = False, outfile = None):
    gotline = False

    proc = await asyncio.create_subprocess_exec(*cmd, cwd=repo, stdin=subprocess.DEVNULL, stdout=(cmd2 and subprocess.PIPE) or outfile or subprocess.PIPE, stderr=subprocess.PIPE)

    if cmd2:
        proc2 = await asyncio.create_subprocess_exec(*cmd2, cwd=repo, stdin=proc.stdout, stdout=outfile or subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc2.stdout
    else:
        output = proc.stdout

    if not outfile:
        remainder = ""
        async for line in output:
            line = line.decode("UTF-8")
            gotline = True
            if zeros:
                parts = line.split("\x00")
                for part in parts[:-1]:
                    yield remainder + part
                    remainder = ""
                remainder = parts[-1]
            else:
                yield line
        if zeros and len(remainder):
            yield remainder

    err = await proc.stderr.read()

    if cmd2:
        err2 = await proc2.stderr.read()

    try:
        await asyncio.wait_for(proc.wait(), timeout=1)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()

    if proc.returncode:
        raise RuntimeError(err.decode("UTF-8").rstrip("\n"))

    if cmd2:
        try:
            await asyncio.wait_for(proc2.wait(), timeout=1)
        except asyncio.TimeoutError:
            proc2.kill()
            await proc2.wait()

        if proc2.returncode:
            raise RuntimeError(err2.decode("UTF-8").rstrip("\n"))

def git_log_generate_command(paths, addfiles, opts):
    basedir = None
    cmd = ["git", "log", "--pretty=format:%H%n%at%n%an%n%s%n%b%x00"] + opts
    if addfiles:
        cmd.append("--numstat")
    cmd.append("--")
    checked = {}
    master = ldmud.get_master()
    this = ldmud.efuns.this_object()
    euid = ldmud.efuns.geteuid(this)

    # First check that all the directories are in the same repository.
    # And while we're at it, check for invalid characters.
    for path in paths:
        target = check_path(path, master, euid, this, "git_list_commits")
        (repo, fname) = get_repo(target, checked)

        if basedir is None:
            basedir = repo
        elif basedir != repo:
            raise ValueError("Paths are from different repositories.")

        cmd.append("./" + fname)

    return (cmd, basedir)

def git_log_process_line(result, data, addfiles, line):
    if not hasattr(data, 'commit'):
        data.commit = []
    if not hasattr(data, 'files'):
        data.files = None

    if line == "\x00\n" or line == "\x00":
        if len(data.commit) > 3:
            if addfiles:
                result.append(ldmud.Array((data.commit[0][:-1], int(data.commit[1][:-1]), data.commit[2][:-1], data.commit[3][:-1], "".join(data.commit[4:]),ldmud.Array(),)))
            else:
                result.append(ldmud.Array((data.commit[0][:-1], int(data.commit[1][:-1]), data.commit[2][:-1], data.commit[3][:-1], "".join(data.commit[4:]),)))
        data.commit = []
        if addfiles:
            data.files = []
    elif line == "\n":
        if len(result) > 0 and data.files:
            result[-1][5] = ldmud.Array(data.files)
            data.files = None
    elif data.files is not None:
        parts = line[:-1].split("\t")
        if len(parts) == 3:
            if parts[0] == '-':
                data.files.append(ldmud.Array((parts[2], 0, 0,)))
            else:
                data.files.append(ldmud.Array((parts[2], int(parts[0]), int(parts[1]),)))
    else:
        data.commit.append(line)

def git_log_postprocess(result, data):
    if len(result) > 0 and getattr(data, 'files', None):
        result[-1][5] = ldmud.Array(data.files)

def efun_git_list_commits(paths: ldmud.Array, addfiles: int = 0) -> ldmud.Array:
    """
    SYNOPSIS
            mixed* git_list_commits(string* paths[, int addfiles])

    DESCRIPTION
            For the given directories or files lists all commits. The first
            entry of the result is the path of the repository, the following
            entries are the commits given as arrays with the following entries:
                [0]  Commit-UUID        (string)
                [1]  Timestamp          (int)
                [2]  Author             (string)
                [3]  Short Description  (string)
                [4]  Long Description   (string)
                [5]  Array of files, similar to git_info_commit().
                     (This is only added if <addfiles> != 0)

    SEE ALSO
            git_info_commit(E)
    """

    if not len(paths):
        raise ValueError("No path given.")

    (cmd, basedir) = git_log_generate_command(paths, addfiles, [])

    result = [ "/" + basedir[2:] ]
    data = type('git_log_data', (), {})()

    for line in call_git(cmd, basedir):
        git_log_process_line(result, data, addfiles, line)

    git_log_postprocess(result, data)

    return ldmud.Array(result)

def efun_git_info_commit(path: str, commitid: str) -> ldmud.Array:
    """
    SYNOPSIS
            mixed* git_info_commit(string path, string commitid)

    DESCRIPTION
            For the given commit id in the given repository return an array
            with the following information:
                [0]  Commit-UUID        (string)
                [1]  Timestamp          (int)
                [2]  Author             (string)
                [3]  Short Description  (string)
                [4]  Long Description   (string)
                [5]  Array of files, each file has the following information:
                       [0]  Path of the file, relative to the repository
                       [1]  Added lines
                       [2]  Removed lines

    SEE ALSO
            git_list_commits(E)
    """

    check_commitid(commitid)

    master = ldmud.get_master()
    this = ldmud.efuns.this_object()
    euid = ldmud.efuns.geteuid(this)
    target = check_path(path, master, euid, this, "git_info_commit")

    result = []
    commit = []
    for line in call_git(["git", "show", "--pretty=format:%H%n%at%n%an%n%s%n%b%x00", "--numstat", commitid], target):
        if line == "\x00\n":
            if len(commit) > 3:
                result.extend((commit[0][:-1], int(commit[1][:-1]), commit[2][:-1], commit[3][:-1], "".join(commit[4:]),))
                commit = None
        elif commit is None:
            parts = line[:-1].split("\t")
            if len(parts) == 3:
                if parts[0] == '-':
                    result.append(ldmud.Array((parts[2], 0, 0,)))
                else:
                    result.append(ldmud.Array((parts[2], int(parts[0]), int(parts[1]),)))
        else:
            commit.append(line)

    return ldmud.Array(result)

def efun_git_show_diff(path: str, commitid: str, fname: str) -> str:
    """
    SYNOPSIS
            string git_show_diff(string path, string commitid, string fname)

    DESCRIPTION
            For the given commit id and file return a diff.

    SEE ALSO
            git_list_commits(E), git_info_commit(E), git_cat(E)
    """

    check_commitid(commitid)
    check_fname(fname)

    master = ldmud.get_master()
    this = ldmud.efuns.this_object()
    euid = ldmud.efuns.geteuid(this)
    target = check_path(path, master, euid, this, "git_show_diff")

    result = io.StringIO()
    for line in call_git(["git", "show", "--pretty=format:", commitid, "--", fname], target):
        result.write(line)

    return result.getvalue()

def efun_git_status(paths: ldmud.Array) -> ldmud.Array:
    """
    SYNOPSIS
            mixed** git_status(string* paths)

    DESCRIPTION
            For the given directories or files list any changes that are not
            committed. Returns an array for each such file:
                [0]  Repository                         (string)
                [1]  File Name (relative to repository) (string)
                [2]  Status flags                       (string)

            The status flags are the same as in the sort format of 'git status'.

    SEE ALSO
            git_list_commits(E), git_info_commit(E)
    """

    if not len(paths):
        raise ValueError("No path given.")

    repos = {}
    checked = {}
    master = ldmud.get_master()
    this = ldmud.efuns.this_object()
    euid = ldmud.efuns.geteuid(this)

    for path in paths:
        target = check_path(path, master, euid, this, "git_status", allowmissing=True)
        (repo, fname) = get_repo(target, checked)

        repos.setdefault(repo, [])
        repos[repo].append(fname)

    result = []
    skip_next = False
    for repo, files in repos.items():
        for line in call_git(["git", "status", "--porcelain=1", "-z", "--untracked-files=all", "--" ] + [ "./" + fname for fname in files ], repo, zeros=True):
            if skip_next:
                skip_next = False
                continue

            if line[0] == 'R':
                skip_next = True

            result.append(ldmud.Array((repo[1:], line[3:], line[0:2],)))

    return ldmud.Array(result)

def efun_git_status_diff(repo: str, fname: str) -> str:
    """
    SYNOPSIS
            string git_status_diff(string repo, string path)

    DESCRIPTION
            Return the current uncommited changes for the given file
            in the given repository as a unified diff.

    SEE ALSO
            git_status(E)
    """

    master = ldmud.get_master()
    this = ldmud.efuns.this_object()
    euid = ldmud.efuns.geteuid(this)
    target = check_path(repo, master, euid, this, "git_status_diff")
    check_fname(fname)

    result = io.StringIO()
    for line in call_git(["git", "diff", "HEAD", "--", fname], target):
        result.write(line)

    return result.getvalue()

def efun_git_commit(repo: str, files: ldmud.Array, msg: str, wiz: str = None) -> None:
    """
    SYNOPSIS
            void git_commit(string repo, string* files, string msg[, string wiz])

    DESCRIPTION
            Commit the given files in the given repository with the
            given message. If an author is given with <wiz> then the privilege
            is checked with the master.

    SEE ALSO
            git_status(E), git_status_diff(E)
    """

    master = ldmud.get_master()
    this = ldmud.efuns.this_object()
    euid = ldmud.efuns.geteuid(this)

    if not wiz:
        wiz = euid
    elif not master.functions.privilege_violation("git_commit", this, repo, wiz, 0):
        raise PermissionError("Insufficient privileges!")

    target = check_path(repo, master, euid, this, "git_commit")

    if repo[-1] != "/":
        repo += "/"

    for fname in files:
        check_path(repo + fname, master, euid, this, "git_commit", readonly=False, allowmissing=True)

    for line in call_git(["git", "add", "--"] + list(files), target):
        pass

    for line in call_git(["git", "-c", "user.name="+wiz.capitalize(), "-c", "user.email="+wiz+"@"+GIT_DOMAIN, "commit", "-q", "--author="+wiz.capitalize()+" <"+wiz+"@"+GIT_DOMAIN+">", "-m", msg, "--" ] + list(files), target):
        pass

def efun_git_reverse(repo: str, commitid: str, fname: str = None) -> None:
    """
    SYNOPSIS
            void git_reverse(string path, string commitid[, string fname])

    DESCRIPTION
            Undo the given commit in the working directory. The commit is applied
            reversely to the working directory, but not committed. If a filename
            is given, only this file is affected.

            If the reverse patch does not apply cleanly an error is thrown.

    SEE ALSO
            git_commit(E), git_info_commit(E), git_show_diff(E)
    """

    check_commitid(commitid)

    master = ldmud.get_master()
    this = ldmud.efuns.this_object()
    euid = ldmud.efuns.geteuid(this)
    target = check_path(repo, master, euid, this, "git_reverse")

    if repo[-1] != "/":
        repo += "/"

    if fname:
        files = [fname]
    else:
        files = []
        for line in call_git(["git", "show", "--pretty=format:", "--numstat", commitid], target):
            parts = line[:-1].split("\t")
            if len(parts) == 3:
                files.append(parts[2].split(" => ")[0])

    for fname in files:
        check_path(repo + fname, master, euid, this, "git_reverse", readonly=False, allowmissing=True)

    for line in call_git(["git", "show", "--pretty=format:", commitid, "--"] + files, target,
                  cmd2 = ["git", "apply", "--reverse"]):
        print(line)

def efun_git_cat(repo: str, commitid: str, fname: str, destfile: str) -> None:
    """
    SYNOPSIS
            void git_cat(string path, string commitid, string fname, string destfile)

    DESCRIPTION
            Write the contents of the file <fname> of the given commit to the
            file <destfile>. If the file already exists, it will be overwritten.

    SEE ALSO
            git_show_diff(E), git_list_commits(E), git_info_commit(E)
    """

    check_commitid(commitid)

    master = ldmud.get_master()
    this = ldmud.efuns.this_object()
    euid = ldmud.efuns.geteuid(this)
    target = check_path(repo, master, euid, this, "git_cat")

    dest = check_path(destfile, master, euid, this, "git_cat", readonly=False, allowmissing=True)
    if fname[0] == '/':
        fname = fname[1:]

    tmpname = dest + ".git_cat_tmp"
    try:
        with open(tmpname, "wt") as f:
            for line in call_git(["git", "show", commitid + ":" + fname], target, outfile = f):
                pass
        os.rename(tmpname, dest)
    except:
        os.remove(tmpname)
        raise

def efun_git_search_commits(callback: ldmud.Closure, paths: ldmud.Array, search: str, regexp: int = 0, addfiles: int = 0) -> None:
    """
    SYNOPSIS
            void git_search_commits(closure callback, string* paths, string search[, int regexp[, int addfiles]])

    DESCRIPTION
            Searches in the given directories for commits change the number
            of occurrences of the string <search>. If <regexp> != 0 then
            treat <search> as a regular expression.

            The first entry of the result is the path of the repository,
            the following entries are the commits given as arrays with the
            following entries:
                [0]  Commit-UUID        (string)
                [1]  Timestamp          (int)
                [2]  Author             (string)
                [3]  Short Description  (string)
                [4]  Long Description   (string)
                [5]  Array of files, similar to git_info_commit().
                     (This is only added if <addfiles> != 0)

            This efun works asynchronous and calls <callback> with the
            result. If an error occurs, the callback is called with
            the error string.

    SEE ALSO
            git_list_commits(E)
    """

    if not len(paths):
        raise ValueError("No path given.")

    asyncio.run(do_git_search_commits(callback, paths, search, regexp, addfiles))

async def do_git_search_commits(callback, paths, search, regexp, addfiles):
    try:
        opts = ["-S" + search]
        if regexp:
            opts.append("--pickaxe-regex")

        (cmd, basedir) = git_log_generate_command(paths, addfiles, opts)

        result = [ "/" + basedir[2:] ]
        data = type('git_log_data', (), {})()

        async for line in async_call_git(cmd, basedir):
            git_log_process_line(result, data, addfiles, line)

        git_log_postprocess(result, data)
    except Exception as ex:
        callback(str(ex))
        return

    callback(ldmud.Array(result))
