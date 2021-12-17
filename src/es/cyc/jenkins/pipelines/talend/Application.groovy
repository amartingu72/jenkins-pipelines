package es.cyc.jenkins.pipelines


import groovy.json.JsonOutput

class Application implements Serializable {
    
    def actionName="updateEsbTask"
    def taskId
    def taskName
    def description="demo-update"
    def tag="Mygroup-update"
    def repository
    def featureUrl
    def featureName
    def featureVersion
    def featureType="ROUTE"
    def runtimeContext="Default"
    def runtimeServerName
    def runtimePropertyId="DemoRESTRoute"
    def authPass
    def authUser
    def context

    Application(groupId, artifactId, version ){
        this.featureUrl=String.format("mvn:%s/%s/%s/xml", groupId, artifactId, version)
        this.featureName=artifactId
        this.featureVersion=version
    }

    def setTaskId(taskId){
        this.taskId=this.taskId
    }

    def setTaskName(taskName){
        this.taskName=taskName
    }

    def setRepository(repository) {
        this.repository=repository
    }
    
    def setRuntimeServerName(runtimeServerName){
        this.runtimeServerName=runtimeServerName
    }

    def setAuthPass(authPass){
        this.authPass=authPass
    }

    def setAuthUser(authUser){
        this.authUser=authUser
    }

    def setContext(context) {
        this.context=context
    }

    
    static void main(String[] args) {
        def app=new Application('es.cyc.talend',"myArtifact", '1.0.0')
        
        println( JsonOutput.toJson(app))
        
    }

}