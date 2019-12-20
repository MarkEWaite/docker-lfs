// Enter "Preparing to shutdown" state
if (System.getenv("START_QUIET").equalsIgnoreCase('true')) {
  jenkins.model.Jenkins.instance.doQuietDown()
}
