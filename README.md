 # Pulumi infra

 A minimal Pulumi packages for provisioning a single AWS EC2 bucket using Python.

 ## Prerequisites

 - An AWS account with permissions to create EC2.
 - AWS credentials configured in your environment (for example via AWS CLI or environment variables).
 - Python 3.6 or later installed.
 - Pulumi CLI already installed and logged in.

 ## Getting Started

 1. Setup the local environment:
   ```bash
   mkdir -p ~/.pulumi-local-state
   pulumi login file://$HOME/.pulumi-local-state
   ```

 2. Follow the prompts to set your project name and AWS region (default: `eu-west-2`).

 3. Preview the planned changes:
   ```bash
   pulumi preview
   ```
 
 5. Deploy the stack:
   ```bash
   pulumi up
   ```
 
 6. Tear down when finished:
   ```bash
   pulumi destroy
   ```

 ## Configuration

 This template defines the following config value:

 - `aws:region` (string)
   The AWS region to deploy resources into.
   Default: `us-east-1`

 View or update configuration with:
 ```bash
 pulumi config get aws:region
 pulumi config set aws:region us-west-2
 ```

 ## Outputs

 Retrieve outputs with:
 ```bash
 pulumi stack output
 ```

 ## Help and Community

 If you have questions or need assistance:
 - Pulumi Documentation: https://www.pulumi.com/docs/
 - Community Slack: https://slack.pulumi.com/
 - GitHub Issues: https://github.com/pulumi/pulumi/issues

 Contributions and feedback are always welcome!