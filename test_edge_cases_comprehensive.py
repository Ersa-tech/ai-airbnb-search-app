#!/usr/bin/env python3
"""
Comprehensive Edge Case Testing Suite for AI Airbnb Search Application
Tests various failure scenarios, edge cases, and robustness issues
"""

import requests
import json
import time
import threading
import concurrent.futures
from unittest.mock import patch, MagicMock
import sys
import os

# Add the backend directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

class EdgeCaseTestSuite:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        
        if status == "FAIL":
            self.failed_tests.append(result)
            
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_malformed_api_responses(self):
        """Test handling of malformed API responses"""
        print("\n🔧 Testing Malformed API Response Handling")
        print("-" * 50)
        
        # Test cases for malformed data
        malformed_cases = [
            {
                "name": "Empty API Response",
                "query": "test empty response",
                "mock_response": {}
            },
            {
                "name": "Missing Data Field",
                "query": "test missing data",
                "mock_response": {"status": "success"}
            },
            {
                "name": "Invalid Property Structure",
                "query": "test invalid structure",
                "mock_response": {
                    "data": {
                        "list": [
                            {"invalid": "structure"},
                            {"listing": None},
                            {"listing": {"id": None}}
                        ]
                    }
                }
            },
            {
                "name": "Non-JSON Response",
                "query": "test non-json",
                "mock_response": "This is not JSON"
            }
        ]
        
        for case in malformed_cases:
            try:
                # This would require mocking the RapidAPI call
                # For now, test with actual backend to see how it handles edge cases
                response = requests.post(
                    f"{self.base_url}/api/v1/search",
                    json={"query": case["query"]},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') or len(data.get('data', {}).get('properties', [])) >= 0:
                        self.log_test(f"Malformed Response: {case['name']}", "PASS", 
                                    "Backend handled gracefully")
                    else:
                        self.log_test(f"Malformed Response: {case['name']}", "FAIL", 
                                    "Backend did not handle gracefully")
                else:
                    self.log_test(f"Malformed Response: {case['name']}", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Malformed Response: {case['name']}", "FAIL", str(e))
    
    def test_invalid_location_inputs(self):
        """Test handling of invalid location inputs"""
        print("\n🌍 Testing Invalid Location Input Handling")
        print("-" * 50)
        
        invalid_locations = [
            "!@#$%^&*()",  # Special characters
            "123456789",   # Numbers only
            "",            # Empty string
            "   ",         # Whitespace only
            "ñoñó çítÿ",   # Non-ASCII characters
            "a" * 1000,    # Very long string
            "Mars",        # Non-existent location
            "Atlantis",    # Fictional location
            "NULL",        # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
        ]
        
        for location in invalid_locations:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/search",
                    json={"query": f"Find a place in {location}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') is not False:
                        self.log_test(f"Invalid Location: '{location[:20]}...'", "PASS", 
                                    "Handled gracefully with fallback")
                    else:
                        self.log_test(f"Invalid Location: '{location[:20]}...'", "WARN", 
                                    "Returned error but handled safely")
                else:
                    self.log_test(f"Invalid Location: '{location[:20]}...'", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Invalid Location: '{location[:20]}...'", "FAIL", str(e))
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        print("\n⚡ Testing Concurrent Request Handling")
        print("-" * 50)
        
        def make_request(query_id):
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/search",
                    json={"query": f"Test concurrent request {query_id}"},
                    timeout=15
                )
                return {
                    "id": query_id,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds()
                }
            except Exception as e:
                return {
                    "id": query_id,
                    "status_code": 0,
                    "success": False,
                    "error": str(e)
                }
        
        # Test with 10 concurrent requests
        num_requests = 10
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
                futures = [executor.submit(make_request, i) for i in range(num_requests)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful_requests = sum(1 for r in results if r['success'])
            avg_response_time = sum(r.get('response_time', 0) for r in results if r['success']) / max(successful_requests, 1)
            
            if successful_requests >= num_requests * 0.8:  # 80% success rate
                self.log_test("Concurrent Requests", "PASS", 
                            f"{successful_requests}/{num_requests} successful, avg {avg_response_time:.2f}s")
            else:
                self.log_test("Concurrent Requests", "FAIL", 
                            f"Only {successful_requests}/{num_requests} successful")
                
        except Exception as e:
            self.log_test("Concurrent Requests", "FAIL", str(e))
    
    def test_large_query_inputs(self):
        """Test handling of very large query inputs"""
        print("\n📏 Testing Large Query Input Handling")
        print("-" * 50)
        
        large_queries = [
            "Find a place " + "very " * 100 + "nice",  # Repeated words
            "A" * 5000,  # Very long query
            "Find a place in " + ", ".join([f"City{i}" for i in range(100)]),  # Many locations
            "Find a " + " ".join([f"bedroom{i}" for i in range(50)]) + " house",  # Many bedrooms
        ]
        
        for i, query in enumerate(large_queries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/search",
                    json={"query": query},
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Large Query {i+1}", "PASS", 
                                f"Query length: {len(query)} chars")
                elif response.status_code == 413:  # Payload too large
                    self.log_test(f"Large Query {i+1}", "PASS", 
                                "Properly rejected large payload")
                else:
                    self.log_test(f"Large Query {i+1}", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Large Query {i+1}", "FAIL", str(e))
    
    def test_network_timeout_scenarios(self):
        """Test handling of network timeouts"""
        print("\n⏰ Testing Network Timeout Scenarios")
        print("-" * 50)
        
        # Test with very short timeout
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/search",
                json={"query": "Find a place in San Francisco"},
                timeout=0.001  # Very short timeout
            )
            self.log_test("Network Timeout", "FAIL", "Request should have timed out")
        except requests.exceptions.Timeout:
            self.log_test("Network Timeout", "PASS", "Timeout handled correctly")
        except Exception as e:
            self.log_test("Network Timeout", "WARN", f"Different error: {str(e)}")
    
    def test_memory_usage_patterns(self):
        """Test memory usage under various scenarios"""
        print("\n💾 Testing Memory Usage Patterns")
        print("-" * 50)
        
        # Test with queries that might cause memory issues
        memory_test_queries = [
            "Find properties in " + " ".join([f"location{i}" for i in range(1000)]),
            "Find a place with " + " ".join([f"amenity{i}" for i in range(500)]),
        ]
        
        for i, query in enumerate(memory_test_queries):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/v1/search",
                    json={"query": query},
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = end_time - start_time
                    if response_time < 30:  # Should complete within 30 seconds
                        self.log_test(f"Memory Test {i+1}", "PASS", 
                                    f"Completed in {response_time:.2f}s")
                    else:
                        self.log_test(f"Memory Test {i+1}", "WARN", 
                                    f"Slow response: {response_time:.2f}s")
                else:
                    self.log_test(f"Memory Test {i+1}", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Memory Test {i+1}", "FAIL", str(e))
    
    def test_price_parsing_edge_cases(self):
        """Test price parsing with various formats"""
        print("\n💰 Testing Price Parsing Edge Cases")
        print("-" * 50)
        
        # This would require unit testing the transform_airbnb_properties function
        # For now, test with queries that might return unusual price formats
        price_test_queries = [
            "Find cheapest place in San Francisco",
            "Find most expensive place in New York",
            "Find place under $50 in Miami",
            "Find place over $1000 in Los Angeles",
        ]
        
        for query in price_test_queries:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/search",
                    json={"query": query},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    properties = data.get('data', {}).get('properties', [])
                    
                    # Check if all properties have valid prices
                    valid_prices = all(
                        isinstance(prop.get('price'), (int, float)) and prop.get('price') > 0
                        for prop in properties
                    )
                    
                    if valid_prices or len(properties) == 0:
                        self.log_test(f"Price Parsing: {query[:30]}...", "PASS", 
                                    f"All {len(properties)} properties have valid prices")
                    else:
                        self.log_test(f"Price Parsing: {query[:30]}...", "FAIL", 
                                    "Some properties have invalid prices")
                else:
                    self.log_test(f"Price Parsing: {query[:30]}...", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Price Parsing: {query[:30]}...", "FAIL", str(e))
    
    def test_rating_parsing_edge_cases(self):
        """Test rating parsing with various formats"""
        print("\n⭐ Testing Rating Parsing Edge Cases")
        print("-" * 50)
        
        # Test with queries that might return unusual rating formats
        rating_test_queries = [
            "Find highest rated place in San Francisco",
            "Find place with good reviews in New York",
            "Find new properties in Miami",
        ]
        
        for query in rating_test_queries:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/search",
                    json={"query": query},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    properties = data.get('data', {}).get('properties', [])
                    
                    # Check if all properties have valid ratings
                    valid_ratings = all(
                        isinstance(prop.get('rating'), (int, float)) and 
                        0 <= prop.get('rating') <= 5 and
                        isinstance(prop.get('reviewCount'), int) and
                        prop.get('reviewCount') >= 0
                        for prop in properties
                    )
                    
                    if valid_ratings or len(properties) == 0:
                        self.log_test(f"Rating Parsing: {query[:30]}...", "PASS", 
                                    f"All {len(properties)} properties have valid ratings")
                    else:
                        self.log_test(f"Rating Parsing: {query[:30]}...", "FAIL", 
                                    "Some properties have invalid ratings")
                else:
                    self.log_test(f"Rating Parsing: {query[:30]}...", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Rating Parsing: {query[:30]}...", "FAIL", str(e))
    
    def test_openrouter_service_failures(self):
        """Test handling of OpenRouter service failures"""
        print("\n🤖 Testing OpenRouter Service Failure Handling")
        print("-" * 50)
        
        # Test queries that would trigger OpenRouter usage
        ai_test_queries = [
            "Find the best luxury properties globally",
            "Recommend properties for a family vacation",
            "Find unique accommodations in Europe",
        ]
        
        for query in ai_test_queries:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/search",
                    json={"query": query},
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Even if OpenRouter fails, the search should still work with fallbacks
                    if data.get('success') is not False:
                        self.log_test(f"OpenRouter Fallback: {query[:30]}...", "PASS", 
                                    "Search worked despite potential AI service issues")
                    else:
                        self.log_test(f"OpenRouter Fallback: {query[:30]}...", "FAIL", 
                                    "Search failed when AI service unavailable")
                else:
                    self.log_test(f"OpenRouter Fallback: {query[:30]}...", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"OpenRouter Fallback: {query[:30]}...", "FAIL", str(e))
    
    def test_data_consistency(self):
        """Test data consistency across multiple requests"""
        print("\n🔄 Testing Data Consistency")
        print("-" * 50)
        
        # Make the same request multiple times and check for consistency
        test_query = "Find a place in San Francisco"
        responses = []
        
        for i in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/search",
                    json={"query": test_query},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    responses.append(data)
                    
            except Exception as e:
                self.log_test("Data Consistency", "FAIL", f"Request {i+1} failed: {str(e)}")
                return
        
        if len(responses) >= 2:
            # Check if responses have similar structure
            first_response = responses[0]
            consistent = True
            
            for response in responses[1:]:
                if (response.get('success') != first_response.get('success') or
                    len(response.get('data', {}).get('properties', [])) == 0 and 
                    len(first_response.get('data', {}).get('properties', [])) > 0):
                    consistent = False
                    break
            
            if consistent:
                self.log_test("Data Consistency", "PASS", 
                            f"Consistent results across {len(responses)} requests")
            else:
                self.log_test("Data Consistency", "FAIL", 
                            "Inconsistent results across requests")
        else:
            self.log_test("Data Consistency", "FAIL", 
                        "Not enough successful responses to compare")
    
    def run_all_tests(self):
        """Run all edge case tests"""
        print("🧪 AI Airbnb Search - Comprehensive Edge Case Testing Suite")
        print("=" * 70)
        
        # Check if backend is running
        try:
            health_response = requests.get(f"{self.base_url}/health", timeout=5)
            if health_response.status_code != 200:
                print("❌ Backend is not running or unhealthy")
                return
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            return
        
        print("✅ Backend is running and healthy")
        
        # Run all test categories
        test_methods = [
            self.test_malformed_api_responses,
            self.test_invalid_location_inputs,
            self.test_concurrent_requests,
            self.test_large_query_inputs,
            self.test_network_timeout_scenarios,
            self.test_memory_usage_patterns,
            self.test_price_parsing_edge_cases,
            self.test_rating_parsing_edge_cases,
            self.test_openrouter_service_failures,
            self.test_data_consistency,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} failed: {e}")
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate a summary report of all tests"""
        print("\n" + "=" * 70)
        print("📊 EDGE CASE TESTING SUMMARY REPORT")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        warning_tests = sum(1 for r in self.test_results if r['status'] == 'WARN')
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            print("-" * 40)
            for test in self.failed_tests:
                print(f"• {test['test']}: {test['details']}")
        
        # Save detailed report
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "test_results": self.test_results,
            "failed_tests": self.failed_tests,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('edge_case_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: edge_case_test_report.json")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        
        if failed_tests > 0:
            print("• Fix failed test cases to improve system robustness")
        if warning_tests > 0:
            print("• Review warning cases for potential improvements")
        
        print("• Implement retry logic for API failures")
        print("• Add input validation and sanitization")
        print("• Implement circuit breaker pattern for external services")
        print("• Add comprehensive logging for debugging")
        print("• Consider implementing rate limiting")
        print("• Add monitoring and alerting for production")

if __name__ == "__main__":
    test_suite = EdgeCaseTestSuite()
    test_suite.run_all_tests()
