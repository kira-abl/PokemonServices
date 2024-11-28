provider "aws" {
    region = "us-west-2"
}

resource "aws_instance" "logic" {
  ami           = "ami-055e3d4f0bbeb5878"
  instance_type = "t2.micro"
  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo yum install -y httpd
              sudo systemctl start httpd
              sudo systemctl enable httpd

              # Create HTML file
              echo '<!DOCTYPE html> <html> <body> <h1>Kira'"'"'s re/Start Project Work</h1> <p>EC2 Instance Challenge Lab</p> </body> </html>' | sudo tee /var/www/html/index.html

              # Give ec2-user write permissions to /var/www/html
              sudo chown -R ec2-user:apache /var/www/html
              sudo chmod 775 /var/www/html
  EOF

  # Ensure user data runs on every instance reboot
  user_data_replace_on_change = true
}
