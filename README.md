# Falcon's ISRO Hackathon Repository

Welcome to the Falcon's ISRO Hackathon project repository. This project involves predicting precipitation using an AI model based on NETCDF data provided by ISRO, recorded with C Doppler radar data. The repository includes the AI model, UI, accuracy, and visualization screenshots.

# Project Overview
This repository contains the following:
- **AI Model**: Predicts precipitation based on radar data.
- **NETCDF Data**: Radar data files provided by ISRO.
- **UI Screenshots**: Visualizations and model performance.
- **Accuracy Reports**: Screenshots showcasing the model's performance.

# Docker Setup

# Clone the Repository

```bash
git clone https://github.com/vishwajitsarnobat/isro_hackathon.git
```

This command fetches the Dockerfile and project files into your working directory.

### Build the Docker Image

```bash
sudo docker build -t isro_hackathon .
```

Builds the Docker image with the environment required to run the AI model and related programs.

> **Note**: If you encounter errors, ensure that Docker is running by executing:
> ```bash
> systemctl start docker
> ```

### Syncing Local Repo with Changes in GitHub Repo

#### Pull Latest Changes

```bash
git pull origin main
```

Updates your local repository with the latest changes from GitHub, including Dockerfile updates and project files.

#### Rebuild the Docker Image

```bash
sudo docker build -t isro_hackathon .
```

Rebuilds the Docker image to reflect any new changes in the environment and project files.

### Installing Additional Python Libraries or Packages via apt

1. **Modify the Dockerfile**:  
   Add any necessary commands to the `RUN` section for additional libraries or packages.
   > **Best Practice**: Use separate `RUN` instructions to optimize Docker's build cache and reduce unnecessary rebuilds.
   
2. **Rebuild the Docker Image**:
   ```bash
   sudo docker build -t isro_hackathon .
   ```

### Running the Container

#### Start the Docker Container

```bash
sudo docker run -it isro_hackathon
```

#### List Project Files

Once inside the container, list the project files:

```bash
ls
```

This will display all project files inside the container.

### Uploading Changes to GitHub Repo

1. **Add Changes**:
   ```bash
   git add .
   ```

2. **Commit Changes**:
   ```bash
   git commit -m "Commit message"
   ```

3. **Push Changes**:
   ```bash
   git push origin main
   ```

### Clearing Older Dangling Builds

To remove unused Docker images and free up space:

```bash
sudo docker image prune
```

## Project Features
- **AI Prediction Model**: Uses machine learning to predict precipitation.
- **Visualization**: Displays prediction accuracy and visualizes results.
- **Screenshots**: Contain UI, accuracy, and performance details.

## Technologies Used
- **Python**
- **Docker**
- **NETCDF**
- **ISRO C Doppler Radar Data**
