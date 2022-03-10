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
    kotlin("jvm") version "1.4.20"

    id("com.github.node-gradle.node") version "3.1.0"
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
    "22.2.0-${LocalDateTime.now().format(DateTimeFormatter.ofPattern("Mdd.Hmm"))}"
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
    register("dumpVersion") {
        doLast {
            project.logger.lifecycle("Dumping version $releasedVersion")
            file(buildDir).mkdirs()
            file("$buildDir/version.dump").writeText("version=${releasedVersion}")
        }
    }

    named<YarnTask>("yarn_install") {
        args.set(listOf("--mutex", "network"))
        workingDir.set(file("${rootDir}/documentation"))
    }

    register<YarnTask>("yarnRunStart") {
        dependsOn(named("yarn_install"))
        args.set(listOf("run", "start"))
        workingDir.set(file("${rootDir}/documentation"))
    }

    register<YarnTask>("yarnRunBuild") {
        dependsOn(named("yarn_install"))
        args.set(listOf("run", "build"))
        workingDir.set(file("${rootDir}/documentation"))
    }

    register<Delete>("docCleanUp") {
        delete(file("${rootDir}/docs"))
        delete(file("${rootDir}/documentation/build"))
        delete(file("${rootDir}/documentation/.docusaurus"))
        delete(file("${rootDir}/documentation/node_modules"))
    }

    register<Copy>("docBuild") {
        dependsOn(named("yarnRunBuild"), named("docCleanUp"))
        from(file("${rootDir}/documentation/build"))
        into(file("${rootDir}/docs"))
    }

    register<GenerateDocumentation>("updateDocs") {
        dependsOn(named("docBuild"))
    }

    register<Zip>("blueprintsArchives") {
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


    register<NebulaRelease>("nebulaRelease") {
        dependsOn(named("buildOperators"), named("updateDocs"))
    }

    register<Exec>("syncBlueprintsArchives") {
        dependsOn("blueprintsArchives")
        val command =
            "ssh xebialabs@nexus1.xebialabs.cyso.net rsync -razv --delete --chmod=Du=rwx,Dg=rx,Do=rx,Fu=rw,Fg=r,Fo=r --include='/xl-infra/***' " +
                    "--include='/xl-up/***' --include='index.json' --include='LICENCE.txt' --exclude='*' . " +
                    "xldown@dist.xebialabs.com:/var/www/dist.xebialabs.com/public/xl-up-blueprints/$releasedVersion"
        commandLine(command.split(" "))
    }

    register("syncToDistServer") {
        dependsOn("syncBlueprintsArchives")
    }

    named<Upload>("uploadArchives") {
        dependsOn(named("dumpVersion"))
        dependsOn(named("publish"))
    }

    register("buildOperators") {
        dependsOn("blueprintsArchives")
    }

    register("checkDependencyVersions") {
        // a placeholder to unify with release in jenkins-job
    }
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
