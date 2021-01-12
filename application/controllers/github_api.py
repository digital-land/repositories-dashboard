import requests
import threading, queue
import time
from dateutil import parser
import pprint

github_controller = None


def init(api_key):
    global github_controller
    github_controller = GithubController(api_key)


class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next


class GithubController:
    def __init__(self, api_key):
        self.session = requests.session()
        self.session.headers.update({"Authorization": "token {}".format(api_key)})
        self.repos = self.get_all_repos()

    def get_all_repos(self):
        all_repos = []
        page = 1
        number_results = 100
        while True:
            repos = self.session.get("https://api.github.com/orgs/digital-land/repos",
                                params={"per_page": number_results, "page": page}).json()
            all_repos.extend(repos)
            page = page + 1
            if len(repos) < number_results:
                break
        return all_repos

    def get_builds_for_repos(self, repos):
        q = queue.Queue()
        url_list = Node("workflows", Node("runs", Node("jobs")))
        key_list = Node("workflows", Node("workflow_runs", Node("jobs")))
        response = {}

        for x in range(30):
            threading.Thread(target=self.task_runner, args=(q, response), daemon=False).start()

        for repo in repos:
            response[repo] = {}
            key = key_list
            while key is not None:
                response[repo][key.val] = []
                key = key.next
            q.put(self.Task("https://api.github.com/repos/digital-land/{}/actions".format(repo), repo, key_list, url_list))

        q.join()

        result = []
        for repo_name in response.keys():

            builds = []
            for run in response[repo_name]["workflow_runs"]:
                build = {
                    "name": run["name"],
                    "run_id": run["id"],
                    "event": run["event"],
                    "status": run["status"],
                    "conclusion": run["conclusion"],
                    "commit_id": run["head_sha"],
                    "commit_message": run["head_commit"]["message"],
                    "commit_author": run["head_commit"]["author"]["name"],
                    "branch": run["head_branch"],
                    "html_url": run["html_url"],
                    "created_at": run["created_at"],
                    "updated_at": run["updated_at"],
                    "time_elapsed": str(parser.isoparse(run["updated_at"]) - parser.isoparse(run["created_at"])),
                    "jobs": [job for job in response[repo_name]["jobs"] if job["run_id"] == run["id"]]
                }
                for job in build["jobs"]:
                    for step in job["steps"]:
                        if step["conclusion"] == "failure":
                            build["failed_step"] = step["name"]

                builds.append(build)

            if len(builds) > 0:
                builds.sort(reverse=True, key=lambda x: parser.isoparse(x["updated_at"]))
                result.append({"repository_name": repo_name, "builds": builds})
        result.sort(reverse=True, key=lambda x: parser.isoparse(x["builds"][0]["updated_at"]))
        return result

    def task_runner(self, q, result):
        while True:
            task = q.get()
            response = self.session.get(task.url + "/" + task.url_node.val, params={"per_page": 5, "page": 1}).json()
            if task.key_node.next is not None:
                for item in response[task.key_node.val]:
                    q.put(self.Task(item["url"], task.repo, task.key_node.next, task.url_node.next))

            with threading.Lock():
                for item in response[task.key_node.val]:
                    result[task.repo][task.key_node.val].append(item)
            q.task_done()

    class Task:
        def __init__(self, url, repo, key_node, url_node):
            self.url = url
            self.repo = repo
            self.key_node = key_node
            self.url_node = url_node

