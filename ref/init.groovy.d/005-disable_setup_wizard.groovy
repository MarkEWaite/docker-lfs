import jenkins.install.InstallState
import jenkins.model.Jenkins

// Also requires command line argument at startup (see README)
Jenkins.getInstance().setInstallState(InstallState.INITIAL_SETUP_COMPLETED)
