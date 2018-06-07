try { // massive try{} catch{} around the entire build for failure notifications
    timestamps {
        node('docker') {
            checkout scm
            stage('Build the scrapers Docker image') {
                docker.withRegistry('https://quay.io/', 'quay-io-factory2-builder-sa-credentials') {
                    def image = docker.build "factory2/estuary-scrapers:latest", "-f docker/Dockerfile-scrapers ."
                    image.push()
                }
            }

            stage('Build the API Docker image') {
                docker.withRegistry('https://quay.io/', 'quay-io-factory2-builder-sa-credentials') {
                    def image = docker.build "factory2/estuary-api:latest", "-f docker/Dockerfile-api ."
                    image.push()
                }
            }
        }
    }
} catch (e) {
    if (ownership.job.ownershipEnabled) {
        mail to: ownership.job.primaryOwnerEmail,
             cc: ownership.job.secondaryOwnerEmails.join(', '),
             subject: "Jenkins job ${env.JOB_NAME} #${env.BUILD_NUMBER} failed",
             body: "${env.BUILD_URL}\n\n${e}"
    }
    throw e
}
