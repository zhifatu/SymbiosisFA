import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .philosophy_test import PhilosophicalConsistencyTestSuite
from .completeness_test import CompletenessTester
from .kunzhuan_test import KunzhuanValidator


def run_all_tests():
    """运行所有测试"""

    print("=" * 70)
    print("秩法图框架完整测试套件")
    print("=" * 70)

    all_passed = True
    results = {}

    # 1. 哲学一致性测试
    print("\n1. 运行哲学一致性测试...")
    philosophy_tester = PhilosophicalConsistencyTestSuite()
    philosophy_results = philosophy_tester.run_all_tests()
    results['philosophy'] = philosophy_results

    philosophy_passed = philosophy_results.get('all_passed', False)
    all_passed = all_passed and philosophy_passed

    print(f"   结果: {'✅ 通过' if philosophy_passed else '❌ 失败'}")

    # 2. 完备性测试
    print("\n2. 运行完备性测试...")
    completeness_tester = CompletenessTester()
    completeness_results = completeness_tester.test_full_coverage()
    results['completeness'] = completeness_results

    completeness_passed = completeness_results.get('meets_requirements', False)
    all_passed = all_passed and completeness_passed

    print(f"   结果: {'✅ 通过' if completeness_passed else '❌ 失败'}")

    # 3. 坤转正确性测试
    print("\n3. 运行坤转正确性测试...")
    kunzhuan_validator = KunzhuanValidator()
    kunzhuan_results = kunzhuan_validator.test_all_cases()
    results['kunzhuan'] = kunzhuan_results

    kunzhuan_passed = kunzhuan_results.get('all_correct', False)
    all_passed = all_passed and kunzhuan_passed

    print(f"   结果: {'✅ 通过' if kunzhuan_passed else '❌ 失败'}")

    # 4. 集成测试
    print("\n4. 运行集成测试...")
    integration_results = test_integration()
    results['integration'] = integration_results

    integration_passed = integration_results.get('success', False)
    all_passed = all_passed and integration_passed

    print(f"   结果: {'✅ 通过' if integration_passed else '❌ 失败'}")

    # 最终报告
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

    if all_passed:
        print("🎉 所有测试通过！秩法图框架验证成功。")
    else:
        print("❌ 部分测试失败，需要修复。")

    # 生成详细报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'all_passed': all_passed,
        'results': results,
        'summary': {
            'total_tests': 4,
            'passed_tests': sum([philosophy_passed, completeness_passed,
                                 kunzhuan_passed, integration_passed]),
            'failed_tests': 4 - sum([philosophy_passed, completeness_passed,
                                     kunzhuan_passed, integration_passed])
        }
    }

    # 保存报告
    import json
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n详细报告已保存: {report_file}")

    return all_passed, report


def test_integration():
    """集成测试：运行完整模拟"""
    try:
        from primal_framework.simulator import FALawSimulator

        print("   运行演示模拟...")
        simulator = FALawSimulator({'simulation_id': 'integration_test'})

        # 快速运行一个小场景
        report = simulator.run_scenario('survival_competition', steps=10, step_duration=0)

        # 验证基本要求
        requirements_met = all([
            report.get('final_state', {}).get('entities_total', 0) > 0,
            'philosophy_validation' in report,
            report.get('philosophy_validation', {}).get('all_valid', False)
        ])

        return {
            'success': requirements_met,
            'scenario_ran': True,
            'entities_created': report.get('final_state', {}).get('entities_total', 0),
            'philosophy_valid': report.get('philosophy_validation', {}).get('all_valid', False),
            'report_generated': True
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'scenario_ran': False
        }


if __name__ == "__main__":
    success, report = run_all_tests()

    # 根据测试结果退出
    sys.exit(0 if success else 1)