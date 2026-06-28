terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ---------------------------------------------------------------------------
# GitHub Actions用OIDCプロバイダ（auto-blogで作成済みのものを参照）
#
# 同一AWSアカウントにOIDCプロバイダは1つしか作れないため、
# auto-blogのTerraformが作成したプロバイダをARNで直接参照する。
# ---------------------------------------------------------------------------
locals {
  github_oidc_provider_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
}

# ---------------------------------------------------------------------------
# IAMロール: mainブランチへのpushのみ引き受けを許可
# ---------------------------------------------------------------------------
data "aws_iam_policy_document" "github_actions_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [local.github_oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_org}/${var.github_repo}:ref:refs/heads/${var.github_branch}"]
    }
  }
}

resource "aws_iam_role" "github_actions_deploy" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.github_actions_trust.json
}

# ---------------------------------------------------------------------------
# 権限ポリシー
# ---------------------------------------------------------------------------
data "aws_iam_policy_document" "github_actions_deploy" {

  # フロントエンドS3バケット（同期操作）
  statement {
    sid     = "S3FrontendBucketLevel"
    effect  = "Allow"
    actions = ["s3:ListBucket", "s3:GetBucketLocation"]
    resources = [var.s3_frontend_bucket_arn]
  }

  statement {
    sid     = "S3FrontendObjectLevel"
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${var.s3_frontend_bucket_arn}/*"]
  }

  # SAM CLIアーティファクト用S3バケット（sam buildの成果物アップロード）
  statement {
    sid     = "S3SAMArtifactsBucketLevel"
    effect  = "Allow"
    actions = ["s3:ListBucket", "s3:GetBucketLocation"]
    resources = [var.sam_artifacts_bucket_arn]
  }

  statement {
    sid     = "S3SAMArtifactsObjectLevel"
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${var.sam_artifacts_bucket_arn}/*"]
  }

  # CloudFrontキャッシュ無効化
  statement {
    sid    = "CloudFrontInvalidation"
    effect = "Allow"
    actions = [
      "cloudfront:CreateInvalidation",
      "cloudfront:GetInvalidation",
      "cloudfront:ListInvalidations",
    ]
    resources = [var.cloudfront_distribution_arn]
  }

  # CloudFormation（sam deploy + スタック出力取得）
  # sam deployが内部で呼び出すアクションが多岐にわたるため、
  # 対象スタック2つにスコープを絞った上でcloudformation:*を許可する
  statement {
    sid     = "CloudFormationStackOps"
    effect  = "Allow"
    actions = ["cloudformation:*"]
    resources = [
      # アプリ本体スタック
      "arn:aws:cloudformation:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:stack/${var.stack_name}/*",
      # SAM CLIが内部管理するS3バケット用スタック
      "arn:aws:cloudformation:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:stack/aws-sam-cli-managed-default/*",
    ]
  }

  # cloudformation:ValidateTemplate / GetTemplateSummary は resource: * が必要
  statement {
    sid     = "CloudFormationGlobal"
    effect  = "Allow"
    actions = ["cloudformation:ValidateTemplate", "cloudformation:GetTemplateSummary"]
    resources = ["*"]
  }

  # Lambda関数の更新
  statement {
    sid    = "LambdaFunctionOps"
    effect = "Allow"
    actions = [
      "lambda:GetFunction",
      "lambda:GetFunctionConfiguration",
      "lambda:CreateFunction",
      "lambda:UpdateFunctionCode",
      "lambda:UpdateFunctionConfiguration",
      "lambda:DeleteFunction",
      "lambda:AddPermission",
      "lambda:RemovePermission",
    ]
    resources = [
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.stack_name}-*",
    ]
  }

  # SAMがLambda実行ロールを作成するためのIAM操作（CAPABILITY_IAM）
  statement {
    sid    = "IAMRoleOpsForSAM"
    effect = "Allow"
    actions = [
      "iam:GetRole",
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:PassRole",
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
      "iam:PutRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:GetRolePolicy",
    ]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.stack_name}-*",
    ]
  }

  # API Gateway HTTP API
  statement {
    sid    = "ApiGatewayOps"
    effect = "Allow"
    actions = [
      "apigateway:GET",
      "apigateway:POST",
      "apigateway:PUT",
      "apigateway:PATCH",
      "apigateway:DELETE",
    ]
    resources = [
      "arn:aws:apigateway:${data.aws_region.current.name}::/*",
    ]
  }
}

resource "aws_iam_role_policy" "github_actions_deploy" {
  name   = var.policy_name
  role   = aws_iam_role.github_actions_deploy.id
  policy = data.aws_iam_policy_document.github_actions_deploy.json
}
