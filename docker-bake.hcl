# ---- groups ----

group "linux" {
  targets = [
    "almalinux_jdk11",
    "alpine_jdk11",
    "alpine_jdk17",
    "alpine_jdk21",
    "centos7_jdk11",
    "debian_jdk11",
    "debian_jdk17",
    "debian_jdk21",
    "debian_slim_jdk11",
    "debian_slim_jdk17",
    "debian_slim_jdk21",
    "rhel_ubi8_jdk11",
    "rhel_ubi9_jdk17",
    "rhel_ubi9_jdk21",
  ]
}

group "linux-arm64" {
  targets = [
    "almalinux_jdk11",
    "debian_jdk11",
    "debian_jdk17",
    "debian_jdk21",
    "rhel_ubi8_jdk11",
    "rhel_ubi9_jdk17",
    "rhel_ubi9_jdk21",
  ]
}

group "linux-s390x" {
  targets = [
    "debian_jdk11",
  ]
}

group "linux-ppc64le" {
  targets = [
    "debian_jdk11",
    "debian_jdk17",
    "debian_jdk21",
    "rhel_ubi9_jdk17",
  ]
}

# ---- variables ----

variable "JENKINS_VERSION" {
  default = "2.419"
}

variable "JENKINS_SHA" {
  default = "895a90dd5929a38c8cc8c0342478d27a6e01470cd7e8da8c4ae51f26aa1bdf85"
}

variable "REGISTRY" {
  default = "docker.io"
}

variable "JENKINS_REPO" {
  default = "jenkins/jenkins"
}

variable "LATEST_WEEKLY" {
  default = "false"
}

variable "LATEST_LTS" {
  default = "false"
}

variable "PLUGIN_CLI_VERSION" {
  default = "2.12.13"
}

variable "COMMIT_SHA" {
  default = ""
}

variable "ALPINE_FULL_TAG" {
  default = "3.18.4"
}

variable "ALPINE_SHORT_TAG" {
  default = regex_replace(ALPINE_FULL_TAG, "\\.\\d+$", "")
}

variable "JAVA11_VERSION" {
  default = "11.0.20.1_1"
}

variable "JAVA17_VERSION" {
  default = "17.0.8.1_1"
}

# not passed through currently as inconsistent versions are published (2023-08-14)
# alpine not published on 34, but x64 on 35 isn't published for linux
variable "JAVA21_VERSION" {
  default = "21+35"
}

variable "BOOKWORM_TAG" {
  default = "20230919"
}

# ----  user-defined functions ----

# return a tag prefixed by the Jenkins version
function "_tag_jenkins_version" {
  params = [tag]
  result = notequal(tag, "") ? "${REGISTRY}/${JENKINS_REPO}:${JENKINS_VERSION}-${tag}" : "${REGISTRY}/${JENKINS_REPO}:${JENKINS_VERSION}"
}

# return a tag optionaly prefixed by the Jenkins version
function "tag" {
  params = [prepend_jenkins_version, tag]
  result = equal(prepend_jenkins_version, true) ? _tag_jenkins_version(tag) : "${REGISTRY}/${JENKINS_REPO}:${tag}"
}

# return a weekly optionaly prefixed by the Jenkins version
function "tag_weekly" {
  params = [prepend_jenkins_version, tag]
  result =  equal(LATEST_WEEKLY, "true") ? tag(prepend_jenkins_version, tag) : ""
}

# return a LTS optionaly prefixed by the Jenkins version
function "tag_lts" {
  params = [prepend_jenkins_version, tag]
  result =  equal(LATEST_LTS, "true") ? tag(prepend_jenkins_version, tag) : ""
}

# ---- targets ----

target "almalinux_jdk11" {
  dockerfile = "11/almalinux/almalinux8/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    JAVA_VERSION = JAVA11_VERSION
  }
  tags = [
    tag(true, "almalinux"),
    tag_weekly(false, "almalinux"),
    tag_lts(false, "lts-almalinux")
  ]
  platforms = ["linux/amd64", "linux/arm64"]
}

