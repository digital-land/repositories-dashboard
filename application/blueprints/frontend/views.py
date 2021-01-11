from application.controllers.github_api import GithubController
from flask import (
    current_app,
    Blueprint,
    render_template,
)

frontend = Blueprint("frontend", __name__, template_folder="templates")

@frontend.route("/")
def builds():
    controller = GithubController(api_key=current_app.config["GITHUB_API_KEY"])
    active_repos = [repo["name"] for repo in controller.repos if repo["archived"] == False]
    repos = controller.get_builds_for_repos(active_repos)
    return render_template("builds.html", repos=repos)
