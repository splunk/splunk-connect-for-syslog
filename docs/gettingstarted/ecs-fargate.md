You can run SC4S on AWS using ECS with the Fargate. This lets you run SC4S as a
managed, serverless container without provisioning EC2 instances.

Refer to AWS [documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started-fargate.html)
on how to set up your ECS environment and the AWS CLI.

# Prepare your initial configuration

!!! warning "Fargate ephemeral storage and the disk buffer"
    Fargate tasks use **ephemeral storage** that does **not** support the file locking that
    syslog-ng needs for its disk buffer. SC4S enables the disk buffer **by default**, so a Fargate task
    started with the default configuration will fail with:
    ```
    Failed to grab disk-buffer dirlock; (...)
    ```
    You must either mount persistent storage (recommended) or disable the disk
    buffer. Both options are described in [Storage and the disk buffer](#storage-and-the-disk-buffer) below.

1. Make sure the following AWS resources exist, all in the same region and VPC. This guide assumes you
   are comfortable with ECS and the AWS CLI:

    - An **ECS cluster** to run the Fargate task in.
    - Subnets in the availability zones you will run in, and a **security group** for the task that allows
      the syslog ports inbound (`514/udp`, `514/tcp`, `601/tcp`, `6514/tcp`) and can reach Splunk HEC
      outbound (see [Networking and load balancing](#networking-and-load-balancing)).
    - If you are using persistent storage: an **EFS file system and access point** for the disk buffer.

    You also need your **Splunk HEC URL and token**. Unlike SC4S's other runtimes there is no env file:
    HEC settings and all other variables are set directly in the task definition's environment block.

2. Create a CloudWatch log group for the task logs (**optional**):

    ```bash
    aws logs create-log-group --log-group-name /ecs/sc4s
    ```

    A Fargate task has no local console and no host to attach to, so the container's awslogs stream is
    how you can monitor it. This is where SC4S's startup diagnostics are sent: the HEC connection
    check, and any errors such as the disk-buffer  failure shown above.

    The example task definition below uses the `awslogs` log driver, which
    requires the named log group to already exist, otherwise the task fails to start. If you would rather
    not use CloudWatch, remove the `logConfiguration` block from the task definition instead.

3. Create the two IAM roles the task definition references. They are assumed by different principals at
   different times, so they are not interchangeable:

    - **Execution role** (`executionRoleArn`) - this is Fargate's own identity, used before your
      container starts: it pulls the image and ships container logs to CloudWatch. You will have to attach the AWS-managed `AmazonECSTaskExecutionRolePolicy`.
    - **Task role** (`taskRoleArn`) - this is the identity **SC4S itself runs as**. If you disable the disk buffer there is no IAM-authorized mount, so SC4S needs no AWS permissions at all and you can skip this role. If you plan on using EFS it needs EFS client access to your file system and access point.

    Both roles share the same trust policy (`trust.json`):

    ```json
    {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}
    ```

    Task-role EFS permissions example (`efs-policy.json`): replace the region, account, and EFS IDs:

    ```json
    {
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Action": ["elasticfilesystem:ClientMount", "elasticfilesystem:ClientWrite"],
        "Resource": "arn:aws:elasticfilesystem:<AWS_REGION>:<ACCOUNT_ID>:file-system/<EFS_FILE_SYSTEM_ID>",
        "Condition": {
          "StringEquals": {
            "elasticfilesystem:AccessPointArn": "arn:aws:elasticfilesystem:<AWS_REGION>:<ACCOUNT_ID>:access-point/<EFS_ACCESS_POINT_ID>"
          }
        }
      }]
    }
    ```

    Create both roles:

    ```bash
    # execution role
    aws iam create-role --role-name sc4s-execution-role --assume-role-policy-document file://trust.json
    aws iam attach-role-policy --role-name sc4s-execution-role \
      --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

    # task role
    aws iam create-role --role-name sc4s-task-role --assume-role-policy-document file://trust.json
    aws iam put-role-policy --role-name sc4s-task-role \
      --policy-name sc4s-efs-access --policy-document file://efs-policy.json
    ```

    Use the resulting ARNs (`arn:aws:iam::<ACCOUNT_ID>:role/sc4s-execution-role` and
    `arn:aws:iam::<ACCOUNT_ID>:role/sc4s-task-role`) for `executionRoleArn` and `taskRoleArn` in the task definition.

    !!! note "Option without EFS needs no task role"
        If you disable the disk buffer there is no IAM-authorized mount, so SC4S needs no AWS permissions at all. You can skip the task role entirely — omit `taskRoleArn` from the task definition and create only the execution role.

4. Create the task definition. The following is a complete example for a single SC4S container on Fargate. It mounts an EFS access point at `/var/lib/syslog-ng` so the disk buffer keeps working (see [Storage and the disk buffer](#storage-and-the-disk-buffer)). Replace every `<...>` placeholder with your own values.

    ``` json
    --8<---- "docs/resources/ecs/sc4s-task-definition.json"
    ```

    !!! note "If you skipped the CloudWatch log group"
        The `logConfiguration` block at the end of the container definition ships logs to the `/ecs/sc4s` log group from step 2. If you did not create that log group, you have to remove the whole `logConfiguration` block.

    Below you can find a minimal working example of a task definition, this one doesn't have any diskbuffer or task log configuration:

    ``` json
    --8<---- "docs/resources/ecs/sc4s-task-definition-minimal.json"
    ```

    Register either one with:

    ```bash
    aws ecs register-task-definition --cli-input-json file://sc4s-task-definition.json
    ```

# Storage and the disk buffer

SC4S keeps its disk buffer in `/var/lib/syslog-ng`. The disk buffer protects the SC4S -> Splunk connection: if Splunk (or HEC) is unreachable, events queue on disk and drain when it recovers, instead of being dropped. Because Fargate's local storage is ephemeral and cannot be locked, you have two options.

## Option A: Mount EFS

Mount an Amazon EFS access point at `/var/lib/syslog-ng`. EFS supports the locking syslog-ng needs, so the disk buffer stays enabled and you keep full outage protection.

First create the file system and an access point. The syslog-ng process in the container runs as the non-root `syslog` user, UID/GID 1024, so the access point owns its root directory as `1024` and forces that identity on every task:

```bash
# 1. Create the file system -> returns "FileSystemId": "fs-0123456789abcdef0"
aws efs create-file-system --encrypted --tags Key=Name,Value=sc4s-var

# 2. A mount target in each subnet/AZ your tasks run in (repeat per subnet).
#    <EFS_SG> must allow inbound NFS (TCP 2049) from the task security group.
aws efs create-mount-target --file-system-id <EFS_FILE_SYSTEM_ID> \
  --subnet-id <SUBNET_ID> --security-groups <EFS_SG>

# 3. An access point rooted at /sc4s, owned and entered as UID/GID 1024
#    -> returns "AccessPointId": "fsap-0123456789abcdef0"
aws efs create-access-point --file-system-id <EFS_FILE_SYSTEM_ID> \
  --posix-user Uid=1024,Gid=1024 \
  --root-directory 'Path=/sc4s,CreationInfo={OwnerUid=1024,OwnerGid=1024,Permissions=0755}'
```

The two IDs those commands return are what you paste into the task definition's `volumes` block.

Setup notes:

- Create the EFS file system in **the same VPC** as your tasks, with a mount target in each subnet/AZ the service runs in.
- The EFS security group must allow **NFS (TCP 2049)** inbound from the task security group.

!!! warning "One task per access point"
    Every task started from a task definition mounts the same access point, so running a service
    with `--desired-count` greater than `1` makes several syslog-ng instances share one buffer
    directory, and collide trying to access the same resources.

    Giving each task its own directory requires a separate access point **and** a separate task
    definition, which cannot be expressed through a single ECS service's desired count. In practice
    this means you have to choose:

    - EFS disk buffer with a single task,
    - EFS disk buffer with multiple tasks, each task as its own single-task service with its own access point and task definition,
    - Multiple tasks with the disk buffer disabled , accepting the data-loss risk.

## Option B: Disable the disk buffer

If you do not need on-disk buffering, disable it and SC4S will start on ephemeral storage with no persistent volume. Add this environment variable to the container definition and remove the `volumes` and `mountPoints` blocks:

```json
{"name": "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE", "value": "no"}
```

!!! danger "Data-loss without disk buffer"
    With the disk buffer disabled, SC4S only holds an in-memory queue for the Splunk destination. If Splunk/HEC is unreachable and that queue fills, or the task is stopped or replaced - **buffered events are lost**. This is acceptable for a  proof of concept or for loss-tolerant data, but for production use prefer **Option A (EFS)**.

# Networking and load balancing

In `awsvpc` network mode (required by Fargate) each task gets its own elastic network interface and IP.
Open the syslog ports on the task's security group: `514/udp`, `514/tcp`, `601/tcp`, `6514/tcp`, and the
health-check port `8080/tcp`.

(sbylica note: ok we need to talk about it some more during the review!)
To place a stable endpoint in front of one or more tasks, use a **Network Load Balancer (NLB)**: it is
the only AWS-managed load balancer that supports UDP as well as TCP/TLS. Point a target group
(`target-type: ip`) at the task IPs and enable `preserve_client_ip` so SC4S still sees the real sender
address (SC4S keys host and vendor identification off the source IP).

Before you put a load balancer in front of SC4S, read
[Load balancing](../architecture/lb/index.md): load balancing syslog has important
caveats and is not officialy supported by Splunk.

# Run SC4S as a service

Run SC4S as an ECS **service** so ECS keeps the desired number of tasks running and replaces any that
fail:

```bash
aws ecs create-service \
  --cluster <CLUSTER_NAME> \
  --service-name sc4s \
  --task-definition sc4s \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SECURITY_GROUP_ID>],assignPublicIp=ENABLED}"
```

To front the service with the NLB, add `--load-balancers` and `--health-check-grace-period-seconds 60`
(SC4S needs roughly 30–60s to boot before `/health` answers).

# Validate your configuration

1. Confirm the task reaches and stays in the `RUNNING` state:

    ```bash
    aws ecs describe-tasks --cluster <CLUSTER_NAME> --tasks <TASK_ARN> \
      --query 'tasks[0].{lastStatus:lastStatus,health:healthStatus}'
    ```

2. Check the container logs in CloudWatch. On a healthy start you should see:

    ```ini
    SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:events...
    syslog-ng checking config
    Configuring the health check port to: 8080
    [INFO] Listening at: http://0.0.0.0:8080
    starting syslog-ng
    ```

    ```bash
    aws logs tail /ecs/sc4s --follow
    ```

3. Validate that SC4S is delivering to Splunk. Run this search in Splunk:

    ```ini
    index=* sourcetype=sc4s:events "starting up"
    ```

    If you run more than one task, confirm traffic is spread across them by checking the indexed
    `sc4s_container` field - each task reports a distinct value:

    ```ini
    index=* | stats count by sc4s_container
    ```

# Update SC4S

Register a new revision of the task definition (for example after changing an environment variable or
image tag), then update the service to it:

```bash
aws ecs update-service --cluster <CLUSTER_NAME> --service sc4s \
  --task-definition sc4s --force-new-deployment
```

ECS performs a rolling replacement of the tasks.

# Stop SC4S

Scale the service to zero, then delete it:

```bash
aws ecs update-service --cluster <CLUSTER_NAME> --service sc4s --desired-count 0
aws ecs delete-service --cluster <CLUSTER_NAME> --service sc4s
```
