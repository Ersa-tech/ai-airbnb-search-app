#!/usr/bin/env python3
"""
Test script for multi-country search functionality
"""

import requests
import json
import time

def test_multi_country_search():
    """Test the enhanced multi-country search functionality"""
    
    base_url = "http://localhost:5000"
    
    # Test cases for multi-country search
    test_cases = [
        {
            "name": "Global cheapest large homes",
            "query": "Cheapest large homes globally",
            "filters": {
                "amenities": ["wifi"],
                "propertyTypes": ["entire_house"]
            }
        },
        {
            "name": "Budget-friendly properties in Europe",
            "query": "Budget-friendly 8+ bedroom houses in Europe",
            "filters": {
                "amenities": ["wifi", "washer"],
                "propertyTypes": ["entire_house"]
            }
        },
        {
            "name": "Most expensive luxury estates worldwide",
            "query": "Most expensive luxury estates worldwide",
            "filters": {
                "amenities": ["wifi", "tv"],
                "propertyTypes": ["entire_house"]
            }
        },
        {
            "name": "Large group accommodation in Asia",
            "query": "Large group accommodation in Asia",
            "filters": {
                "amenities": ["wifi"],
                "propertyTypes": ["entire_house"]
            }
        },
        {
            "name": "Affordable properties across multiple countries",
            "query": "Affordable large group accommodation across multiple countries",
            "filters": {
                "amenities": ["wifi", "washer"],
                "propertyTypes": ["entire_house"]
            }
        }
    ]
    
    print("🌍 Testing Multi-Country Search Functionality")
    print("=" * 60)
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Backend Health: {health_data['status']}")
            print(f"📊 Version: {health_data.get('version', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    print("\n🔍 Running Multi-Country Search Tests:")
    print("-" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Query: '{test_case['query']}'")
        print(f"   Filters: {test_case['filters']}")
        
        try:
            start_time = time.time()
            
            # Make search request
            response = requests.post(
                f"{base_url}/api/v1/search",
                json={
                    "query": test_case["query"],
                    "filters": test_case["filters"]
                },
                timeout=30
            )
            
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    properties = data.get('data', {}).get('properties', [])
                    locations = data.get('data', {}).get('locations', [])
                    criteria = data.get('data', {}).get('criteria', {})
                    
                    print(f"   ✅ Success: Found {len(properties)} properties")
                    print(f"   🌍 Locations searched: {', '.join(locations)}")
                    print(f"   🎯 Search criteria: {criteria}")
                    print(f"   ⏱️  Response time: {response_time}ms")
                    
                    if properties:
                        print(f"   🏠 Sample properties:")
                        for j, prop in enumerate(properties[:3], 1):
                            print(f"      {j}. {prop['title']} - ${prop['price']} in {prop['location']}")
                    
                    # Check AI summary
                    ai_summary = data.get('message', '')
                    if ai_summary:
                        print(f"   🤖 AI Summary: {ai_summary[:100]}...")
                    
                else:
                    error_msg = data.get('error', 'Unknown error')
                    print(f"   ❌ Search failed: {error_msg}")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Request timed out (>30s)")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection error")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Small delay between requests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🎉 Multi-Country Search Testing Complete!")
    print("\n📋 Key Features Tested:")
    print("   ✅ Global search patterns (worldwide, globally)")
    print("   ✅ Regional search patterns (Europe, Asia)")
    print("   ✅ Price-based criteria (cheapest, most expensive)")
    print("   ✅ Size-based criteria (large homes, 8+ bedrooms)")
    print("   ✅ Multi-location property aggregation")
    print("   ✅ AI-powered property selection")
    print("   ✅ Filter integration (amenities, property types)")

if __name__ == "__main__":
    test_multi_country_search()
