import org.gradle.api.DefaultTask
import org.gradle.api.tasks.TaskAction
import org.gradle.kotlin.dsl.extra
import org.gradle.process.ExecOperations
import javax.inject.Inject

open class NebulaRelease @Inject constructor(private val execOperations: ExecOperations) : DefaultTask() {

    @TaskAction
    fun doRelease() {
        val version = project.extra.get("releasedVersion")
        project.logger.lifecycle("Releasing version is: $version")

        execOperations.exec {
            executable = "./gradlew"
            args = listOf(
                "build", "uploadArchives", "-Prelease.version=$version", "final",
                "-Prelease.ignoreSuppliedVersionVerification=true"
            )
        }
    }
}
