#!/usr/bin/env python3
"""
Debug the mock car repository to see what's happening
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.persistence.mock_car_repository import MockCarRepository

async def debug_mock_cars():
    """Debug mock car repository"""
    try:
        print("🔧 Creating MockCarRepository...")
        repo = MockCarRepository()
        
        print(f"📊 Cars in mock repo: {len(repo._cars)}")
        
        # Test list cars
        print("\n📋 Testing list cars...")
        result = await repo.list(page=1, limit=5)
        
        print(f"✅ List result keys: {list(result.keys())}")
        print(f"📊 Cars returned: {len(result.get('cars', []))}")
        print(f"📊 Total: {result.get('total', 0)}")
        
        if result.get('cars'):
            first_car = result['cars'][0]
            print(f"\n🚗 First car:")
            print(f"  ID: {first_car.get('id')}")
            print(f"  Make: {first_car.get('make')}")
            print(f"  Model: {first_car.get('model')}")
            print(f"  Status: {first_car.get('status')}")
        
        print("\n🎉 Mock repository test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_mock_cars())
    sys.exit(0 if success else 1)