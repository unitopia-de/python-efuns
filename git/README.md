# Python Efuns for interaction with git

These efuns provide an interface to git.
* `void git_cat(string path, string commitid, string fname, string destfile))`
* `void git_commit(string repo, string* files, string msg[, string wiz])`
* `mixed* git_info_commit(string path, string commitid)`
* `mixed* git_list_commits(string* paths[, int addfiles])`
* `void git_reverse(string path, string commitid[, string fname])`
* `void git_search_commits(closure callback, string* paths, string search[, int regexp[, int addfiles]])`
* `string git_show_diff(string path, string commitid, string fname)`
* `mixed** git_status(string* paths)`
* `string git_status_diff(string repo, string path)`

They are used by the UNItopia Zauberstab commands.
