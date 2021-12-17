package es.sanitas.jenkins.pipelines

import java.text.SimpleDateFormat
import groovy.json.JsonBuilder
import hudson.AbortException


// https://jenkins.io/doc/book/pipeline/shared-libraries/#writing-libraries
class GitOperations implements Serializable {

  def canonicalOrgs = [ "apps", "arquitectura", "desarrollo-bravocloud", "entrega-continua", "qa" ]

  def credentialsId
  def gitrepo
  def gitbranch
  def steps

  GitOperations( steps, gitrepo, gitbranch='master', credentialsId='d11bb379-9dd6-4e60-b93e-fd0f7807ead4' ) {
    this.steps = steps
    this.gitrepo = gitrepo
    this.gitbranch = gitbranch
    this.credentialsId = credentialsId
  }

  def clone() {
    steps.echo ":: Cloning repo $gitrepo/$gitbranch..."
    steps.checkout( [ $class: 'GitSCM',
                      branches: [ [ name: "*/$gitbranch" ] ],
                      extensions: [[$class: 'CloneOption', timeout: 60]],
                      userRemoteConfigs: [ [ credentialsId: this.credentialsId, url: this.gitrepo ] ]
                    ] )
  }

  def cloneHash(commitHash) {
    steps.echo ":: Cloning repo $gitrepo/$commitHash..."
    steps.checkout( [ $class: 'GitSCM',
                      branches: [ [ name: commitHash ]],
                      userRemoteConfigs: [ [ credentialsId: this.credentialsId, url: this.gitrepo ] ]
                    ] )
  }

  /**
   *  Devuelve último commit de un repo/objeto(branch,tag)
   *  Si el nombre del objeto se repite se devolveran n resultados
   */
  def findRemoteLastCommitGitLab( repo, branchOrTag ) {
    steps.echo ":: Finding last commit in $repo for $branchOrTag"
    def object = branchOrTag - "origin/"  //  se elimina origin/ -- GITLAB

    steps.sshagent (credentials: ["$credentialsId"]) {
      return steps.sh (script:"no_proxy=sanitas.dom && git ls-remote $repo $object | awk '{print \$1}'", returnStdout: true).trim()
    }
  }

  def isAllowedOrg() {
    for( org in canonicalOrgs ) {
      if( gitrepo.contains( org ) ) {
        return true
      }
    }
    return false
  }

  def isAllowedBranch() {
    isMasterBranch() || isDevelopBranch() || isHotfixBranch() || isFeatureBranch() || isReleaseCandidateBranch()
  }

  def getRepoOwner() {
    this.gitrepo?.startsWith( "git@" ) ? "" : this.gitrepo.substring(7).split("/")[2]
  }

  def isDevelopBranch() {
    "develop".equals( this.gitbranch )
  }

  def isHotfixBranch() {
    this.gitbranch?.toLowerCase().startsWith( "hotfix/" )
  }

  def isFeatureBranch() {
    this.gitbranch?.toLowerCase().startsWith( "feature/" )
  }

  def isMasterBranch( branch ) {
    "master".equals( branch ) || ( branch?.toLowerCase() ==~ /master-v\d+/ )
  }

  def isMasterBranch() {
    isMasterBranch( this.gitbranch )
  }

  def isPromotable( isSnapshot=false ) {
    isAllowedOrg() && ( isSnapshot || ( ( isMasterBranch() || isHotfixBranch() || isReleaseCandidateBranch() ) ) )
  }

  def isReleaseCandidateBranch() {
    steps.echo ":: $gitbranch ..."

    this.gitbranch?.toLowerCase().startsWith( "rc/" )
  }

  def classifierRc() {
    def dateFormat = new SimpleDateFormat( "yyyyMMddHHmmSS" )
    def date = new Date()

    "releasecandidate-" + dateFormat.format( date )
  }

