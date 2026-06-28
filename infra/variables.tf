variable "aws_region" {
  description = "デプロイ対象リソースが存在するAWSリージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "github_org" {
  description = "GitHubのOrganization名（またはユーザー名）"
  type        = string
  default     = "yuki-engineer08"
}

variable "github_repo" {
  description = "リポジトリ名（Organization/ユーザー名を含まないリポジトリ名のみ）"
  type        = string
  default     = "care-manual-chatbot"
}

variable "github_branch" {
  description = "IAMロールの引き受けを許可するブランチ名"
  type        = string
  default     = "main"
}

variable "stack_name" {
  description = "CloudFormationスタック名（SAMデプロイ先）"
  type        = string
  default     = "care-manual-chatbot"
}

variable "s3_frontend_bucket_arn" {
  description = "フロントエンド静的ファイルを配置するS3バケットのARN"
  type        = string
  default     = "arn:aws:s3:::care-manual-chatbot-frontendbucket-17nyngvktc0w"
}

variable "sam_artifacts_bucket_arn" {
  description = "SAM CLIがビルド成果物をアップロードするS3バケットのARN"
  type        = string
  default     = "arn:aws:s3:::aws-sam-cli-managed-default-samclisourcebucket-bv3bmkwlqsey"
}

variable "cloudfront_distribution_arn" {
  description = "フロントエンドを配信するCloudFrontディストリビューションのARN"
  type        = string
  default     = "arn:aws:cloudfront::533232489403:distribution/E1CKC1APSTP8PX"
}

variable "role_name" {
  description = "GitHub Actionsが引き受けるIAMロール名"
  type        = string
  default     = "github-actions-care-manual-chatbot-deploy-role"
}

variable "policy_name" {
  description = "IAMロールにアタッチするインラインポリシー名"
  type        = string
  default     = "github-actions-care-manual-chatbot-deploy-policy"
}
