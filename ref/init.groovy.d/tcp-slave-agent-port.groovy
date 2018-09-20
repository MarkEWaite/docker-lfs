import hudson.model.*;
import jenkins.model.*;


Thread.start {
      // See https://wiki.jenkins-ci.org/display/JENKINS/Configuring+Content+Security+Policy
      // println "--> Setting content security policy for javadoc plugin"
      // System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "default-src 'none'; img-src 'self'; style-src 'self'; child-src 'self'; frame-src 'self';")

      sleep 10000
      def env = System.getenv()
      def portValue = env['JENKINS_SLAVE_AGENT_PORT']
      if (portValue) {
          int port = portValue.toInteger()
          Jenkins.instance.setSlaveAgentPort(port)
          println "--> setting agent port for jnlp... done"
      } else {
          println "--> NOT setting agent port for jnlp..."
      }
}
