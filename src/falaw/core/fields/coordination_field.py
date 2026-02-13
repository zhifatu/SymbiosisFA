from falaw.core.base.field_base import FieldBase as BaseField
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime
from ..base.field_base import FieldBase
from falaw.models.entities import Individual, Collective
from falaw.core.data_source import get_data_source


class CoordinationField:
    def __init__(self, config=None):
        self.data = get_data_source(config)
        self.registered_fields = {}

    def assess_field_health(self, element_states) -> Dict:
        """评估各场健康度——从矩阵数据计算"""
        retentions = self.data.get_all_self_retentions()

        health = {}
        for field_id, field in self.registered_fields.items():
            if field_id == 'primal':
                # 乾定健康度 = 自我保留率的平均值
                health[field_id] = sum(retentions.values()) / len(retentions)
            elif field_id == 'chaos':
                # 坤转健康度 = 1 - 张力
                tension = self.data.get_tension(element_states)
                health[field_id] = 1 - tension.get('total', {}).get('value', 0)
            # ... 其他场

        return health

    def register_fields(self, field_ids: List[str]):
        """注册要协调的场"""
        self.coordinated_fields = field_ids
        print(f"[CoordinationField] 已注册 {len(field_ids)} 个场: {field_ids}")

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行协调分析"""
        if not self.coordinated_fields:
            return {
                'field': self.field_id,
                'error': 'No fields registered for coordination',
                'kunzhuan_alert': False
            }

        print(f"\n{'=' * 60}")
        print(f"统筹场协调分析开始 | 时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"上下文: {context.get('phenomenon', '未知现象')}")
        print('=' * 60)

        # 收集各场分析结果
        field_analyses = self._collect_field_analyses(context)

        # 协调分析结果
        coordinated_result = self._coordinate_analyses(field_analyses, context)

        # 检查场维持状态
        field_health = self._check_field_health(field_analyses)

        # 记录本次协调
        coordination_record = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'field_analyses': field_analyses,
            'coordinated_result': coordinated_result,
            'field_health': field_health,
            'consensus_achieved': coordinated_result['consensus_achieved']
        }

        self.coordination_history.append(coordination_record)

        # 检查是否需要坤转
        kunzhuan_required = self._check_kunzhuan_requirement(field_health, coordinated_result)

        if kunzhuan_required:
            print(f"⚠️ [坤转警报] 场无法维持，需要坤转指引")
            self.kunzhuan_alert_level = 1.0
            self.field_failure_detected = True

        result = {
            'field': self.field_id,
            'coordinated_result': coordinated_result,
            'field_health': field_health,
            'consensus_achieved': coordinated_result['consensus_achieved'],
            'consensus_type': coordinated_result['consensus_type'],
            'kunzhuan_required': kunzhuan_required,
            'kunzhuan_alert_level': self.kunzhuan_alert_level,
            'recommended_actions': self._generate_recommendations(coordinated_result, field_health),
            'coordination_method': self.config.get('method', 'primal_integration')
        }

        return result

    def _collect_field_analyses(self, context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """收集各场的分析结果"""
        analyses = {}

        # 这里需要实际的场实例
        # 在完整框架中，会通过场协调器获取真实的分析结果
        # 现在使用模拟数据

        simulated_analyses = {
            'primal_field': {
                'field': 'primal_field',
                'analysis': {
                    'primal_presence': True,
                    'excitation_level': 0.8,
                    'life_signs': ['consciousness', 'metabolism'],
                    'kunzhuan_relevance': 0.3,
                    'recommendations': ['maintain_excitation']
                }
            },
            'target_field': {
                'field': 'target_field',
                'analysis': {
                    'target_pursuit_detected': True,
                    'target_type': 'survival',
                    'elimination_justified': False,
                    'kunzhuan_relevance': 0.2,
                    'recommendations': ['clarify_target_hierarchy']
                }
            },
            'mechanism_field': {
                'field': 'mechanism_field',
                'analysis': {
                    'mechanisms_applied': ['survival_instinct', 'resource_optimization'],
                    'explanation_completeness': 0.9,
                    'fallback_used': False,
                    'kunzhuan_relevance': 0.1,
                    'recommendations': ['record_new_pattern']
                }
            }
        }

        return simulated_analyses

    def _coordinate_analyses(self, field_analyses: Dict[str, Dict[str, Any]],
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """协调各场分析结果"""

        # 1. 提取关键结论
        key_conclusions = self._extract_key_conclusions(field_analyses)

        # 2. 检查一致性
        consistency = self._check_consistency(key_conclusions)

        # 3. 尝试形成共识
        consensus_result = self._form_consensus(key_conclusions, consistency, context)

        # 4. 生成统一理解
        unified_understanding = self._generate_unified_understanding(
            field_analyses, consensus_result, context
        )

        coordinated_result = {
            'key_conclusions': key_conclusions,
            'consistency_level': consistency['level'],
            'consistency_details': consistency['details'],
            'consensus_achieved': consensus_result['achieved'],
            'consensus_type': consensus_result['type'],
            'consensus_content': consensus_result['content'],
            'unified_understanding': unified_understanding,
            'coordination_method': 'primal_integration',
            'integration_time': datetime.now().isoformat()
        }

        if consensus_result['achieved']:
            self.consensus_records.append({
                'timestamp': datetime.now().isoformat(),
                'consensus_type': consensus_result['type'],
                'content': consensus_result['content'],
                'context': context
            })

        return coordinated_result

    def _extract_key_conclusions(self, field_analyses: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """从各场分析中提取关键结论"""
        conclusions = {}

        for field_id, analysis in field_analyses.items():
            field_conclusions = []

            # 从分析结果中提取结论
            field_data = analysis.get('analysis', {})

            if 'primal_presence' in field_data and field_data['primal_presence']:
                field_conclusions.append('primal_excitation_present')

            if 'target_pursuit_detected' in field_data and field_data['target_pursuit_detected']:
                field_conclusions.append('target_pursuit_detected')

            if 'mechanisms_applied' in field_data:
                field_conclusions.append(f"mechanisms: {len(field_data['mechanisms_applied'])}")

            if 'recommendations' in field_data:
                field_conclusions.extend([f"rec_{rec}" for rec in field_data['recommendations']])

            conclusions[field_id] = field_conclusions

        return conclusions

    def _check_consistency(self, conclusions: Dict[str, List[str]]) -> Dict[str, Any]:
        """检查各场结论的一致性"""

        # 收集所有结论
        all_conclusions = []
        for field_conclusions in conclusions.values():
            all_conclusions.extend(field_conclusions)

        # 统计结论频率
        from collections import Counter
        conclusion_counts = Counter(all_conclusions)

        # 计算一致性指标
        total_fields = len(conclusions)
        consistency_details = {}

        for conclusion, count in conclusion_counts.items():
            agreement_ratio = count / total_fields
            consistency_details[conclusion] = {
                'agreement_ratio': agreement_ratio,
                'field_count': count,
                'consistent': agreement_ratio >= 0.5
            }

        # 总体一致性水平
        consistent_conclusions = sum(1 for detail in consistency_details.values()
                                     if detail['consistent'])
        total_conclusions = len(consistency_details)

        if total_conclusions == 0:
            consistency_level = 1.0  # 无结论时视为完全一致
        else:
            consistency_level = consistent_conclusions / total_conclusions

        return {
            'level': consistency_level,
            'details': consistency_details,
            'total_fields': total_fields,
            'consistent_conclusions': consistent_conclusions,
            'total_conclusions': total_conclusions
        }

    def _form_consensus(self, conclusions: Dict[str, List[str]],
                        consistency: Dict[str, Any],
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """尝试形成共识"""

        if consistency['level'] >= self.consensus_threshold:
            # 高一致性，可以形成强共识
            consensus_type = 'strong_consensus'

            # 提取共同结论作为共识内容
            common_conclusions = []
            for conclusion, detail in consistency['details'].items():
                if detail['consistent'] and detail['agreement_ratio'] >= 0.7:
                    common_conclusions.append(conclusion)

            consensus_content = {
                'type': 'common_conclusions',
                'content': common_conclusions,
                'agreement_level': consistency['level'],
                'based_on': 'field_agreement'
            }

            return {
                'achieved': True,
                'type': consensus_type,
                'content': consensus_content
            }
        else:
            # 低一致性，需要其他共识形式
            return self._alternative_consensus_forms(conclusions, consistency, context)

    def _alternative_consensus_forms(self, conclusions: Dict[str, List[str]],
                                     consistency: Dict[str, Any],
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """尝试其他共识形式"""

        # 1. 基于原力激发的共识
        if 'primal_excitation_present' in [c for cons in conclusions.values() for c in cons]:
            return {
                'achieved': True,
                'type': 'primal_based_consensus',
                'content': {
                    'type': 'primal_focus',
                    'content': 'Focus on primal excitation patterns',
                    'basis': 'existence_is_excitation_principle'
                }
            }

        # 2. 基于目标追求的共识
        target_related = any('target' in c.lower() for cons in conclusions.values() for c in cons)
        if target_related:
            return {
                'achieved': True,
                'type': 'target_based_consensus',
                'content': {
                    'type': 'target_focus',
                    'content': 'Focus on target pursuit patterns',
                    'basis': 'elimination_as_target_pursuit_principle'
                }
            }

        # 3. 基于坤转逻辑的共识（当无法形成传统共识时）
        return {
            'achieved': True,  # 在秩法图中，坤转准备也是一种"共识"
            'type': 'kunzhuan_preparation_consensus',
            'content': {
                'type': 'preparing_for_kunzhuan',
                'content': 'Fields diverging, preparing for guidance from chaos',
                'basis': 'kunzhuan_is_guidance_not_reconstruction'
            }
        }

    def _generate_unified_understanding(self, field_analyses: Dict[str, Dict[str, Any]],
                                        consensus_result: Dict[str, Any],
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """生成统一理解"""

        phenomenon = context.get('phenomenon', 'unknown_phenomenon')

        unified_understanding = {
            'phenomenon': phenomenon,
            'timestamp': datetime.now().isoformat(),
            'primal_aspect': {
                'present': True,  # 在秩法图中，原力总是存在
                'expression': 'direct' if 'primal_excitation_present' in
                                          [c for cons in field_analyses.values()
                                           for c in cons.get('analysis', {})] else 'indirect'
            },
            'target_aspect': {
                'detected': any('target' in str(v).lower()
                                for analysis in field_analyses.values()
                                for v in analysis.get('analysis', {}).values()),
                'type': 'survival_or_elimination'
            },
            'mechanism_aspect': {
                'explained': True,  # 在秩法图中，现象总是可解释的
                'primary_mechanism': 'primal_excitation_manifestation',
                'supporting_mechanisms': []
            },
            'consensus_integrated': consensus_result['achieved'],
            'consensus_type': consensus_result['type'],
            'philosophical_basis': [
                'existence_is_excitation',
                'elimination_as_target_pursuit',
                'kunzhuan_is_guidance_not_reconstruction'
            ],
            'interpretation': self._generate_interpretation(field_analyses, context)
        }

        return unified_understanding

    def _generate_interpretation(self, field_analyses: Dict[str, Dict[str, Any]],
                                 context: Dict[str, Any]) -> str:
        """生成现象解释"""

        phenomenon = context.get('phenomenon', 'this phenomenon')

        # 基础解释模板
        interpretation = f"现象 '{phenomenon}' "

        # 添加原力层面解释
        primal_detected = any('primal' in str(v).lower()
                              for analysis in field_analyses.values()
                              for v in analysis.get('analysis', {}).values())

        if primal_detected:
            interpretation += "涉及原力激发，"
        else:
            interpretation += "间接联系到原力激发，"

        # 添加目标层面解释
        target_detected = any('target' in str(v).lower()
                              for analysis in field_analyses.values()
                              for v in analysis.get('analysis', {}).values())

        if target_detected:
            interpretation += "体现为目标追求过程，"
        else:
            interpretation += "隐含目标追求逻辑，"

        # 添加机制层面解释
        mechanisms = []
        for analysis in field_analyses.values():
            mechs = analysis.get('analysis', {}).get('mechanisms_applied', [])
            mechanisms.extend(mechs)

        if mechanisms:
            interpretation += f"可通过{len(mechanisms)}种机制解释（{', '.join(mechanisms[:3])}等），"

        # 哲学总结
        interpretation += "符合秩法图三大公理。"

        return interpretation

    def _check_field_health(self, field_analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """检查各场的健康状态"""

        health_scores = {}
        issues = []

        for field_id, analysis in field_analyses.items():
            field_data = analysis.get('analysis', {})

            # 计算场健康分数
            coherence_score = field_data.get('coherence', 0.7)
            stability_score = field_data.get('stability', 0.6)
            primal_connection = field_data.get('primal_connection', 0.8)

            health_score = (coherence_score + stability_score + primal_connection) / 3

            health_scores[field_id] = {
                'score': health_score,
                'coherence': coherence_score,
                'stability': stability_score,
                'primal_connection': primal_connection
            }

            # 检查问题
            if health_score < 0.5:
                issues.append({
                    'field': field_id,
                    'issue': 'low_health_score',
                    'score': health_score,
                    'severity': 'high'
                })

            if coherence_score < 0.4:
                issues.append({
                    'field': field_id,
                    'issue': 'low_coherence',
                    'score': coherence_score,
                    'severity': 'medium'
                })

        overall_health = np.mean([h['score'] for h in health_scores.values()]) if health_scores else 1.0

        return {
            'overall_health': overall_health,
            'field_health_scores': health_scores,
            'issues': issues,
            'critical_issue_count': len([i for i in issues if i['severity'] == 'high']),
            'healthy': overall_health > 0.6 and len(issues) < 3
        }

    def _check_kunzhuan_requirement(self, field_health: Dict[str, Any],
                                    coordinated_result: Dict[str, Any]) -> bool:
        """检查是否需要坤转"""

        # 条件1：场健康严重恶化
        field_unhealthy = (field_health['overall_health'] < 0.4 or
                           field_health['critical_issue_count'] >= 2)

        # 条件2：共识完全无法形成
        consensus_failed = (not coordinated_result['consensus_achieved'] and
                            coordinated_result['consistency_level'] < 0.3)

        # 条件3：协调场本身检测到无法维持
        self_detected = self.field_failure_detected

        # 在秩法图中，坤转是场无法维持时的指引
        kunzhuan_required = (field_unhealthy or consensus_failed or self_detected)

        if kunzhuan_required:
            # 记录坤转触发原因
            trigger_reasons = []
            if field_unhealthy:
                trigger_reasons.append('field_health_critical')
            if consensus_failed:
                trigger_reasons.append('consensus_impossible')
            if self_detected:
                trigger_reasons.append('self_detected_failure')

            print(f"[CoordinationField] 坤转触发原因: {trigger_reasons}")

            # 坤转不是重建，而是混沌中的指引
            print("[CoordinationField] 坤转本质：从混沌中寻求新指引，不是重建旧秩序")
            print("[CoordinationField] 坤转方法：忽略残缺，基于原力激发重新对齐")

        return kunzhuan_required

    def _generate_recommendations(self, coordinated_result: Dict[str, Any],
                                  field_health: Dict[str, Any]) -> List[str]:
        """生成行动建议"""

        recommendations = []

        # 基于共识状态
        if coordinated_result['consensus_achieved']:
            consensus_type = coordinated_result['consensus_type']

            if consensus_type == 'strong_consensus':
                recommendations.append('Implement consensus-based actions')
            elif consensus_type == 'primal_based_consensus':
                recommendations.append('Focus on primal excitation optimization')
            elif consensus_type == 'target_based_consensus':
                recommendations.append('Clarify and pursue primary targets')
            elif consensus_type == 'kunzhuan_preparation_consensus':
                recommendations.append('Prepare for kunzhuan guidance')
        else:
            recommendations.append('Seek alternative consensus forms')

        # 基于场健康
        if not field_health['healthy']:
            recommendations.append('Address field health issues')

            for issue in field_health['issues']:
                if issue['severity'] == 'high':
                    recommendations.append(f"Fix critical issue in {issue['field']}")

        # 基于坤转状态
        if self.kunzhuan_alert_level > 0.7:
            recommendations.append('Initiate kunzhuan guidance process')
            recommendations.append('Ignore fragmentation and inconsistencies')
            recommendations.append('Seek primal realignment from chaos')

        # 基础推荐
        recommendations.append('Maintain primal excitation awareness')
        recommendations.append('Document phenomena-mechanism mappings')
        recommendations.append('Update field coordination protocols')

        return recommendations

    def validate_philosophy(self) -> Dict[str, Any]:
        """验证符合哲学公理"""

        checks = []

        # 检查1：是否连接到原力激发
        primal_check = {
            'check': 'connected_to_primal_excitation',
            'required': True,
            'actual': self.primal_connection > 0.5,
            'value': self.primal_connection,
            'valid': self.primal_connection > 0.5,
            'principle': 'existence_is_excitation'
        }
        checks.append(primal_check)

        # 检查2：是否支持目标追求逻辑
        target_check = {
            'check': 'supports_target_pursuit',
            'required': True,
            'actual': 'target_field' in self.coordinated_fields,
            'valid': 'target_field' in self.coordinated_fields,
            'principle': 'elimination_as_target_pursuit'
        }
        checks.append(target_check)

        # 检查3：是否正确处理坤转
        kunzhuan_check = {
            'check': 'correct_kunzhuan_handling',
            'required': True,
            'actual': self._check_kunzhuan_logic(),
            'valid': self._check_kunzhuan_logic(),
            'principle': 'kunzhuan_is_guidance_not_reconstruction'
        }
        checks.append(kunzhuan_check)

        all_valid = all(check['valid'] for check in checks)

        return {
            'valid': all_valid,
            'field': self.field_id,
            'checks': checks,
            'philosophical_basis': 'Coordinates while maintaining primal focus'
        }

    def _check_kunzhuan_logic(self) -> bool:
        """检查坤转逻辑正确性"""
        # 坤转必须是场无法维持时的指引，不是重建
        correct_trigger = self._check_kunzhuan_requirement(
            {'overall_health': 0.3, 'critical_issue_count': 3, 'healthy': False, 'issues': []},
            {'consensus_achieved': False, 'consistency_level': 0.2, 'consensus_type': 'none'}
        )

        # 坤转必须忽略残缺
        ignores_fragmentation = True  # 在实现中应检查

        # 坤转必须基于原力重对齐
        primal_based = self.primal_connection > 0.6

        return correct_trigger and ignores_fragmentation and primal_based

    def get_state(self) -> Dict[str, Any]:
        """获取当前场状态"""
        return {
            **self.state,
            'coordinated_fields': self.coordinated_fields,
            'coordination_history_count': len(self.coordination_history),
            'consensus_records_count': len(self.consensus_records),
            'conflict_records_count': len(self.conflict_records),
            'kunzhuan_alert_level': self.kunzhuan_alert_level,
            'field_failure_detected': self.field_failure_detected,
            'overall_health': self._check_field_health({})['overall_health']  # 简化
        }

    def reset(self):
        """重置场状态"""
        super().reset()
        self.coordination_history.clear()
        self.consensus_records.clear()
        self.conflict_records.clear()
        self.kunzhuan_alert_level = 0.0
        self.field_failure_detected = False

    def calculate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """实现抽象方法：计算协调状态"""
        return {
            'consensus_achieved': False,
            'consensus_type': 'none',
            'kunzhuan_required': False,
            'field_health': {
                'primal_field': 0.7,
                'target_field': 0.6,
                'mechanism_field': 0.8,
                'chaos_field': 0.5
            },
            'recommended_actions': []
        }

    def update(self, delta_time: float) -> None:
        """实现抽象方法：更新场状态"""
        # 简单实现，什么都不做
        pass

    def extend(self, extension: Dict[str, Any]) -> bool:
        """扩展场功能"""
        super().extend(extension)

        # 处理特定扩展类型
        extension_type = extension.get('type')

        if extension_type == 'new_coordination_method':
            method_name = extension.get('method_name')
            method_logic = extension.get('logic')
            if method_name and method_logic:
                # 添加新的协调方法
                if not hasattr(self, '_custom_methods'):
                    self._custom_methods = {}
                self._custom_methods[method_name] = method_logic
                return True

        elif extension_type == 'new_consensus_form':
            form_name = extension.get('form_name')
            form_logic = extension.get('logic')
            if form_name and form_logic:
                # 添加新的共识形式
                if not hasattr(self, '_consensus_forms'):
                    self._consensus_forms = []
                self._consensus_forms.append({'name': form_name, 'logic': form_logic})
                return True

        return False
# 保持向后兼容
Coordination = CoordinationField

__all__ = ['CoordinationField', 'Coordination']
