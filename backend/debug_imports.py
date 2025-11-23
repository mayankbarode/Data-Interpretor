import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("Attempting to import app.main...")
try:
    from app.main import app
    print("Successfully imported app.main")
except Exception as e:
    print(f"Failed to import app.main: {e}")
    import traceback
    traceback.print_exc()

print("\nAttempting to import app.api.endpoints...")
try:
    from app.api import endpoints
    print("Successfully imported app.api.endpoints")
except Exception as e:
    print(f"Failed to import app.api.endpoints: {e}")
    import traceback
    traceback.print_exc()

print("\nChecking session_store identity...")
try:
    from app.api.endpoints import session_store as s1
    import app.main
    # We need to access session_store from main if it was imported there, 
    # but main imports it from endpoints, so it should be the same object.
    # Let's check if we can modify it in endpoints and see it in main's import
    s1["test"] = "value"
    from app.api.endpoints import session_store as s2
    print(f"Session store identity check: {s1 is s2}")
    print(f"Session store content: {s2}")
except Exception as e:
    print(f"Failed session store check: {e}")
