# Official Falcon's ISRO Hackathon Repository

Welcome to the Falcon's ISRO Hackathon project repository. This document outlines the steps to set up, sync, and manage the project using Docker and Git.

## Initial Setup

1. **Clone the Repository**
    ```bash
    git clone https://github.com/vishwajitsarnobat/isro_hackathon.git
    ```
    This command fetches the Dockerfile and project files into your working directory.

2. **Build the Docker Image**
    ```bash
    sudo docker build -t isro_hackathon .
    ```
    Builds the Docker image with the common environment required to run the programs.

    - **Note:** If you encounter errors, ensure that Docker is running by executing:
      ```bash
      systemctl start docker
      ```

## Syncing Local Repo with Changes in GitHub Repo

1. **Pull Latest Changes**
    ```bash
    git pull origin main
    ```
    Updates your local repository with the latest changes from GitHub, including the Dockerfile and project files.

2. **Rebuild the Docker Image**
    ```bash
    sudo docker build -t isro_hackathon .
    ```
    Rebuilds the Docker image to reflect the latest changes in the environment and project files.

## Importing Python Libraries or Installing Packages via `apt`

1. **Modify the Dockerfile**
    - Open the Dockerfile and add the necessary commands to the `RUN` section for new libraries or packages.
    - **Best Practice:** Use separate `RUN` instructions to optimize Docker's build cache and reduce unnecessary rebuilds. If you need assistance, consult resources or seek help.

2. **Rebuild the Docker Image**
    ```bash
    sudo docker build -t isro_hackathon .
    ```
    Rebuilds the Docker image with the updated Dockerfile.

## Uploading Changes to GitHub Repo

1. **Add Changes**
    ```bash
    git add .
    ```

2. **Commit Changes**
    ```bash
    git commit -m "Commit message"
    ```

3. **Push Changes**
    ```bash
    git push origin main
    ```

## Running the Container

1. **Start the Docker Container**
    ```bash
    sudo docker run -it isro_hackathon
    ```

2. **List Project Files**
    ```bash
    ls
    ```
    Lists the project files inside the container.

## Clearing Older Dangling Builds

To remove unused Docker images and free up space:
```bash
sudo docker image prune
```


