# minimal app.py to test models import

try:
    from models import User, Farmer, Product, Customer, Transaction
    print("✅ Models imported successfully!")
except ImportError as e:
    print("❌ ImportError:", e)

# Optional: print class names to double-check
print("Available classes in models.py:")
print(" -", User)
print(" -", Farmer)
print(" -", Product)
print(" -", Customer)
print(" -", Transaction)
