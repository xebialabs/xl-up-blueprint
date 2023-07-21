import com.github.gradle.node.yarn.task.YarnTask
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

buildscript {
    repositories {
        mavenLocal()
        gradlePluginPortal()
        arrayOf("releases", "public").forEach { r ->
            maven {
                url = uri("${project.property("nexusBaseUrl")}/repositories/${r}")
                credentials {
                    username = project.property("nexusUserName").toString()
                    password = project.property("nexusPassword").toString()
                }
            }
        }
    }

    dependencies {
        classpath("com.xebialabs.gradle.plugins:gradle-commit:${properties["gradleCommitPluginVersion"]}")
        classpath("com.xebialabs.gradle.plugins:gradle-xl-defaults-plugin:${properties["xlDefaultsPluginVersion"]}")
    }
}

plugins {
    kotlin("jvm") version "1.8.10"

    id("com.github.node-gradle.node") version "4.0.0"
    id("idea")
    id("nebula.release") version (properties["nebulaReleasePluginVersion"] as String)
    id("maven-publish")
}

apply(plugin = "ai.digital.gradle-commit")

group = "ai.digital.xlclient.blueprints"
project.defaultTasks = listOf("build")

val releasedVersion = System.getenv()["RELEASE_EXPLICIT"] ?: if (project.version.toString().contains("SNAPSHOT")) {
    project.version.toString()
} else {
    "23.3.0-${LocalDateTime.now().format(DateTimeFormatter.ofPattern("Mdd.Hmm"))}"
}
project.extra.set("releasedVersion", releasedVersion)

repositories {
    mavenLocal()
    gradlePluginPortal()
    maven {
        url = uri("https://plugins.gradle.org/m2/")
    }
}

idea {
    module {
        setDownloadJavadoc(true)
        setDownloadSources(true)
    }
}

dependencies {
    implementation(gradleApi())
    implementation(gradleKotlinDsl())

}

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

tasks.named<Test>("test") {
    useJUnitPlatform()
}

tasks {

    register<Zip>("blueprintsArchives") {
        group = "blueprint"
        from("./") {
            include("xl-infra/**/*")
            include("xl-up/**/*")
            include("*.json")
            include("LICENSE.txt")
            archiveBaseName.set("xl-up-blueprints")
            archiveVersion.set(releasedVersion)
            archiveExtension
        }
    }

    register<Exec>("copyBlueprintsArchives") {
        group = "blueprint-dist"
        dependsOn("blueprintsArchives")

        if (project.hasProperty("versionToSync") && project.property("versionToSync") != "") {
            val versionToSync = project.property("versionToSync")
            val commandUnzip =
                "ssh xebialabs@nexus1.xebialabs.cyso.net " +
                        "rm -fr /tmp/xl-up-blueprints/$versionToSync/; mkdir -p /tmp/xl-up-blueprints/$versionToSync; " +
                        "cd /tmp/xl-up-blueprints/$versionToSync/;" +
                        "unzip -o /opt/sonatype-work/nexus/storage/digitalai-public/ai/digital/xlclient/blueprints/xl-up-blueprints/$versionToSync/xl-up-blueprints-$versionToSync.zip"

            commandLine(commandUnzip.split(" "))
        } else {
            commandLine("echo",
                "You have to specify which version you want to sync, ex. ./gradlew syncBlueprintsArchives -PversionToSync=22.3.0")
        }
    }

    register<Exec>("syncBlueprintsArchives") {
        group = "blueprint-dist"
        dependsOn("blueprintsArchives", "copyBlueprintsArchives")

        if (project.hasProperty("versionToSync") && project.property("versionToSync") != "") {
            val versionToSync = project.property("versionToSync")

            val commandRsync =
                "ssh xebialabs@nexus1.xebialabs.cyso.net rsync --update -raz -i --chmod=Du=rwx,Dg=rx,Do=rx,Fu=rw,Fg=r,Fo=r --include='*' " +
                        "/tmp/xl-up-blueprints/$versionToSync/ " +
                        "xldown@dist.xebialabs.com:/var/www/dist.xebialabs.com/public/xl-up-blueprints/$versionToSync"

            commandLine(commandRsync.split(" "))
        } else {
            commandLine("echo",
                "You have to specify which version you want to sync, ex. ./gradlew syncBlueprintsArchives -PversionToSync=22.3.0")
        }
    }

    register("syncToDistServer") {
        group = "blueprint-dist"
        dependsOn("syncBlueprintsArchives")
    }

    register("buildBlueprints") {
        group = "blueprint"
        dependsOn("blueprintsArchives")
    }

    register("checkDependencyVersions") {
        // a placeholder to unify with release in jenkins-job
    }

    register("uploadArchives") {
        group = "upload"
        dependsOn("dumpVersion", "publish")
    }

    register("uploadArchivesMavenRepository") {
        group = "upload"
        dependsOn("dumpVersion", "publishAllPublicationsToMavenRepository")
    }

    register("uploadArchivesToMavenLocal") {
        group = "upload"
        dependsOn("dumpVersion", "publishToMavenLocal")
    }

    register("dumpVersion") {
        group = "release"
        doLast {
            project.logger.lifecycle("Dumping version $releasedVersion")
            file(buildDir).mkdirs()
            file("$buildDir/version.dump").writeText("version=${releasedVersion}")
        }
    }

    register<NebulaRelease>("nebulaRelease") {
        group = "release"
        dependsOn(named("buildOperators"), named("updateDocs"))
    }

    named<YarnTask>("yarn_install") {
        group = "doc"
        args.set(listOf("--mutex", "network"))
        workingDir.set(file("${rootDir}/documentation"))
    }

    register<YarnTask>("yarnRunStart") {
        group = "doc"
        dependsOn(named("yarn_install"))
        args.set(listOf("run", "start"))
        workingDir.set(file("${rootDir}/documentation"))
    }

    register<YarnTask>("yarnRunBuild") {
        group = "doc"
        dependsOn(named("yarn_install"))
        args.set(listOf("run", "build"))
        workingDir.set(file("${rootDir}/documentation"))
    }

    register<Delete>("docCleanUp") {
        group = "doc"
        delete(file("${rootDir}/docs"))
        delete(file("${rootDir}/documentation/build"))
        delete(file("${rootDir}/documentation/.docusaurus"))
        delete(file("${rootDir}/documentation/node_modules"))
    }

    register<Copy>("docBuild") {
        group = "doc"
        dependsOn(named("yarnRunBuild"), named("docCleanUp"))
        from(file("${rootDir}/documentation/build"))
        into(file("${rootDir}/docs"))
    }

    register<GenerateDocumentation>("updateDocs") {
        group = "doc"
        dependsOn(named("docBuild"))
    }
}

tasks.withType<AbstractPublishToMaven> {
    dependsOn("build")
}

tasks.named("build") {
    dependsOn("buildBlueprints")
}

publishing {
    publications {
        register("xl-up-blueprints-archive", MavenPublication::class) {
            artifact(tasks["blueprintsArchives"]) {
                artifactId = "xl-up-blueprints"
                version = releasedVersion
            }
        }
    }

    repositories {
        maven {
            url = uri("${project.property("nexusBaseUrl")}/repositories/digitalai-public")
            credentials {
                username = project.property("nexusUserName").toString()
                password = project.property("nexusPassword").toString()
            }
        }
    }
}

node {
    version.set("16.13.2")
    yarnVersion.set("1.22.17")
    download.set(true)
}
