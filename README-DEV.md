# xl-up-blueprint

To test the blueprint locally you need `xl cli` on your machine  and also clone this repository:

```$xslt
xl up -b xl-infra -l /PATH/TO/xl-up-blueprint/
```

When you make a PR and also want to run integration test against an existing EKS cluster, GKE or Plain mutlinode K8s cluster then add label ``run-xl-up-pr`` in your github PR, then this pr will run against master in xl-cli branch. If you are working in story that has changes also in xl-cli repo in a branch with the same name then also add ``same-branch-on-cli`` label in your pr