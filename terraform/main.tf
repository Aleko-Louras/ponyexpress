# -------------------------------------------------------
# terraform/main.tf — Pony Express Infrastructure
# Creates: VPC, Subnet, Security Group, EC2, ECR, IAM
# State stored in S3 so GitHub Actions can run this
# -------------------------------------------------------

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state — allows GitHub Actions to run terraform
  # Create this S3 bucket manually once before anything else:
  # aws s3 mb s3://ponyexpress-terraform-state
  backend "s3" {
    bucket = "ponyexpress-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# -------------------------------------------------------
# VARIABLES
# -------------------------------------------------------

variable "aws_region" {
  default = "us-east-1"
}

variable "app_name" {
  default = "ponyexpress"
}

variable "my_ip" {
  description = "Your IP for SSH access (x.x.x.x/32)"
  type        = string
}

# -------------------------------------------------------
# VPC — isolated network for the app
# -------------------------------------------------------

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = { Name = "${var.app_name}-vpc" }
}

# Public subnet — where EC2 lives
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true   # EC2 gets a public IP automatically
  availability_zone       = "${var.aws_region}a"

  tags = { Name = "${var.app_name}-public-subnet" }
}

# Internet gateway — allows traffic in/out of VPC
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.app_name}-igw" }
}

# Route table — sends internet traffic through the gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = { Name = "${var.app_name}-rt" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# -------------------------------------------------------
# SECURITY GROUP — firewall rules (least privilege)
# -------------------------------------------------------

resource "aws_security_group" "app_sg" {
  name   = "${var.app_name}-sg"
  vpc_id = aws_vpc.main.id

  # SSH — your IP only
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "SSH from developer IP only"
  }

  # React frontend — public
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP public"
  }

  # FastAPI backend — public
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "FastAPI public"
  }

  # All outbound allowed (for package installs, ECR pulls)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.app_name}-sg" }
}

# -------------------------------------------------------
# IAM — least privilege role for EC2 to pull from ECR
# -------------------------------------------------------

resource "aws_iam_role" "ec2_role" {
  name = "${var.app_name}-ec2-role"

  # Trust policy: only EC2 can assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

# Attach read-only ECR access — EC2 can pull images but not push
resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Instance profile wraps the role so EC2 can use it
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.app_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# -------------------------------------------------------
# ECR REPOSITORIES — one per service
# -------------------------------------------------------

resource "aws_ecr_repository" "frontend" {
  name                 = "${var.app_name}-frontend"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_repository" "backend" {
  name                 = "${var.app_name}-backend"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
}

# -------------------------------------------------------
# EC2 INSTANCE
# -------------------------------------------------------

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  key_name               = "${var.app_name}-key"   # Create in AWS Console first

  # Ansible will handle Docker install — this just installs Python for Ansible
  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y python3
  EOF

  tags = { Name = "${var.app_name}-server" }
}

# -------------------------------------------------------
# OUTPUTS — used by GitHub Actions and Ansible
# -------------------------------------------------------

output "ec2_public_ip" {
  value = aws_instance.app.public_ip
}

output "frontend_ecr_url" {
  value = aws_ecr_repository.frontend.repository_url
}

output "backend_ecr_url" {
  value = aws_ecr_repository.backend.repository_url
}

output "vpc_id" {
  value = aws_vpc.main.id
}