target "alpine_jdk11" {
  dockerfile = "11/alpine/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    ALPINE_TAG = ALPINE_FULL_TAG
    JAVA_VERSION = JAVA11_VERSION
  }
  tags = [
    tag(true, "alpine-jdk11"),
    tag_weekly(false, "alpine-jdk11"),
    tag_weekly(false, "alpine${ALPINE_SHORT_TAG}-jdk11"),
    tag_lts(false, "lts-alpine-jdk11")
  ]
  platforms = ["linux/amd64"]
}

target "alpine_jdk17" {
  dockerfile = "17/alpine/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    ALPINE_TAG = ALPINE_FULL_TAG
    JAVA_VERSION = JAVA17_VERSION
  }
  tags = [
    tag(true, "alpine"),
    tag_weekly(false, "alpine"),
    tag_weekly(false, "alpine-jdk17"),
    tag_weekly(false, "alpine${ALPINE_SHORT_TAG}-jdk17"),
    tag_lts(false, "lts-alpine"),
    tag_lts(false, "lts-alpine-jdk17"),
    tag_lts(true, "lts-alpine")
  ]
  platforms = ["linux/amd64"]
}

target "alpine_jdk21" {
  dockerfile = "21/alpine/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    ALPINE_TAG = ALPINE_FULL_TAG
    JAVA_VERSION = JAVA21_VERSION
  }
  tags = [
    tag(true, "alpine-jdk21-preview"),
    tag_weekly(false, "alpine-jdk21-preview"),
    tag_weekly(false, "alpine${ALPINE_SHORT_TAG}-jdk21-preview"),
    tag_lts(false, "lts-alpine-jdk21-preview")
  ]
  platforms = ["linux/amd64", "linux/arm64"]
}

target "centos7_jdk11" {
  dockerfile = "11/centos/centos7/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    JAVA_VERSION = JAVA11_VERSION
  }
  tags = [
    tag(true, "centos7"),
    tag_weekly(false, "centos7"),
    tag_weekly(false, "centos7-jdk11"),
    tag_lts(true, "lts-centos7"),
    tag_lts(false, "lts-centos7"),
    tag_lts(false, "lts-centos7-jdk11")
  ]
  platforms = ["linux/amd64"]
}

target "debian_jdk11" {
  dockerfile = "11/debian/bookworm/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    BOOKWORM_TAG = BOOKWORM_TAG
    JAVA_VERSION = JAVA11_VERSION
  }
  tags = [
    tag(true, "jdk11"),
    tag_weekly(false, "latest-jdk11"),
    tag_weekly(false, "jdk11"),
    tag_lts(false, "lts-jdk11"),
    tag_lts(true, "lts-jdk11")
  ]
  platforms = ["linux/amd64", "linux/arm64", "linux/s390x", "linux/ppc64le"]
}

target "debian_jdk17" {
  dockerfile = "17/debian/bookworm/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    BOOKWORM_TAG = BOOKWORM_TAG
    JAVA_VERSION = JAVA17_VERSION
  }
  tags = [
    tag(true, ""),
    tag(true, "jdk17"),
    tag_weekly(false, "latest"),
    tag_weekly(false, "latest-jdk17"),
    tag_weekly(false, "jdk17"),
    tag_lts(false, "lts"),
    tag_lts(false, "lts-jdk17"),
    tag_lts(true, "lts"),
    tag_lts(true, "lts-jdk17")
  ]
  platforms = ["linux/amd64", "linux/arm64", "linux/ppc64le"]
}

