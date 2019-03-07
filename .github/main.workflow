workflow "tox" {
  on = "push"
  resolves = [
    "Python 3.7",
    "Json Files",
  ]
}

action "Python 3.7" {
  uses = "home-assistant/actions/py37-tox@master"
}

action "Json Files" {
  uses = "home-assistant/actions/jq@master"
  args = "**/*.json"
}
