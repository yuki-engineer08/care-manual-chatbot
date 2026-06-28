output "github_actions_role_arn" {
  description = "GitHub ActionsワークフローがOIDCで引き受けるIAMロールのARN（GitHub Secretsの AWS_ROLE_ARN に設定する）"
  value       = aws_iam_role.github_actions_deploy.arn
}
