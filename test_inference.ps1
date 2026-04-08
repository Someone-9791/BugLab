$env:API_BASE_URL = "http://test.example.com/v1"
$env:API_KEY = "test-key-12345"
$env:MODEL_NAME = "test-model"

cd D:\Projects\MetaOpenEnv
python inference.py 2>&1
