import git
from ontobio.util.user_agent import get_user_agent

NAME="biolink-api"
VERSION=git.Repo(search_parent_directories=True).head.object.hexsha[:7]
USER_AGENT=get_user_agent(name=NAME, version=VERSION)