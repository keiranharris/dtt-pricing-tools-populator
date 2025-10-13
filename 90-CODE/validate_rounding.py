#!/usr/bin/env python3
"""
Quick validation script for Feature 006 whole-integer rounding functionality.

Tests the calculate_engineering_rate function with various inputs to verify
that rates are properly rounded to whole integers.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_rounding_functionality():
    """Test the rounding functionality with various rate calculations."""
    print("🔍 Testing Feature 006 Whole-Integer Rounding")
    print("=" * 50)
    
    try:
        from rate_card_calculator import calculate_engineering_rate
        
        # Test cases: (cost_rate, margin, expected_rounded_result)
        test_cases = [
            (100.0, 0.45, 182),   # 100/(1-0.45) = 181.82 -> 182  
            (120.0, 0.50, 240),   # 120/(1-0.50) = 240.0 -> 240
            (80.0, 0.35, 123),    # 80/(1-0.35) = 123.08 -> 123
            (150.0, 0.65, 429),   # 150/(1-0.65) = 428.57 -> 429
            (50.0, 0.40, 83),     # 50/(1-0.40) = 83.33 -> 83
            (75.0, 0.42, 129),    # 75/(1-0.42) = 129.31 -> 129
            (200.0, 0.55, 444),   # 200/(1-0.55) = 444.44 -> 444
        ]
        
        print("Testing rate calculations with rounding:")
        print(f"{'Cost Rate':>10} | {'Margin':>7} | {'Expected':>8} | {'Actual':>8} | {'Status':>8}")
        print("-" * 60)
        
        all_passed = True
        for cost_rate, margin, expected in test_cases:
            try:
                result = calculate_engineering_rate(cost_rate, margin)
                status = "✅ PASS" if result == expected else "❌ FAIL"
                if result != expected:
                    all_passed = False
                print(f"${cost_rate:>9.2f} | {margin*100:>6.1f}% | ${expected:>7} | ${result:>7} | {status}")
            except Exception as e:
                print(f"${cost_rate:>9.2f} | {margin*100:>6.1f}% | ${expected:>7} | {'ERROR':>7} | ❌ FAIL")
                all_passed = False
        
        print("-" * 60)
        
        if all_passed:
            print("✅ All rounding tests PASSED!")
            print("🎯 Feature 006 whole-integer rounding is working correctly")
        else:
            print("❌ Some rounding tests FAILED!")
            
        return all_passed
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_integer_types():
    """Test that returned values are proper integers."""
    print("\n🔍 Testing Return Type Validation")
    print("=" * 35)
    
    try:
        from rate_card_calculator import calculate_engineering_rate
        
        result = calculate_engineering_rate(100.0, 0.45)
        
        print(f"Result: {result}")
        print(f"Type: {type(result)}")
        print(f"Is integer: {isinstance(result, int)}")
        
        if isinstance(result, int):
            print("✅ Returns proper integer type")
            return True
        else:
            print("❌ Does not return integer type")
            return False
            
    except Exception as e:
        print(f"❌ Error testing types: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Feature 006 Whole-Integer Rounding Validation")
    print("=" * 50)
    
    test1_passed = test_rounding_functionality()
    test2_passed = test_integer_types()
    
    print("\n" + "=" * 50)
    print("🎯 VALIDATION SUMMARY")
    print("=" * 50)
    
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED")
        print("🎉 Feature 006 rounding implementation is ready!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED") 
        print("⚠️  Review implementation before proceeding")
        sys.exit(1)