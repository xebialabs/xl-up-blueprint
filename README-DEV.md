# xl-up-blueprint

To test the blueprint locally you need `xl cli` on your machine  and also clone this repository:

```$xslt
xl up -b xl-infra -l /PATH/TO/xl-up-blueprint/
```

When you make a PR and also want to run integration test against an existing EKS cluster, GKE or Plain mutlinode K8s cluster then add label ``run-xl-up-pr`` in your github PR. If you want to run the integration tests on master then add label ``run-xl-up-master``. Make sure that you do run the integration tests if another PR with the same label is running 