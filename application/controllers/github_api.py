import requests
import queue
import concurrent.futures
import logging
from dateutil import parser


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

        for repo in repos:
            response[repo] = {}
            key = key_list
            while key is not None:
                response[repo][key.val] = []
                key = key.next

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            future_to_task = {}
            for repo in repos:
                task = self.Task("https://api.github.com/repos/digital-land/{}/actions".format(repo), repo, key_list, url_list)
                future_to_task[executor.submit(self.task_runner, task, q)] = task

            while future_to_task:
                done, not_done = concurrent.futures.wait(
                    future_to_task, timeout=2,
                    return_when=concurrent.futures.FIRST_COMPLETED)
                while not q.empty():
                    # fetch a task from the queue
                    task = q.get()

                    # Start the load operation and mark the future with its task
                    future_to_task[executor.submit(self.task_runner, task, q)] = task

                for future in done:
                    task = future_to_task[future]
                    try:
                        output = future.result()
                    except Exception as exc:
                        logging.warning("GET %r generated an exception: %s" % (task.url, exc), exc_info=True)
                    else:
                        for item in output:
                            response[task.repo][task.key_node.val].append(item)

                    # remove the now completed future
                    del future_to_task[future]

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
                            logging.info(
                                f"Registering failure on run {run['id']} of {repo_name} at {run['updated_at']}"
                                f" during step - {step['name']}"
                            )
                            build["failed_step"] = step["name"]

                builds.append(build)

            if len(builds) > 0:
                builds.sort(reverse=True, key=lambda x: parser.isoparse(x["updated_at"]))
                result.append({"repository_name": repo_name,
                               "is_active": self.is_repo_active(response[repo_name]),
                               "builds": builds})
        result.sort(reverse=True, key=lambda x: parser.isoparse(x["builds"][0]["updated_at"]))
        return result

    def is_repo_active(self, repo):
        # Add any criteria here to check if repo is active
        return repo["workflows"][0]["state"] == "active"

    def task_runner(self, task, q):
        response = self.session.get(task.url + "/" + task.url_node.val, params={"per_page": 5, "page": 1}).json()
        if task.key_node.next is not None:
            for item in response[task.key_node.val]:
                q.put(self.Task(item["url"], task.repo, task.key_node.next, task.url_node.next))

        return response[task.key_node.val]

    class Task:
        def __init__(self, url, repo, key_node, url_node):
            self.url = url
            self.repo = repo
            self.key_node = key_node
            self.url_node = url_node

