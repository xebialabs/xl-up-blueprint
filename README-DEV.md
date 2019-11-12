# xl-up-blueprint

To test the blueprint locally you need `xl cli` on your machine  and also clone this repository:

```$xslt
xl up -b xl-infra -l /PATH/TO/xl-up-blueprint/
```

When you make a PR and also want to run integration test against an existing EKS cluster, GKE or Plain mutlinode K8s cluster then add label ``run-xl-up-pr`` in your github PR, then this pr will run against master in xl-cli branch. If you are working in story that has changes also in xl-cli repo in a branch with the same name then also add ``same-branch-on-cli`` label in your pr

# Testing v2

A need arose to be able to test more than simple existence/non-existence of files. Thus the [xl-blueprint-test](https://github.com/xebialabs/xl-yaml-test) repo was created. The binary from that repo is here, called `main`.

The new test framework necessitates a new test file structure. But fear not! The ability to convert existing test files to the new format is also included. This is done simply by doing the following

```
./main --convert ./integration-tests/test-cases/
```

This command will recursively look for `test-*` YAML files, and output their equivelant to a folder called `v2` within said tests' directory. When we're ready, we can then delete the old tests and move to using the new format instead. 

## Running v2 tests

To actually run the v2 tests - run the following command

```
./main --local-repo-path $(pwd) --blueprint-directory xl-infra --test-path './integration-tests/test-cases/**/v2'
```

This will again recurse through the `test-path` provided within `local-repo-path`, and run all the tests it finds in sequence. Now you might wonder why it takes so long (+- 1 minute at the time of writing this). Reason is that it runs many more tests than it used to using the old method. Each file will contain roughly 100 assertions after conversion - that's excluding the content assertions. We have tried implementing parallel testing with a `--parallel` flag, but somewhere that got messed up as the `xl` binary keeps throwing weird memory panics. Might need to look into this further as required. 

An example for this new format can be found in the `xl-yaml-test` repo. An example test for the new RabbitMQ setup is already included in this repo. 

# Clean up disk in AWS and GCP

The default policy of volumes deletion is RETAIN. This means that during testing many volumes are created but not deleted and this result in polluting the cloud infra. To clean up the volumes run this command in

AWS:

```$xslt
for i in `aws ec2 describe-volumes --query "Volumes[*].{ID:VolumeId,Name:Tags[?Key=='Name'].Value}" --output text | grep kubernetes-dynamic | awk '{print $1}'`; do aws ec2 delete-volume --volume-id $i; done
```   

GCP:

```$xslt
for i in `gcloud compute disks list | grep xl-up-cluster--pvc | awk '{print $1}'`; do gcloud compute disks delete $i -q; done
```