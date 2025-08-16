#!/usr/bin/env python3
"""
Continuous testing script for Green Hill Canarias multi-agent system
Tests both simple and multi-agent modes with Green Hill GPT integration.

The functionality here is intended for manual execution rather than as part
of the automated unit test suite. Pytest would otherwise collect the helper
function ``test_graph_mode`` and attempt to resolve its ``mode`` parameter as a
fixture, resulting in errors. Mark the entire module as skipped so that
standard ``pytest`` runs do not execute it.
"""

import os
import time
import json
from typing import Dict, Any
import pytest

# Skip this module during normal pytest runs
pytestmark = pytest.mark.skip(reason="integration test script")

from main import create_simple_graph, create_multi_agent_graph

# Test scenarios for continuous validation
TEST_SCENARIOS = [
    {
        "name": "Basic Strategy Query",
        "question": "What are the key strategic opportunities for Green Hill Canarias?",
        "expected_keywords": ["strategy", "opportunities", "growth", "canary"]
    },
    {
        "name": "Financial Planning",
        "question": "How should Green Hill Canarias approach investment and funding?",
        "expected_keywords": ["investment", "funding", "financial", "roi"]
    },
    {
        "name": "Market Analysis",
        "question": "What is the market potential in the Canary Islands for Green Hill?",
        "expected_keywords": ["market", "potential", "canary islands", "analysis"]
    },
    {
        "name": "Risk Assessment", 
        "question": "What are the main risks Green Hill Canarias should consider?",
        "expected_keywords": ["risk", "assessment", "mitigation", "considerations"]
    },
    {
        "name": "Innovation Focus",
        "question": "How can Green Hill Canarias leverage technology and innovation?",
        "expected_keywords": ["technology", "innovation", "digital", "transformation"]
    }
]

def test_graph_mode(mode: str, enable_green_hill_gpt: bool = False):
    """Test a specific graph mode with given configuration"""
    
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {mode.upper()} MODE")
    print(f"🌐 Green Hill GPT: {'ENABLED' if enable_green_hill_gpt else 'DISABLED'}")
    print(f"{'='*60}")
    
    # Create appropriate graph
    if mode == "multi_agent":
        app = create_multi_agent_graph()
    else:
        app = create_simple_graph()
    
    results = []
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n🔍 Test {i}/{len(TEST_SCENARIOS)}: {scenario['name']}")
        print(f"Question: {scenario['question']}")
        
        start_time = time.time()
        
        try:
            # Prepare state with configuration
            state = {
                "question": scenario["question"],
                "config": {
                    "enable_green_hill_gpt": enable_green_hill_gpt
                }
            }
            
            # Run the graph
            result = app.invoke(state)
            execution_time = time.time() - start_time
            
            # Extract answer from result
            answer = result.get("final_answer") or result.get("answer") or "No answer generated"
            
            # Validate response
            keywords_found = sum(1 for keyword in scenario["expected_keywords"] 
                               if keyword.lower() in answer.lower())
            keyword_score = keywords_found / len(scenario["expected_keywords"])
            
            test_result = {
                "scenario": scenario["name"],
                "success": True,
                "execution_time": execution_time,
                "keyword_score": keyword_score,
                "answer_length": len(answer),
                "has_error": bool(result.get("error")),
                "green_hill_response": bool(result.get("green_hill_gpt_response"))
            }
            
            print(f"✅ SUCCESS - {execution_time:.2f}s")
            print(f"📊 Keyword match: {keyword_score:.1%}")
            print(f"📝 Answer length: {len(answer)} chars")
            
            if result.get("error"):
                print(f"⚠️ Error present: {result['error']}")
            
            if enable_green_hill_gpt and result.get("green_hill_gpt_response"):
                print(f"🌟 Green Hill GPT response received")
            
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = {
                "scenario": scenario["name"],
                "success": False,
                "execution_time": execution_time,
                "error": str(e),
                "keyword_score": 0,
                "answer_length": 0
            }
            
            print(f"❌ FAILED - {execution_time:.2f}s")
            print(f"Error: {str(e)}")
        
        results.append(test_result)
        
        # Brief pause between tests
        time.sleep(1)
    
    return results

