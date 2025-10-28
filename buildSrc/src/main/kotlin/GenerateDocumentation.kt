import org.gradle.api.DefaultTask
import org.gradle.api.tasks.TaskAction
import org.gradle.process.ExecOperations
import javax.inject.Inject

open class GenerateDocumentation @Inject constructor(private val execOperations: ExecOperations) : DefaultTask() {

    @TaskAction
    fun doRelease() {
        project.logger.lifecycle("Generating documentation from markdown files")

        execOperations.exec {
            executable = "./gradlew"
            args = listOf(
                "commitChanges",
                "-PgitBranchName=master",
                "-PgitMessage=Documentation has been updated",
                "-PgitFileContent=docs/*"
            )
        }
    }
}
