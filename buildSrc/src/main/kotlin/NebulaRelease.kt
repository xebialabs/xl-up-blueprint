import org.gradle.api.DefaultTask
import org.gradle.api.tasks.TaskAction
import org.gradle.kotlin.dsl.extra

open class NebulaRelease : DefaultTask() {

    @TaskAction
    fun doRelease() {
        val version = project.extra.get("releasedVersion")
        project.logger.lifecycle("Releasing version is: $version")

        project.exec {
            executable("./gradlew")
            args(
                "build", "uploadArchives", "-Prelease.version=$version", "final",
                "-Prelease.ignoreSuppliedVersionVerification=true"
            )
        }
    }
}
