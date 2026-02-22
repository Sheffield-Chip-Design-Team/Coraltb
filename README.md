# Coraltb 

## Cloning and Installing the Coraltb Package (Editable Mode)
Follow the steps below to clone this repository and install the package in editable mode for development.

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/your-repo.git](https://github.com/Sheffield-Chip-Design-Team/Coraltb.git) Coraltb
cd Coraltb
```

### 2. Create and activate a virtual environment
```
python3 -m venv .env
source .env/bin/activate        # Linux / macOS
```
or for Windows...
```
.\.env\Scripts\activate         # Windows
```

### 3. Install the package as editable
```bash
git checkout -b dev
pip install -e .
```

### 4 Run the help command
```bash
coral -h
```
