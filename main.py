import pygit2
import sys
import pathlib
from datetime import datetime

def main():
    repo_dir = sys.argv[1]
    repo = pygit2.Repository(repo_dir)
    current_tree = repo.revparse_single("HEAD").tree
    diff = current_tree.diff_to_tree()
    for patch in diff:
        file_path = patch.delta.old_file.path
        blame = repo.blame(file_path)
        lino = 0
        with open(pathlib.Path(repo_dir) / file_path, "r") as f:
            for line in f:
                lino = lino + 1
                if "todo" in line.lower():
                    final_commit_time = datetime.fromtimestamp(blame.for_line(lino).final_committer.time)
                    now = datetime.now()
                    delta = now - final_commit_time
                    print(f"{str(delta)} has passed, you still have a TODO at {file_path}:{lino}.")

if __name__=='__main__':
    main()
