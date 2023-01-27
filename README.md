# Script for testing writing disk performance
## Usage
```
Usage: ./ddtest.py min_free_space (MB) file_size (MB) file_count. F.e. 5000 100 10
```
## Installations
```
pip install -r requirements.txt
```

## Use case
Testings for writing disk performance with 5000MB data and 10 threads.
```
python ./ddtest.py 60000 5000 10
```