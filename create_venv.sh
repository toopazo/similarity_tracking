#!/bin/bash

# deactivate
# echo "Activating virtual environment"
# source venv/bin/activate
# which python
# python --version

# Remove previous venv
echo "Checking for existing venv directory"
if [ -d "venv/" ] 
then
    echo "A previous venv directory exists, we will remove it" 
    
    # Deactivate venv
    if [[ "$VIRTUAL_ENV" != "" ]]
    then
        echo "The venv is active, we will deactivate it"
        deactivate
    else
        echo "The venv is not active, no need to deactivate it"
    fi
    
    # Remove
    rm -rf venv
else
    echo "No venv directory exists"
fi  

# Create new venv
if [[ $EUID -ne 0 ]]
then
    echo "Running as non-root user"
    
    python3 -m venv venv
    source venv/bin/activate
else
    echo "Running as root user"

    apt install build-essential -y
    apt install python3.10-venv -y
    apt install python3.10-dev -y  

    python3.10 -m venv /venv
    source /venv/bin/activate  
fi

pip install --upgrade pip
pip install --upgrade pylint
pip install --upgrade black
pip install --upgrade flake8
pip install --upgrade isort
pip install --upgrade pipreqs

pip install python-dotenv
pip install boto3
pip install tqdm
pip install pandas
pip install openpyxl
pip install wandb
pip install rclone-python

# Other custom installations
pip install torch torchvision torchaudio
pip install -U openmim
mim install mmcv
python -c 'import torch;print(torch.__version__);print(torch.version.cuda)'

pip install PyQt5
pip install munkres

echo "-----------------------------"
echo "Writing requirements.txt file"
pipreqs --force

# . ./create_venv.sh --strategy exito_prodet