target "debian_jdk21" {
  dockerfile = "21/debian/bookworm/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    BOOKWORM_TAG = BOOKWORM_TAG
    JAVA_VERSION = JAVA21_VERSION
  }
  tags = [
    tag(true, "jdk21"),
    tag_weekly(false, "latest-jdk21-preview"),
    tag_weekly(false, "jdk21"),
    tag_lts(false, "lts-jdk21-preview"),
    tag_lts(true, "lts-jdk21-preview")
  ]
  platforms = ["linux/amd64", "linux/arm64", "linux/ppc64le", "linux/s390x", "linux/arm/v7"]
}

target "debian_slim_jdk11" {
  dockerfile = "11/debian/bookworm-slim/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    BOOKWORM_TAG = BOOKWORM_TAG
    JAVA_VERSION = JAVA11_VERSION
  }
  tags = [
    tag(true, "slim-jdk11"),
    tag_weekly(false, "slim-jdk11"),
    tag_lts(false, "lts-slim-jdk11"),
  ]
  platforms = ["linux/amd64"]
}

target "debian_slim_jdk17" {
  dockerfile = "17/debian/bookworm-slim/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    BOOKWORM_TAG = BOOKWORM_TAG
    JAVA_VERSION = JAVA17_VERSION
  }
  tags = [
    tag(true, "slim"),
    tag_weekly(false, "slim"),
    tag_weekly(false, "slim-jdk17"),
    tag_lts(false, "lts-slim"),
    tag_lts(false, "lts-slim-jdk17"),
    tag_lts(true, "lts-slim"),
  ]
  platforms = ["linux/amd64"]
}

target "debian_slim_jdk21" {
  dockerfile = "21/debian/bookworm-slim/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    BOOKWORM_TAG = BOOKWORM_TAG
    JAVA_VERSION = JAVA21_VERSION
  }
  tags = [
    tag(true, "slim-jdk21-preview"),
    tag_weekly(false, "slim-jdk21-preview"),
    tag_lts(false, "lts-slim-jdk21-preview"),
  ]
  platforms = ["linux/amd64", "linux/arm64", "linux/ppc64le", "linux/s390x", "linux/arm/v7"]
}

target "rhel_ubi8_jdk11" {
  dockerfile = "11/rhel/ubi8/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    JAVA_VERSION = JAVA11_VERSION
  }
  tags = [
    tag(true, "rhel-ubi8-jdk11"),
    tag_weekly(false, "rhel-ubi8-jdk11"),
    tag_lts(false, "lts-rhel-ubi8-jdk11"),
    tag_lts(true, "lts-rhel-ubi8-jdk11")
  ]
  platforms = ["linux/amd64", "linux/arm64"]
}

target "rhel_ubi9_jdk17" {
  dockerfile = "17/rhel/ubi9/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    JAVA_VERSION = JAVA17_VERSION
  }
  tags = [
    tag(true, "rhel-ubi9-jdk17"),
    tag_weekly(false, "rhel-ubi9-jdk17"),
    tag_lts(false, "lts-rhel-ubi9-jdk17"),
    tag_lts(true, "lts-rhel-ubi9-jdk17")
  ]
  platforms = ["linux/amd64", "linux/arm64", "linux/ppc64le"]
}

target "rhel_ubi9_jdk21" {
  dockerfile = "21/rhel/ubi9/hotspot/Dockerfile"
  context = "."
  args = {
    JENKINS_VERSION = JENKINS_VERSION
    JENKINS_SHA = JENKINS_SHA
    COMMIT_SHA = COMMIT_SHA
    PLUGIN_CLI_VERSION = PLUGIN_CLI_VERSION
    JAVA_VERSION = JAVA21_VERSION
  }
  tags = [
    tag(true, "rhel-ubi9-jdk21-preview"),
    tag_weekly(false, "rhel-ubi9-jdk21-preview"),
    tag_lts(false, "lts-rhel-ubi9-jdk21-preview"),
    tag_lts(true, "lts-rhel-ubi9-jdk21-preview")
  ]
  platforms = ["linux/amd64", "linux/arm64", "linux/ppc64le"]
}
