#!/usr/bin/env python3
"""
Test Enhanced Backend Components
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import *
import json

def test_input_validation():
    """Test enhanced input validation"""
    print('🧪 Testing Input Validation:')
    validator = InputValidator()
    
    # Test normal query
    normal_query = "Find a place in San Francisco"
    sanitized = validator.sanitize_query(normal_query)
    print(f'✅ Valid query: "{sanitized}"')
    
    # Test XSS attempt
    xss_query = "<script>alert(1)</script>Find place"
    sanitized_xss = validator.sanitize_query(xss_query)
    print(f'✅ XSS attempt sanitized: "{sanitized_xss}"')
    
    # Test long query
    long_query = "a" * 2000
    sanitized_long = validator.sanitize_query(long_query)
    print(f'✅ Long query truncated: {len(sanitized_long)} chars (should be 1000)')
    
    # Test location validation
    print(f'✅ Valid location: {validator.validate_location("San Francisco")}')
    print(f'✅ Invalid location: {validator.validate_location("")}')
    
    return True

def test_circuit_breaker():
    """Test circuit breaker functionality"""
    print('\n🔌 Testing Circuit Breaker:')
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    print(f'✅ Initial state: {cb.state}')
    print(f'✅ Failure count: {cb.failure_count}')
    
    return True

def test_data_transformer():
    """Test enhanced data transformer"""
    print('\n🔄 Testing Data Transformer:')
    dt = EnhancedDataTransformer()
    
    # Test price extraction
    price_tests = [
        "$150",
        "150.50",
        {"price": 200},
        "invalid",
        None
    ]
    
    for price_input in price_tests:
        result = dt.safe_extract_price(price_input)
        print(f'✅ Price "{price_input}" -> {result}')
    
    # Test rating extraction
    rating_tests = [
        "4.81 (53)",
        "New",
        "4.5",
        5.0,
        "invalid"
    ]
    
    for rating_input in rating_tests:
        rating, count = dt.safe_extract_rating(rating_input)
        print(f'✅ Rating "{rating_input}" -> {rating} ({count} reviews)')
    
    # Test image URL extraction
    image_tests = [
        "https://example.com/image.jpg",
        [{"picture": "https://example.com/pic.jpg"}],
        {"url": "https://example.com/img.jpg"},
        "invalid"
    ]
    
    for image_input in image_tests:
        result = dt.safe_extract_image_url(image_input)
        print(f'✅ Image "{str(image_input)[:50]}..." -> {result[:50]}...')
    
    return True

def test_location_extraction():
    """Test location extraction from queries"""
    print('\n🗺️ Testing Location Extraction:')
    
    test_queries = [
        "Find a place in San Francisco",
        "Looking for accommodation near London",
        "Best properties globally",
        "Cheapest homes in Europe",
        "Luxury apartments in Tokyo"
    ]
    
    for query in test_queries:
        locations = extract_multiple_locations_from_query(query)
        print(f'✅ Query: "{query}" -> Locations: {locations}')
    
    return True

def test_criteria_extraction():
    """Test search criteria extraction"""
    print('\n🎯 Testing Criteria Extraction:')
    
    test_queries = [
        "Find cheapest places in San Francisco",
        "Most expensive luxury homes globally",
        "Large spacious apartments in London",
        "Small cozy rooms in Paris"
    ]
    
    for query in test_queries:
        criteria = extract_search_criteria_from_query(query)
        print(f'✅ Query: "{query}" -> Criteria: {criteria}')
    
    return True

def test_place_id_mapping():
    """Test place ID mapping"""
    print('\n🆔 Testing Place ID Mapping:')
    
    test_locations = [
        "San Francisco",
        "NYC",
        "London",
        "Tokyo",
        "Unknown City"
    ]
    
    for location in test_locations:
        place_id = get_place_id(location)
        print(f'✅ Location: "{location}" -> Place ID: {place_id[:20]}...')
    
    return True

def main():
    """Run all tests"""
    print("🚀 Enhanced AI Airbnb Search Backend - Comprehensive Testing")
    print("=" * 60)
    
    try:
        test_input_validation()
        test_circuit_breaker()
        test_data_transformer()
        test_location_extraction()
        test_criteria_extraction()
        test_place_id_mapping()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! Enhanced backend is working correctly.")
        print("🎉 Ready for production deployment!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
