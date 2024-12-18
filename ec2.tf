// Configuring the provider information
provider "aws" {
    region = "us-west-2"
    shared_credentials_files = ["/home/kira/.aws/credentials"]

}

// Creating the EC2 private key
variable "key_name" {
  default = "Pokemon"
}

resource "tls_private_key" "ec2_private_key" {
  algorithm = "RSA"
  rsa_bits  = 4096

  provisioner "local-exec" {
        command = "echo '${tls_private_key.ec2_private_key.private_key_pem}' > /home/kira/Desktop/${var.key_name}.pem"
    }
}

// Making the access of .pem key as a private
resource "null_resource" "key-perm" {
    depends_on = [
        tls_private_key.ec2_private_key,
    ]

    provisioner "local-exec" {
        command = "chmod 600 /home/kira/Desktop/${var.key_name}.pem"
    }
}

module "key_pair" {
  source = "terraform-aws-modules/key-pair/aws"
  key_name   = "Pokemon"
  public_key = tls_private_key.ec2_private_key.public_key_openssh
}

// Creating aws security resource
resource "aws_security_group" "allow_tcp" {
  name        = "allow_tcp1"
  description = "Allow TCP inbound traffic"


  ingress {
    description = "TCP from VPC"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
   ingress {
    description = "SSH from VPC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_tcp1"
  }
}

// Launching the CRUD instance
resource "aws_instance" "CRUD" {
    ami = "ami-055e3d4f0bbeb5878"
    instance_type = "t2.micro"
    key_name = var.key_name
    vpc_security_group_ids = ["${aws_security_group.allow_tcp.id}"]
    tags = {
        Name = "CRUD_API"
        }
    depends_on = [module.key_pair]
}

// Launching the LogicAPI instance
resource "aws_instance" "logicAPI" {
    ami = "ami-055e3d4f0bbeb5878"
    instance_type = "t2.micro"
    key_name = var.key_name
    vpc_security_group_ids = ["${aws_security_group.allow_tcp.id}"]
    tags = {
        Name = "logic_API"
        }
    depends_on = [module.key_pair, aws_instance.CRUD]
    provisioner "local-exec" {
    command = <<EOT
    # Create a temporary inventory file dynamically
    echo "[web_servers]" > /tmp/ansible_inventory
    echo "CRUD ansible_host=${aws_instance.CRUD.public_ip}" >> /tmp/ansible_inventory
    echo "logicAPI ansible_host=${aws_instance.logicAPI.public_ip}" >> /tmp/ansible_inventory

     # Log the inventory file to confirm it was created properly
    cat /tmp/ansible_inventory  # This will output the content to Terraform logs
    
    # Run Docker Compose and pass the first instance IP as an environment variable
    ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -u ec2-user --private-key /home/kira/Desktop/${var.key_name}.pem -i /tmp/ansible_inventory master.yml -e "CRUD_IP=${aws_instance.CRUD.public_ip}"
    EOT
  }
  
}







