// Checkout git client plugin
job('dsl-git-client-plugin') {
    scm {
        git {
            remote {
                url('https://github.com/MarkEWaite/git-client-plugin.git')
            }
            branch('master')
            extensions {
                localBranch()
            }
        }
    }
}
