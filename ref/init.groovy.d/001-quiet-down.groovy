// Enter "Preparing to shutdown" state
if (System.getenv("START_QUIET") == "True") {
  jenkins.model.Jenkins.instance.doQuietDown()
}