  def branch( from, name, commit='HEAD' ) {
    this.clone()

    steps.withCredentials( [ [ $class: 'UsernamePasswordMultiBinding',
                               credentialsId: this.credentialsId,
                               usernameVariable: 'GIT_USERNAME',
                               passwordVariable: 'GIT_PASSWORD' ] ] ) {
      def repoWithoutProtocol= gitrepo.substring(7)
	  if( 'HEAD'.equals( commit ) ) {
          steps.echo ":: New branch from $from"
	  } else {
          steps.echo ":: New branch from $commit"
	  }
      steps.sh """
        git checkout $from
        git checkout -b $name $commit

        echo ":: git push new branch $name"
        git remote set-url origin http://${steps.env.GIT_USERNAME}:${steps.env.GIT_PASSWORD}@${repoWithoutProtocol}
        git push "http://${steps.env.GIT_USERNAME}:${steps.env.GIT_PASSWORD}@${repoWithoutProtocol}" $name
      """
    }
  }

  def merge( from, to, mergeUser="icUser" ) {
    this.clone()

    steps.withCredentials( [ [ $class: 'UsernamePasswordMultiBinding',
                               credentialsId: this.credentialsId,
                               usernameVariable: 'GIT_USERNAME',
                               passwordVariable: 'GIT_PASSWORD' ] ] ) {
      steps.echo ":: Merge branch $from into $to, requested by $mergeUser"
      def repoWithoutProtocol= gitrepo.substring(7)
      steps.sh """
        git remote set-url origin http://${steps.env.GIT_USERNAME}:${steps.env.GIT_PASSWORD}@${repoWithoutProtocol}

        git checkout $from
        git pull origin $from --rebase
        git checkout $to
        git pull origin $to --rebase

        echo ":: git merge - $mergeUser: Merge $from into $to"
        git merge $to $from
        git merge --ff-only $from -m "$mergeUser: Merge $from into $to"

        echo ":: git push merge"
        git push http://${steps.env.GIT_USERNAME}:${steps.env.GIT_PASSWORD}@${repoWithoutProtocol} $to

        echo ":: git delete branch $from"
        git push http://${steps.env.GIT_USERNAME}:${steps.env.GIT_PASSWORD}@${repoWithoutProtocol} :$from
      """
    }
  }

  def tag( tagName ) {
    steps.withCredentials( [ [ $class: 'UsernamePasswordMultiBinding',
                               credentialsId: this.credentialsId,
                               usernameVariable: 'GIT_USERNAME',
                               passwordVariable: 'GIT_PASSWORD' ] ] ) {
      def repoWithoutProtocol= gitrepo.substring(7)
      steps.echo ":: Create git tag $tagName"
      steps.sh """
        git tag -a $tagName -m "$tagName"
        git push "http://${steps.env.GIT_USERNAME}:${steps.env.GIT_PASSWORD}@${repoWithoutProtocol}" --tags
      """
    }
  }

  def release( tagName, jiraIssues ) {
    if( isMasterBranch() ) {
      steps.echo ":: Release $tagName"
      def ownerWithRepo = gitrepo.substring(26)
      def owner = ownerWithRepo.split("/")[0]
      def repo = ownerWithRepo.split("/")[1]
      def body = [:]
      body[ 'body' ] = jiraIssues
      body[ 'draft' ] = false
      body[ 'prerelease' ] = false
      body[ 'name' ] = tagName
      body[ 'tag_name' ] = tagName
      body[ 'target_commitish' ] = 'master'
      def requestBody = new JsonBuilder( body ).toString()

      try {
        def post = steps.httpRequest authentication: this.credentialsId,
                                         acceptType: 'APPLICATION_JSON_UTF8',
                                        contentType: 'APPLICATION_JSON_UTF8',
                                           httpMode: 'POST',
                                        requestBody: requestBody,
                                                url: "http://ic.sanitas.dom/git/api/v1/repos/$owner/$repo/releases",
                                 validResponseCodes: '201'
      } catch( AbortException ae ) {
        steps.echo "::::::::::::::::::::::::::::::::::::::::::::::::"
        steps.echo ":: error generating gitea release ${ae.message} "
        steps.echo "::::::::::::::::::::::::::::::::::::::::::::::::"
      }
    }
  }

}
