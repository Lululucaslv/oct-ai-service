try:
    from power_generation_duration_tool import create_power_generation_duration_tool
    print("✅ power_generation_duration_tool import successful")
    
    from electricity_price_tool import create_electricity_price_tool
    print("✅ electricity_price_tool import successful")
    
    from main import app
    print("✅ main.py import successful")
    
    print("All imports working correctly!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
