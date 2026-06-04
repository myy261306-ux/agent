#!/usr/bin/env python3
"""
Test script for NLI (Natural Language Interface) system
Tests command parser, intent detection, and NLP conversion
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from input_handlers import CommandParser, NLPConverter, IntentType

def test_command_parser():
    """Test command parser with various inputs"""
    print("\n" + "=" * 60)
    print("TEST 1: Command Parser - Intent Detection")
    print("=" * 60)

    parser = CommandParser()
    
    test_cases = [
        ("hello", IntentType.GREETING),
        ("hi there", IntentType.GREETING),
        ("help", IntentType.HELP_REQUEST),
        ("?", IntentType.HELP_REQUEST),
        ("new", IntentType.TASK_CREATION),
        ("build a website", IntentType.TASK_CREATION),
        ("create an app", IntentType.TASK_CREATION),
        ("mujhe website bana do", IntentType.TASK_CREATION),
        ("list", IntentType.LIST_ITEMS),
        ("show projects", IntentType.LIST_ITEMS),
        ("work on project", IntentType.PROJECT_WORK),
        ("status", IntentType.STATUS),
        ("how are you", IntentType.STATUS),
        ("exit", IntentType.EXIT),
        ("quit", IntentType.EXIT),
        ("xyz unknown command", IntentType.UNCLEAR),
    ]
    
    passed = 0
    failed = 0
    
    for user_input, expected_intent in test_cases:
        intent = parser.parse(user_input)
        is_correct = intent.intent_type == expected_intent
        status = "✓" if is_correct else "✗"
        
        print(f"{status} Input: '{user_input}'")
        print(f"  Expected: {expected_intent.value}, Got: {intent.intent_type.value}")
        print(f"  Confidence: {intent.confidence:.2f}")
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        print()
    
    print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    return failed == 0


def test_nlp_converter():
    """Test NLP converter - intent to task parameters"""
    print("\n" + "=" * 60)
    print("TEST 2: NLP Converter - Intent to Task Parameters")
    print("=" * 60)
    
    converter = NLPConverter()
    parser = CommandParser()
    
    test_cases = [
        ("build a website", "create_project"),
        ("list projects", "list_projects"),
        ("show help", "show_help"),
        ("hello", "acknowledge"),
        ("what's the status", "show_status"),
    ]
    
    passed = 0
    failed = 0
    
    for user_input, expected_action in test_cases:
        intent = parser.parse(user_input)
        params = converter.convert_to_task_params(intent)
        actual_action = params.get("action", "unknown")
        
        is_correct = actual_action == expected_action
        status = "✓" if is_correct else "✗"
        
        print(f"{status} Input: '{user_input}'")
        print(f"  Expected action: {expected_action}, Got: {actual_action}")
        print(f"  Full params: {params}")
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        print()
    
    print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    return failed == 0


def test_project_type_extraction():
    """Test project type extraction from natural language"""
    print("\n" + "=" * 60)
    print("TEST 3: Project Type Extraction")
    print("=" * 60)
    
    converter = NLPConverter()
    
    test_cases = [
        ("build a website with react", "website"),
        ("create a rest api", "api"),
        ("make a cli tool", "cli"),
        ("write a python script", "script"),
        ("data analysis tool", "data-analysis"),
        ("python library", "library"),
        ("unknown project", None),
    ]
    
    passed = 0
    failed = 0
    
    for user_input, expected_type in test_cases:
        detected_type = converter._extract_project_type(user_input.lower())
        is_correct = detected_type == expected_type
        status = "✓" if is_correct else "✗"
        
        print(f"{status} Input: '{user_input}'")
        print(f"  Expected type: {expected_type}, Got: {detected_type}")
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        print()
    
    print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    return failed == 0


def test_keyword_retrieval():
    """Test keyword retrieval for each intent type"""
    print("\n" + "=" * 60)
    print("TEST 4: Keyword Retrieval by Intent Type")
    print("=" * 60)
    
    parser = CommandParser()
    
    intent_types = [
        IntentType.GREETING,
        IntentType.TASK_CREATION,
        IntentType.HELP_REQUEST,
        IntentType.PROJECT_WORK,
        IntentType.LIST_ITEMS,
        IntentType.STATUS,
        IntentType.EXIT,
    ]
    
    all_passed = True
    
    for intent_type in intent_types:
        keywords = parser.get_keywords_for_intent(intent_type)
        has_keywords = len(keywords) > 0
        status = "✓" if has_keywords else "✗"
        
        print(f"{status} {intent_type.value}: {len(keywords)} keywords")
        print(f"  Examples: {', '.join(keywords[:3])}")
        
        if not has_keywords:
            all_passed = False
        print()
    
    return all_passed


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 NLI SYSTEM TEST SUITE")
    print("=" * 60)
    
    results = {
        "Command Parser": test_command_parser(),
        "NLP Converter": test_nlp_converter(),
        "Project Type Extraction": test_project_type_extraction(),
        "Keyword Retrieval": test_keyword_retrieval(),
    }
    
    print("\n" + "=" * 60)
    print("OVERALL TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
