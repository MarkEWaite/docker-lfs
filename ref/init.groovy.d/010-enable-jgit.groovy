/* Git client plugin does not yet support configuration as code to enable
   JGit or JGit Apache.  Since configuration as code executes prior to the
   init groovy scripts, this script will enable JGit and JGit Apache. */

/* Work in progress - INCOMPLETE */

import jenkins.model.Jenkins
import hudson.plugins.git.GitTool

println 'Git extensions before additions'
def gitExtensions = Jenkins.instance.getExtensionList(hudson.plugins.git.GitTool.DescriptorImpl.class)
for (gitExtension in gitExtensions) {
  println "Git extension '${gitExtension.displayName}'"
}
println 'End of git extensions before additions'
println ''

List properties = new ArrayList<>()
def tool = new GitTool("my-name-for-jgit", "jgit", properties)
println "GitTool constructed '${tool}'"
println ''

println 'Git extensions after GitTool constructed'
def gitExtensionsAfter = Jenkins.instance.getExtensionList(hudson.plugins.git.GitTool.DescriptorImpl.class)
for (gitExtension in gitExtensionsAfter) {
  println "Git extension '${gitExtension.displayName}'"
}
println 'End of git extensions after GitTool constructed'
println ''
