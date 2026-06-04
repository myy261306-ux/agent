"""
System Validation Tests
Quick tests to verify all components work
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from main_manager import MainManager
from utils.logger import system_logger

logger = system_logger


async def test_initialization():
    """Test system initialization"""
    print("\n✓ Test 1: System Initialization")
    print("-" * 60)

    try:
        manager = MainManager()
        logger.info("✓ MainManager created successfully")

        # Validate connections
        result = await manager.initialize()
        if result:
            logger.info("✓ System initialization successful")
        else:
            logger.error("✗ System initialization failed")
            return False

        # Display status
        manager.display_status()
        return True

    except Exception as e:
        logger.error(f"✗ Initialization test failed: {str(e)}")
        return False


async def test_project_creation():
    """Test project creation"""
    print("\n✓ Test 2: Project Creation")
    print("-" * 60)

    try:
        manager = MainManager()
        await manager.initialize()

        # Create test project
        project = await manager.start_new_project(
            "Test Project", "website", "Test description"
        )

        logger.info(f"✓ Project created: {project.project_id}")
        logger.info(f"✓ Project path: {project.base_path}")

        # Verify project storage
        projects = manager.project_manager.list_projects()
        logger.info(f"✓ Total projects: {len(projects)}")

        return True

    except Exception as e:
        logger.error(f"✗ Project creation test failed: {str(e)}")
        return False


async def test_llm_providers():
    """Test LLM provider configuration"""
    print("\n✓ Test 3: LLM Providers")
    print("-" * 60)

    try:
        manager = MainManager()

        # Get provider info
        provider_info = manager.llm_client.get_provider_info()

        logger.info(f"Total providers configured: {provider_info['total_providers']}")
        logger.info(f"Provider order: {provider_info['provider_order']}")

        for provider in provider_info["providers"]:
            logger.info(f"  - {provider['name']} ({provider['model']})")

        if provider_info["total_providers"] == 0:
            logger.warning("⚠ No LLM providers configured!")
            logger.warning("Add API keys to .env file to enable providers")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ LLM provider test failed: {str(e)}")
        return False


async def test_config_validation():
    """Test configuration validation"""
    print("\n✓ Test 4: Configuration Validation")
    print("-" * 60)

    try:
        from utils.config import Config

        logger.info(f"Projects directory: {Config.PROJECTS_DIR}")
        logger.info(f"Log level: {Config.LOG_LEVEL}")
        logger.info(f"Max concurrent agents: {Config.MAX_CONCURRENT_AGENTS}")
        logger.info(f"Request timeout: {Config.REQUEST_TIMEOUT}s")

        available = Config.get_available_providers()
        logger.info(f"Available providers: {available if available else 'None'}")

        return True

    except Exception as e:
        logger.error(f"✗ Configuration validation failed: {str(e)}")
        return False


async def run_all_tests():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("🧪 SYSTEM VALIDATION TESTS")
    print("=" * 60)

    results = {}

    # Run tests
    results["Configuration"] = await test_config_validation()
    results["LLM Providers"] = await test_llm_providers()
    results["System Initialization"] = await test_initialization()
    results["Project Creation"] = await test_project_creation()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
