import org.gradle.api.DefaultTask
import org.gradle.api.tasks.TaskAction

open class GenerateDocumentation : DefaultTask() {

    @TaskAction
    fun doRelease() {
        project.logger.lifecycle("Generating documentation from markdown files")

        project.exec {
            executable("./gradlew")
            args(
                "commitChanges",
                "-PgitBranchName=master",
                "-PgitMessage=Documentation has been updated",
                "-PgitFileContent=docs/*"
            )
        }
    }
}