def generate_test_report(all_results: Dict[str, Any]):
    """Generate a comprehensive test report"""
    
    print(f"\n{'='*80}")
    print(f"📋 CONTINUOUS TESTING REPORT")
    print(f"{'='*80}")
    
    for mode, results in all_results.items():
        print(f"\n🔧 {mode.upper()}")
        print(f"{'-'*40}")
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["success"])
        avg_execution_time = sum(r["execution_time"] for r in results) / total_tests
        avg_keyword_score = sum(r.get("keyword_score", 0) for r in results) / total_tests
        
        print(f"✅ Success Rate: {successful_tests}/{total_tests} ({successful_tests/total_tests:.1%})")
        print(f"⏱️ Avg Execution Time: {avg_execution_time:.2f}s")
        print(f"📊 Avg Keyword Score: {avg_keyword_score:.1%}")
        
        # Show any failures
        failures = [r for r in results if not r["success"]]
        if failures:
            print(f"❌ Failures:")
            for failure in failures:
                print(f"   - {failure['scenario']}: {failure.get('error', 'Unknown error')}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    
    # Check deployment readiness
    simple_success_rate = sum(1 for r in all_results.get("simple", []) if r["success"]) / len(all_results.get("simple", [1]))
    
    if simple_success_rate >= 0.8:
        print(f"✅ Simple mode ready for production deployment")
    else:
        print(f"⚠️ Simple mode needs debugging before deployment")
    
    if "multi_agent" in all_results:
        multi_success_rate = sum(1 for r in all_results["multi_agent"] if r["success"]) / len(all_results["multi_agent"])
        if multi_success_rate >= 0.8:
            print(f"✅ Multi-agent mode ready for staging deployment") 
        else:
            print(f"⚠️ Multi-agent mode needs debugging")
    
    print(f"🌐 Green Hill GPT integration status: {'CONFIGURED' if os.getenv('GREEN_HILL_GPT_URL') else 'NOT CONFIGURED'}")

def run_continuous_tests():
    """Run the complete continuous testing suite"""
    
    print(f"🚀 STARTING CONTINUOUS TESTING SUITE")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = {}
    
    # Test simple mode (current deployment)
    all_results["simple"] = test_graph_mode("simple")
    
    # Test multi-agent mode
    all_results["multi_agent"] = test_graph_mode("multi_agent")
    
    # Test multi-agent with Green Hill GPT (if configured)
    if os.getenv("GREEN_HILL_GPT_URL"):
        all_results["multi_agent_with_gpt"] = test_graph_mode("multi_agent", enable_green_hill_gpt=True)
    
    # Generate comprehensive report
    generate_test_report(all_results)
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📁 Results saved to: {results_file}")
    
    return all_results

if __name__ == "__main__":
    # Environment setup tips
    print("🔧 ENVIRONMENT SETUP:")
    print("Set DEPLOYMENT_MODE=multi_agent to test multi-agent graph")
    print("Set GREEN_HILL_GPT_URL to enable Green Hill GPT integration")
    print("Set GREEN_HILL_API_KEY for authenticated requests")
    print()
    
    # Run the test suite
    results = run_continuous_tests()
    
    # Check if we should run in loop mode
    if os.getenv("CONTINUOUS_MODE") == "true":
        interval = int(os.getenv("TEST_INTERVAL", 300))  # 5 minutes default
        print(f"\n🔄 CONTINUOUS MODE: Testing every {interval} seconds")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                time.sleep(interval)
                print(f"\n{'='*20} SCHEDULED TEST RUN {'='*20}")
                run_continuous_tests()
        except KeyboardInterrupt:
            print(f"\n🛑 Continuous testing stopped by user")
