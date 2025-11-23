from app.main import app

print("\n=== REGISTERED ROUTES ===")
for route in app.routes:
    route_type = "Unknown"
    if hasattr(route, "methods"):
        route_type = str(route.methods)
    elif "websocket" in str(type(route)).lower():
        route_type = "WebSocket"
    print(f"{route.path} - {route_type}")
