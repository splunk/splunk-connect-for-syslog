You can run SC4S on AWS using ECS with the Fargate. This lets you run SC4S as a
managed, serverless container without provisioning EC2 instances.

Refer to AWS [documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started-fargate.html)
on how to set up your ECS environment and the AWS CLI.

!!! warning "Fargate ephemeral storage and the disk buffer"
    Fargate tasks use **ephemeral storage** that does **not** support the file locking that
    syslog-ng needs for its disk buffer. SC4S enables the disk buffer **by default**, so a Fargate task
    started with the default configuration will fail with:
    ```
    Failed to grab disk-buffer dirlock; filename='/var/lib/syslog-ng/syslog-ng-disk-buffer.dirlock', error='Bad file descriptor (9)'
    ```
    and then crash. You must either mount persistent storage (**recommended**) or disable the disk
    buffer. Both options are described in [Storage and the disk buffer](#storage-and-the-disk-buffer) below.

# Prepare your initial configuration

1. Decide how SC4S will forward to Splunk. At minimum you need your HEC URL and token. These are passed
   to the container as environment variables in the task definition:

    ``` dotenv
    SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=https://<SPLUNK_HEC_HOST>:8088
    SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=<SPLUNK_HEC_TOKEN>
    # Uncomment the following line if using untrusted SSL certificates
    # SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=no
    ```

2. (Optional) Create a CloudWatch log group for the task logs:

    ```bash
    aws logs create-log-group --log-group-name /ecs/sc4s
    ```

    A Fargate task has no local console and no host to attach to, so the container's `awslogs` stream is
    your only window into it. This is where SC4S's startup diagnostics are sent: the HEC connection
    check, and any errors such as the disk-buffer  failure shown above.
    Without it, a task that fails to start shows only as `STOPPED` with no visible reason.

    The example task definition below uses the `awslogs` log driver, which
    requires the named log group to already exist, otherwise the task fails to start. If you would rather
    not use CloudWatch, remove the `logConfiguration` block from the task definition instead (see the note
    under step 4).

3. Create the two IAM roles the task definition references. They are assumed by different principals at
   different times, so they are **not** interchangeable:

    - **Execution role** (`executionRoleArn`) — this is *Fargate's own* identity, used before your
      container starts: it pulls the image and ships container logs to CloudWatch. Attach the AWS-managed
      `AmazonECSTaskExecutionRolePolicy` (ECR pull + `logs:CreateLogStream`/`logs:PutLogEvents`). Add
      `logs:CreateLogGroup` only if you took the `awslogs-create-group` path in step 2.
    - **Task role** (`taskRoleArn`) — this is the identity **SC4S itself runs as**. SC4S delivers to
      Splunk over plain HTTPS, not an AWS API, so it needs *no* AWS permissions for its actual job. The
      only reason this task definition needs a task role is the EFS volume: with `"iam": "ENABLED"`, EFS
      authorizes the mount against the task role, so it needs EFS client access to your file system and
      access point.

    Both roles share the same trust policy (`trust.json`):

    ```json
    {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}
    ```

    Task-role EFS permissions (`efs-policy.json`) — replace the region, account, and EFS IDs:

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

    # task role (+ the EFS inline policy)
    aws iam create-role --role-name sc4s-task-role --assume-role-policy-document file://trust.json
    aws iam put-role-policy --role-name sc4s-task-role \
      --policy-name sc4s-efs-access --policy-document file://efs-policy.json
    ```

    Use the resulting ARNs (`arn:aws:iam::<ACCOUNT_ID>:role/sc4s-execution-role` and
    `.../sc4s-task-role`) for `executionRoleArn` and `taskRoleArn` in the task definition.

    !!! note "Option B (no EFS) needs no task role"
        If you disable the disk buffer (Option B below) there is no IAM-authorized mount, so SC4S needs
        no AWS permissions at all. You can skip the task role entirely — omit `taskRoleArn` from the task
        definition and create only the execution role.

4. Create the task definition. The following is a complete example for a single SC4S container on
   Fargate. It mounts an EFS access point at `/var/lib/syslog-ng` so the disk buffer keeps working
   (see [Storage and the disk buffer](#storage-and-the-disk-buffer)). Replace every `<...>` placeholder
   with your own values.

    ``` json
    --8<---- "docs/resources/ecs/sc4s-task-definition.json"
    ```

    !!! note "If you skipped the CloudWatch log group"
        The `logConfiguration` block at the end of the container definition ships logs to the
        `/ecs/sc4s` log group from step 2. If you did not create that log group, either remove the whole
        `logConfiguration` block, or set `"awslogs-create-group": "true"` in its `options` and add the
        `logs:CreateLogGroup` permission to the task execution role (the managed
        `AmazonECSTaskExecutionRolePolicy` does not grant it).

    Register it with:

    ```bash
    aws ecs register-task-definition --cli-input-json file://sc4s-task-definition.json
    ```

# Storage and the disk buffer

SC4S keeps its disk buffer in `/var/lib/syslog-ng`. The disk buffer protects the **SC4S → Splunk**
hop: if Splunk (or HEC) is unreachable, events queue on disk and drain when it recovers, instead of
being dropped. Because Fargate's local storage is ephemeral and cannot be locked, you have two options.

## Option A — Mount EFS (recommended)

Mount an Amazon EFS access point at `/var/lib/syslog-ng`. EFS supports the locking syslog-ng needs, so
the disk buffer stays enabled and you keep full outage protection. This is what the example task
definition above does, via its `volumes` and `mountPoints` blocks:

```json
"volumes": [
  {
    "name": "sc4s-var",
    "efsVolumeConfiguration": {
      "fileSystemId": "<EFS_FILE_SYSTEM_ID>",
      "transitEncryption": "ENABLED",
      "authorizationConfig": {
        "accessPointId": "<EFS_ACCESS_POINT_ID>",
        "iam": "ENABLED"
      }
    }
  }
],
```

Setup notes:

- Create the EFS file system in the **same VPC** as your tasks, with a **mount target in each subnet/AZ**
  the service runs in.
- The EFS security group must allow **NFS (TCP 2049)** inbound from the task security group.
- Create an **access point** so each task gets a consistent POSIX identity and root directory. In the
  SC4S container the syslog-ng process runs as the non-root `syslog` user, **UID/GID 1024**, so set the
  access point's POSIX user and group — and the owner of its root directory — to `1024` so the buffer
  directory is writable.
- If you run more than one task, give **each task its own subdirectory** (a dedicated access point per
  task, or a unique path). Two syslog-ng instances must not share the same buffer directory.

## Option B — Disable the disk buffer (workaround)

If you do not need on-disk buffering, disable it and SC4S will start on ephemeral storage with no
persistent volume. Add this environment variable to the container definition and remove the `volumes`
and `mountPoints` blocks:

```json
{"name": "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE", "value": "no"}
```

!!! danger "Data-loss trade-off"
    With the disk buffer disabled, SC4S only holds an **in-memory** queue for the Splunk destination.
    If Splunk/HEC is unreachable and that queue fills — or the task is stopped or replaced — **buffered
    events are lost**. This is acceptable for a quick proof of concept or for loss-tolerant data, but for
    production use prefer **Option A (EFS)**.

# Networking and load balancing

In `awsvpc` network mode (required by Fargate) each task gets its own elastic network interface and IP.
Open the syslog ports on the task's security group: `514/udp`, `514/tcp`, `601/tcp`, `6514/tcp`, and the
health-check port `8080/tcp`.

To place a stable endpoint in front of one or more tasks, use a **Network Load Balancer (NLB)** — it is
the only AWS-managed load balancer that supports UDP as well as TCP/TLS. Point a target group
(`target-type: ip`) at the task IPs and enable `preserve_client_ip` so SC4S still sees the real sender
address (SC4S keys host and vendor identification off the source IP).

Before you put a load balancer in front of SC4S, read
[Load balancing](../architecture/lb/index.md) — load balancing syslog has important
caveats (uneven distribution, connection stickiness at L4, and source-IP preservation) and is not
supported by Splunk. For the health check, use an **HTTP** check against `GET /health` on port `8080`
rather than a bare TCP port check: the `/health` endpoint returns `200` only when syslog-ng itself is
alive, so it detects a container whose HTTP listener is up but whose pipeline has failed.

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
    `sc4s_container` field — each task reports a distinct value:

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
