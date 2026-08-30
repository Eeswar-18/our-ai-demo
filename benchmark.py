"""
Benchmark script to measure latency of our-ai-demo V0.
"""
import time
import json
from typing import Dict, Any
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def time_request(message: str) -> Dict[str, Any]:
    """Send a request to the chat endpoint and measure the latency."""
    start = time.time()
    response = client.post("/v1/chat", json={"message": message})
    end = time.time()
    
    latency = end - start
    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "latency": latency,
            "response": data.get("message", ""),
            "intent": data.get("intent", ""),
            "tool_executions": data.get("tool_executions", []),
            "verification_results": data.get("verification_results", [])
        }
    else:
        return {
            "success": False,
            "latency": latency,
            "status_code": response.status_code,
            "detail": response.json().get("detail", "")
        }

def run_benchmark():
    """Run a series of requests and report latency."""
    print("Running benchmark for our-ai-demo V0...")
    print("=" * 50)
    
    # Simple request: general question
    simple_message = "Hello, how are you?"
    print(f"Simple request: '{simple_message}'")
    simple_result = time_request(simple_message)
    if simple_result["success"]:
        print(f"  Success: True")
        print(f"  Latency: {simple_result['latency']:.3f} seconds")
        print(f"  Intent: {simple_result['intent']}")
        print(f"  Tool executions: {len(simple_result['tool_executions'])}")
        print(f"  Verification results: {len(simple_result['verification_results'])}")
    else:
        print(f"  Success: False")
        print(f"  Latency: {simple_result['latency']:.3f} seconds")
        print(f"  Error: {simple_result['detail']}")
    
    print()
    
    # Complex request: payment status inquiry
    complex_message = "I paid with transaction ID txn_123456. Was it successful?"
    print(f"Complex request: '{complex_message}'")
    complex_result = time_request(complex_message)
    if complex_result["success"]:
        print(f"  Success: True")
        print(f"  Latency: {complex_result['latency']:.3f} seconds")
        print(f"  Intent: {complex_result['intent']}")
        print(f"  Tool executions: {len(complex_result['tool_executions'])}")
        print(f"  Verification results: {len(complex_result['verification_results'])}")
    else:
        print(f"  Success: False")
        print(f"  Latency: {complex_result['latency']:.3f} seconds")
        print(f"  Error: {complex_result['detail']}")
    
    print()
    print("=" * 50)
    print("Benchmark complete.")
    
    # Check against Phase 0 targets
    print("\nPhase 0 Latency Targets:")
    print("  Simple request latency < 2 seconds")
    print("  Complex request latency < 5 seconds")
    print()
    if simple_result["success"] and simple_result["latency"] < 2.0:
        print("[PASS] Simple request target met")
    else:
        print("[FAIL] Simple request target NOT met")
        
    if complex_result["success"] and complex_result["latency"] < 5.0:
        print("[PASS] Complex request target met")
    else:
        print("[FAIL] Complex request target NOT met")

if __name__ == "__main__":
    run_benchmark()
