provider "aws" {}

data "aws_region" "current" {
    provider = aws
}

variable "name-cluster1" {
  description = "Name of created cluster 1"
  type        = string
  default     = "test-cluster1"
}

variable "name-cluster2" {
  description = "Name of created cluster 2"
  type        = string
  default     = "test-cluster2"
}

module "eks-cluster1" {
  source = "./eks-cluster"
  region = "${data.aws_region.current.name}"
  name = "${var.name-cluster1}"
}

module "eks-cluster2" {
  source = "./eks-cluster"
  region = "${data.aws_region.current.name}"
  name = "${var.name-cluster2}"
}