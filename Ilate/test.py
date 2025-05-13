import os 
from dotenv import load_dotenv

load_dotenv()


key = os.getenv("RAZORPAY_KEYS")
secret = os.getenv("RAZORPAY_SECRETS")

print(key)
print(secret)