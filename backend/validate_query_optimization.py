#!/usr/bin/env python3
"""
Optimized Query Service Validation Script

This script validates the optimized query service, batch processing,
and performance improvements for MeTTa operations.
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_optimized_query_service():
    """Test the optimized query service"""
    print("🚀 Testing Optimized Query Service")
    print("=" * 50)

    try:
        # Import the optimized query service
        from services.metta_query_optimizer import (
            get_optimized_query_service,
            execute_optimized_query,
            execute_batch_query
        )

        service = get_optimized_query_service()

        print("✅ Optimized query service initialized")
        print(f"   Max workers: {service.batch_processor.max_workers}")
        print(f"   Max connections: {service.connection_pool.max_connections}")

        # Test query optimization
        print("\n🔧 Testing Query Optimization")
        print("-" * 50)

        test_queries = [
            ('contribution_validation', {'contribution_id': 'test_123'}),
            ('user_contributions', {'user_id': 'user_456'}),
            ('batch_contributions', {'contribution_ids': ['c1', 'c2', 'c3']})
        ]

        for query_type, params in test_queries:
            optimized = service.query_optimizer.optimize_query(query_type, params)
            print(f"   {query_type}:")
            print(f"     Optimizations: {optimized['optimization_applied']}")
            print(f"     Estimated cost: {optimized['estimated_cost']:.3f}")
        # Test connection pool
        print("\n🔌 Testing Connection Pool")
        print("-" * 50)

        pool_stats = service.connection_pool.get_pool_stats()
        print(f"   Max connections: {pool_stats['max_connections']}")
        print(f"   Available: {pool_stats['available_connections']}")
        print(f"   Active: {pool_stats['active_connections']}")
        print(f"   Utilization: {pool_stats['pool_utilization']:.2%}")

        # Test connection acquisition and return
        conn = service.connection_pool.get_connection()
        if conn:
            print("   ✅ Connection acquired successfully")
            service.connection_pool.return_connection(conn)
            print("   ✅ Connection returned successfully")
        else:
            print("   ❌ Failed to acquire connection")

        # Test batch processing
        print("\n📦 Testing Batch Processing")
        print("-" * 50)

        # Create test data
        test_contributions = [f"contribution_{i}" for i in range(20)]
        test_rewards = [
            {
                'contribution_id': f"contribution_{i}",
                'quality_score': 0.5 + (i * 0.02),
                'impact_score': 0.3 + (i * 0.03)
            }
            for i in range(15)
        ]

        # Mock operation functions
        def mock_validate(contribution_id, **kwargs):
            time.sleep(0.01)  # Simulate processing time
            return {
                'contribution_id': contribution_id,
                'valid': True,
                'confidence': 0.85,
                'optimizations': kwargs.get('optimizations', [])
            }

        def mock_calculate_reward(request, **kwargs):
            time.sleep(0.005)  # Simulate processing time
            return {
                'contribution_id': request['contribution_id'],
                'reward': 50 + int(request['quality_score'] * 25),
                'optimizations': kwargs.get('optimizations', [])
            }

        # Test batch validation
        print("   Testing batch validation...")
        start_time = time.time()
        batch_result = service.execute_batch_query(
            'batch_contributions',
            test_contributions,
            mock_validate
        )
        batch_time = time.time() - start_time

        print(f"   ✅ Batch validation completed in {batch_time:.3f}s")
        print(f"     Processed: {batch_result['total_processed']} items")
        print(f"     Success: {batch_result['success_count']}")
        print(f"     Errors: {batch_result['error_count']}")
        print(f"     Avg time per item: {batch_result['avg_time_per_item']:.3f}s")
        # Test batch reward calculation
        print("\n   Testing batch reward calculation...")
        start_time = time.time()
        reward_result = service.execute_batch_query(
            'batch_rewards',
            test_rewards,
            mock_calculate_reward
        )
        reward_time = time.time() - start_time

        print(f"   ✅ Batch reward calculation completed in {reward_time:.3f}s")
        print(f"     Processed: {reward_result['total_processed']} items")
        print(f"     Success: {reward_result['success_count']}")
        print(f"     Errors: {reward_result['error_count']}")
        print(f"     Avg time per item: {reward_result['avg_time_per_item']:.3f}s")
        # Compare with individual processing
        print("\n⚡ Performance Comparison")
        print("-" * 50)

        # Individual processing
        print("   Testing individual processing...")
        start_time = time.time()
        individual_results = []
        for contribution in test_contributions[:10]:  # Test with subset
            result = mock_validate(contribution)
            individual_results.append(result)
        individual_time = time.time() - start_time

        print(f"   Individual processing: {individual_time:.3f}s for 10 items")
        print(f"   Batch processing speedup: {individual_time/batch_time:.1f}x faster")
        # Test health check
        print("\n🏥 Testing Health Check")
        print("-" * 50)

        health = service.health_check()
        print(f"   Overall status: {health['status']}")
        print(f"   Connection pool: {health['connection_pool']}")
        print(f"   Batch processor: {health['batch_processor']}")
        print(f"   Query optimizer: {health['query_optimizer']}")

        # Get performance stats
        print("\n📊 Performance Statistics")
        print("-" * 50)

        stats = service.get_performance_stats()
        print(f"   Total queries: {stats['overall_stats']['total_queries']}")
        print(f"   Success rate: {stats['overall_stats']['success_rate']:.2%}")
        print(f"   Query types: {stats['overall_stats']['query_types_count']}")

        if stats['query_stats']:
            print("   Query type breakdown:")
            for query_type, type_stats in stats['query_stats'].items():
                print(f"     {query_type}: {type_stats['total_queries']} queries, {type_stats['avg_duration']:.3f}s avg")

        print("\n✅ Optimized Query Service Validation Complete!")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ Optimized query service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_service_integration():
    """Test integration with enhanced MeTTa service"""
    print("\n🔗 Testing Enhanced Service Integration")
    print("=" * 50)

    try:
        from services.metta_integration_enhanced import get_metta_service

        service = get_metta_service(force_mock=True)

        print("✅ Enhanced service initialized")
        print(f"   Query optimizer: {'Available' if service.query_optimizer else 'Not Available'}")

        if service.query_optimizer:
            # Test batch validation integration
            print("\n   Testing batch validation integration...")
            test_contributions = [f"int_test_{i}" for i in range(10)]

            start_time = time.time()
            result = service.batch_validate_contributions(test_contributions)
            batch_time = time.time() - start_time

            print(f"   ✅ Batch validation completed in {batch_time:.3f}s")
            print(f"     Success: {result['success_count']}/{result['total_processed']}")

            # Test batch processing integration
            print("\n   Testing batch processing integration...")
            start_time = time.time()
            result = service.batch_process_contributions(test_contributions)
            process_time = time.time() - start_time

            print(f"   ✅ Batch processing completed in {process_time:.3f}s")
            print(f"     Success: {result['success_count']}/{result['total_processed']}")

            # Test batch rewards integration
            print("\n   Testing batch rewards integration...")
            test_rewards = [
                {
                    'contribution_id': f"reward_test_{i}",
                    'quality_score': 0.6 + (i * 0.02),
                    'impact_score': 0.4 + (i * 0.02)
                }
                for i in range(8)
            ]

            start_time = time.time()
            result = service.batch_calculate_rewards(test_rewards)
            reward_time = time.time() - start_time

            print(f"   ✅ Batch rewards completed in {reward_time:.3f}s")
            print(f"     Success: {result['success_count']}/{result['total_processed']}")

            # Test service health
            print("\n   Testing service health...")
            health = service.get_service_health()
            print(f"   Overall health: {'Healthy' if health['overall_healthy'] else 'Unhealthy'}")

            for component, status in health['components'].items():
                healthy_status = status.get('healthy', True) if isinstance(status, dict) else True
                print(f"     {component}: {'✅' if healthy_status else '❌'}")

        else:
            print("   ❌ Query optimizer not available for integration testing")

        print("\n✅ Enhanced Service Integration Test Complete!")
        return True

    except Exception as e:
        print(f"❌ Enhanced service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_optimization_report():
    """Generate optimization performance report"""
    print("\n📊 Generating Optimization Performance Report")
    print("=" * 50)

    try:
        from services.metta_query_optimizer import get_optimized_query_service
        from services.metta_integration_enhanced import get_metta_service

        query_service = get_optimized_query_service()
        enhanced_service = get_metta_service(force_mock=True)

        # Collect performance data
        report = {
            'generated_at': datetime.now().isoformat(),
            'query_service_stats': query_service.get_performance_stats(),
            'enhanced_service_health': enhanced_service.get_service_health(),
            'performance_comparison': {}
        }

        # Save report
        report_file = os.path.join(os.path.dirname(__file__), 'optimization_report.json')

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ Optimization report saved to: {report_file}")

        # Print summary
        print("\n📈 Optimization Summary:")
        overall_stats = report['query_service_stats']['overall_stats']
        print(f"   Total Optimized Queries: {overall_stats['total_queries']}")
        print(f"   Success Rate: {overall_stats['success_rate']:.2%}")
        print(f"   Query Types Optimized: {overall_stats['query_types_count']}")

        health = report['enhanced_service_health']
        print(f"   Service Health: {'Healthy' if health['overall_healthy'] else 'Needs Attention'}")

        return True

    except Exception as e:
        print(f"❌ Failed to generate optimization report: {e}")
        return False

if __name__ == "__main__":
    print("Nimo Optimized Query Service Validation")
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    # Run validation tests
    success1 = test_optimized_query_service()
    success2 = test_enhanced_service_integration()

    if success1 and success2:
        # Generate optimization report
        generate_optimization_report()

        print("\n🎯 Next Steps:")
        print("1. ✅ Query optimization and batch processing implemented")
        print("2. 🔄 Ready to implement connection pooling")
        print("3. 🔄 Ready to add health check endpoints")
        print("4. 🔄 Ready for production deployment preparation")

    else:
        print("\n❌ Some tests failed - check logs above")
        sys.exit(1)