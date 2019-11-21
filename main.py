import pygit2
import sys
import pathlib
import asyncio
from datetime import datetime

def pprint_todo(entry, now):
    path, line, blame = entry
    commiter = blame.final_committer.name
    final_time = datetime.fromtimestamp(blame.final_committer.time)
    print(f"{str(now - final_time)} has passed, {commiter} still has a todo at {path}:{line}")

async def find_todos(repo, file_path):
    line_no = 0
    result = []
    blame = repo.blame(file_path)
    with open(pathlib.Path(repo.path) / '..' / file_path, "r") as f:
        for line in f:
            line_no = line_no + 1
            if "todo" in line.lower():
                result.append((file_path, line_no, blame.for_line(line_no)))
    return result

async def main():
    repo_dir = sys.argv[1]
    repo = pygit2.Repository(repo_dir)
    current_tree = repo.revparse_single("HEAD").tree
    diff = current_tree.diff_to_tree()
    futs = set()
    now = datetime.now()
    for patch in diff:
        file_path = patch.delta.old_file.path
        futs.add(asyncio.ensure_future(find_todos(repo, file_path)))
    while True:
        done, tobedone = await asyncio.wait(futs, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            result = await task
            for r in result:
                pprint_todo(r, now)
        if len(tobedone) == 0:
            break
        else:
            futs = tobedone

if __name__=='__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
