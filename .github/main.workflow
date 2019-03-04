workflow "tox" {
  on = "push"
  resolves = ["Python 3.7"]
}

action "Python 3.7" {
  uses = "home-assistant/actions/py37-tox@master"
}
