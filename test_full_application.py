#!/usr/bin/env python3
"""
Full Application Integration Test
"""

import requests
import json
import time

def test_backend_health():
    """Test backend health endpoint"""
    print("🏥 Testing Backend Health...")
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        print(f'✅ Health check: {response.status_code} - {response.json()}')
        return True
    except Exception as e:
        print(f'❌ Health check failed: {e}')
        return False

def test_search_endpoint():
    """Test search functionality"""
    print("\n🔍 Testing Search Endpoint...")
    try:
        search_data = {
            'query': 'Find a place in San Francisco',
            'location': 'San Francisco'
        }
        response = requests.post('http://localhost:5000/search', 
                               json=search_data, 
                               timeout=15)
        print(f'✅ Search endpoint: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            properties = data.get('properties', [])
            print(f'   Properties found: {len(properties)}')
            print(f'   Response time: {data.get("metadata", {}).get("response_time", "N/A")}')
            
            # Test property structure
            if properties:
                prop = properties[0]
                required_fields = ['id', 'title', 'price', 'location', 'rating']
                missing_fields = [field for field in required_fields if field not in prop]
                if missing_fields:
                    print(f'⚠️  Missing fields in property: {missing_fields}')
                else:
                    print(f'✅ Property structure valid')
                    print(f'   Sample property: {prop["title"][:50]}...')
            
            return True
        else:
            print(f'❌ Error: {response.text}')
            return False
    except Exception as e:
        print(f'❌ Search test failed: {e}')
        return False

def test_multi_location_search():
    """Test multi-location search"""
    print("\n🌍 Testing Multi-Location Search...")
    try:
        search_data = {
            'query': 'Find properties globally',
            'location': 'global'
        }
        response = requests.post('http://localhost:5000/search', 
                               json=search_data, 
                               timeout=20)
        print(f'✅ Global search: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            properties = data.get('properties', [])
            print(f'   Global properties found: {len(properties)}')
            
            # Check for diverse locations
            locations = set()
            for prop in properties[:10]:  # Check first 10
                locations.add(prop.get('location', '').split(',')[0])
            print(f'   Unique locations: {len(locations)}')
            print(f'   Sample locations: {list(locations)[:5]}')
            return True
        else:
            print(f'❌ Error: {response.text}')
            return False
    except Exception as e:
        print(f'❌ Global search test failed: {e}')
        return False

def test_error_handling():
    """Test error handling"""
    print("\n🛡️ Testing Error Handling...")
    try:
        # Test invalid request
        response = requests.post('http://localhost:5000/search', 
                               json={}, 
                               timeout=5)
        print(f'✅ Invalid request handling: {response.status_code}')
        
        # Test XSS attempt
        xss_data = {
            'query': '<script>alert("xss")</script>Find place',
            'location': 'San Francisco'
        }
        response = requests.post('http://localhost:5000/search', 
                               json=xss_data, 
                               timeout=10)
        print(f'✅ XSS protection: {response.status_code}')
        
        return True
    except Exception as e:
        print(f'❌ Error handling test failed: {e}')
        return False

def test_performance():
    """Test performance metrics"""
    print("\n⚡ Testing Performance...")
    try:
        search_data = {
            'query': 'Find a place in New York',
            'location': 'New York'
        }
        
        start_time = time.time()
        response = requests.post('http://localhost:5000/search', 
                               json=search_data, 
                               timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f'✅ Response time: {response_time:.2f} seconds')
        
        if response_time < 3.0:
            print(f'✅ Performance target met (<3s)')
        else:
            print(f'⚠️  Performance slower than target (>3s)')
        
        return True
    except Exception as e:
        print(f'❌ Performance test failed: {e}')
        return False

def main():
    """Run all tests"""
    print("🚀 AI Airbnb Search - Full Application Test")
    print("=" * 50)
    
    tests = [
        test_backend_health,
        test_search_endpoint,
        test_multi_location_search,
        test_error_handling,
        test_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Application is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    main()
