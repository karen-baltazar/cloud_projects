#!/bin/bash

# Get the user profile path
PROFILE_PATH=$(python -c "import os; print(os.path.expanduser('~').replace('\\\\', '/'))")

# Step 1: Run aws_setup.py to configure the AWS cluster and get the load balancer DNS
echo "Step 1: Configuring AWS cluster..."
output=$(python aws_setup.py "$@")
export EC2_URL=$output

# Step 2: Build the Docker image
echo "Step 2: Building Docker image..."
docker build -t tp1-app .

# Step 3: Run benchmarking.py in a Docker container and get container id
echo "Step 3: Running benchmarking..."
docker run -e EC2_URL -v $PROFILE_PATH/.aws:/root/.aws tp1-app
container_id=$(docker ps -lq)

# Step 4: Wait for the Docker container to finish
echo "Step 4: Waiting for the Docker container to finish..."
docker wait $container_id

# Step 5: Copy the output folder from the Docker container to the local machine
echo "Step 5: Copying output folder to local machine..."

docker cp $container_id:/app/output $PROFILE_PATH/Downloads

echo "Automation script completed!"
