#!/bin/bash

# Download SadTalker Models Script
echo "Downloading SadTalker models..."
echo "This may take a while as the models are large (several GB total)"

# Create checkpoints directory
mkdir -p SadTalker/checkpoints

# Download main models
echo "Downloading main models..."
cd SadTalker
bash scripts/download_models.sh

# Download additional required models
echo "Downloading additional required models..."
wget -nc https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2/epoch_20.pth -O ./checkpoints/epoch_20.pth
wget -nc https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2/auido2exp_00300-model.pth -O ./checkpoints/auido2exp_00300-model.pth
wget -nc https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2/auido2pose_00140-model.pth -O ./checkpoints/auido2pose_00140-model.pth
wget -nc https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2/facevid2vid_00189-model.pth.tar -O ./checkpoints/facevid2vid_00189-model.pth.tar
wget -nc https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2/shape_predictor_68_face_landmarks.dat -O ./checkpoints/shape_predictor_68_face_landmarks.dat

cd ..

echo "All models downloaded successfully!"
echo "You can now run 'make start' to start the application." 