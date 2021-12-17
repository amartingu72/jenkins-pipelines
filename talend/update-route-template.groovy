import es.cyc.jenkins.pipelines.*

nodeLabel = 'rhel8'
import groovy.json.JsonOutput


try {

  node( nodeLabel ) {

    stage ('Getting taks id'){
        steps.echo ":: Calling Talend ESP API..."
    }

    stage ('Updating route'){
        steps.echo ":: Calling Talend ESP API..."
        def app=new Application(params.groupId, params.artifactId, params.version)
        steps.echo JsonOutput.toJson(app)

    }
  }
} catch ( e ) {
  //pipelines.handleGlobalPipelineException( e, currentBuild, params.notif_emails, '$PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS!' )
  println "Error"
}
   