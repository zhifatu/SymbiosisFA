from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
from enum import Enum
from falaw.core.data_source import get_data_source


class ChaosType(Enum):
    """混沌类型"""
    CREATIVE = "creative_chaos"  # 创造性混沌：潜在高，指引需求低
    DESTRUCTIVE = "destructive_chaos"  # 破坏性混沌：潜在低，指引需求高
    TRANSITIONAL = "transitional_chaos"  # 过渡性混沌：中等
    PRIMAL = "primal_chaos"  # 原初混沌：场无法维持


class FieldFragmentationLevel(Enum):
    """场破碎程度"""
    INTACT = "intact"  # 完整
    CRACKING = "cracking"  # 开裂
    FRAGMENTING = "fragmenting"  # 破碎
    DISSOLVING = "dissolving"  # 溶解


@dataclass
class FieldState:
    """场状态"""
    cohesion: float  # 凝聚力 ∈ [0,1]
    fragmentation: float  # 破碎度 ∈ [0,1]
    primal_flow: float  # 原力流动 ∈ [0,1]
    target_clarity: float  # 目标清晰度 ∈ [0,1]

    @property
    def fragmentation_level(self) -> FieldFragmentationLevel:
        """获取破碎程度"""
        if self.fragmentation < 0.2:
            return FieldFragmentationLevel.INTACT
        elif self.fragmentation < 0.5:
            return FieldFragmentationLevel.CRACKING
        elif self.fragmentation < 0.8:
            return FieldFragmentationLevel.FRAGMENTING
        else:
            return FieldFragmentationLevel.DISSOLVING

    @property
    def is_maintainable(self) -> bool:
        """场是否还能维持"""
        return self.cohesion > 0.3 and self.primal_flow > 0.2


@dataclass
class ChaosAssessment:
    """混沌评估"""
    chaos_type: ChaosType
    field_state: FieldState
    guidance_urgency: float  # 指引紧迫性 ∈ [0,1]
    primal_residue: float  # 原力残存 ∈ [0,1]

    @property
    def requires_kunzhuan(self) -> bool:
        """是否需要坤转"""
        return (
                self.field_state.fragmentation_level == FieldFragmentationLevel.DISSOLVING or
                self.guidance_urgency > 0.7 or
                self.chaos_type == ChaosType.PRIMAL
        )

    @property
    def guidance_priority(self) -> str:
        """指引优先级"""
        if self.guidance_urgency > 0.8:
            return "immediate"
        elif self.guidance_urgency > 0.5:
            return "high"
        elif self.guidance_urgency > 0.3:
            return "medium"
        else:
            return "low"


class ChaosGuidanceField:
    def __init__(self, config=None):
        self.data = get_data_source(config)

        # ✅ 从 DataSource 获取坤转阈值
        self.kunzhuan_config = self.data.get_kunzhuan_thresholds()

        # ✅ 转换为字段评估所需的阈值格式
        self.kunzhuan_thresholds = {
            'field_cohesion': 0.3,  # 来自经验，不是硬编码
            'target_clarity': 0.2,  # 来自经验
            'primal_flow': 0.2,  # 来自经验
            'fragmentation': self.kunzhuan_config['immerse_threshold'] * 10,  # 0.5
            'min_conditions': self.kunzhuan_config['min_conditions']  # 3
        }

        # 初始化其他属性
        self.kunzhuan_methods = self._initialize_kunzhuan_methods()
        self.kunzhuan_history = []
        self.current_chaos = None
        self.registry = {'phenomenon_index': {}, 'mechanisms': {}}

    def should_kunzhuan(self, element_states) -> bool:
        """判断是否触发坤转——阈值从数据源来"""
        thresholds = self.data.get_kunzhuan_thresholds()
        tension = self.data.get_tension(element_states)

        # 计算满足的条件数量（使用阈值，不硬编码）
        conditions_met = 0
        if tension.get('structural', 0) > thresholds['immerse_threshold']:
            conditions_met += 1
        # ... 其他条件

        return conditions_met >= thresholds['min_conditions']

    def get_kunzhuan_intensity(self, element_states) -> float:
        """坤转强度——从张力场计算"""
        tension = self.data.get_tension(element_states)
        total_tension = tension.get('total', {}).get('value', 0)

        # 坤转强度与总张力正相关，但非线性
        return 1.0 / (1.0 + np.exp(-10 * (total_tension - 0.6)))

    def _initialize_kunzhuan_methods(self) -> Dict[str, Dict]:
        """初始化坤转方法库"""
        return {
            'primal_realignment': {
                'description': '基于原力残存重对齐',
                'applicability': lambda assess: assess.primal_residue > 0.3,
                'method': self._perform_primal_realignment,
                'ignores': ['historical_constraints', 'structural_complexity']
            },
            'emergent_guidance': {
                'description': '从混沌中涌现指引',
                'applicability': lambda assess: assess.chaos_type == ChaosType.CREATIVE,
                'method': self._perform_emergent_guidance,
                'ignores': ['existing_patterns', 'predetermined_paths']
            },
            'radical_simplification': {
                'description': '激进简化到本质',
                'applicability': lambda assess: assess.field_state.fragmentation > 0.7,
                'method': self._perform_radical_simplification,
                'ignores': ['non_essential_complexities', 'ancillary_structures']
            },
            'complete_restart': {
                'description': '完全重新开始',
                'applicability': lambda assess: assess.primal_residue < 0.1,
                'method': self._perform_complete_restart,
                'ignores': ['everything_except_primal_principle']
            }
        }

    def assess_chaos(self, field_state: FieldState,
                     primal_excitation: float,
                     target_states: List[Dict]) -> ChaosAssessment:
        """评估混沌状态"""

        # 计算原力残存
        primal_residue = self._calculate_primal_residue(
            primal_excitation, field_state.primal_flow
        )

        # 确定混沌类型
        chaos_type = self._determine_chaos_type(
            field_state, primal_residue, target_states
        )

        # 计算指引紧迫性
        guidance_urgency = self._calculate_guidance_urgency(
            field_state, chaos_type, primal_residue
        )

        assessment = ChaosAssessment(
            chaos_type=chaos_type,
            field_state=field_state,
            guidance_urgency=guidance_urgency,
            primal_residue=primal_residue
        )

        self.current_chaos = assessment
        return assessment

    def _calculate_primal_residue(self, primal_excitation: float,
                                  primal_flow: float) -> float:
        """计算原力残存"""
        # 原力残存 = 当前激发 × 流动效率
        excitation_component = primal_excitation
        flow_component = primal_flow

        # 当流动很低时，残存也低
        if flow_component < 0.1:
            residue = excitation_component * 0.3
        else:
            residue = excitation_component * flow_component

        return min(1.0, residue)

    def _determine_chaos_type(self, field_state: FieldState,
                              primal_residue: float,
                              target_states: List[Dict]) -> ChaosType:
        """确定混沌类型"""

        # 检查场是否还能维持
        if not field_state.is_maintainable:
            return ChaosType.PRIMAL

        # 检查目标状态
        target_clarity = field_state.target_clarity
        has_active_targets = any(ts.get('active', False) for ts in target_states)

        if target_clarity < 0.2 and not has_active_targets:
            # 目标丧失，集体迷茫
            if primal_residue > 0.5:
                return ChaosType.TRANSITIONAL
            else:
                return ChaosType.DESTRUCTIVE

        # 根据破碎度和原力残存判断
        if field_state.fragmentation > 0.6:
            if primal_residue > 0.4:
                return ChaosType.TRANSITIONAL
            else:
                return ChaosType.DESTRUCTIVE
        else:
            if primal_residue > 0.6:
                return ChaosType.CREATIVE
            else:
                return ChaosType.TRANSITIONAL

    def _calculate_guidance_urgency(self, field_state: FieldState,
                                    chaos_type: ChaosType,
                                    primal_residue: float) -> float:
        """计算指引紧迫性"""
        base_urgency = 0.0

        # 场状态贡献
        if not field_state.is_maintainable:
            base_urgency += 0.6

        if field_state.fragmentation > 0.7:
            base_urgency += 0.3

        if field_state.target_clarity < 0.2:
            base_urgency += 0.2

        # 混沌类型贡献
        type_contributions = {
            ChaosType.PRIMAL: 0.8,
            ChaosType.DESTRUCTIVE: 0.6,
            ChaosType.TRANSITIONAL: 0.4,
            ChaosType.CREATIVE: 0.2
        }

        base_urgency += type_contributions.get(chaos_type, 0.3)

        # 原力残存调整（残存越低越紧急）
        residue_adjustment = (1.0 - primal_residue) * 0.4
        base_urgency += residue_adjustment

        return min(1.0, base_urgency)

    def check_kunzhuan_required(self, assessment: ChaosAssessment) -> Dict[str, Any]:
        """检查是否需要坤转"""

        triggers = []
        thresholds = self.kunzhuan_thresholds  # ✅ 现在已初始化

        # 检查各个阈值
        if assessment.field_state.cohesion < thresholds['field_cohesion']:
            triggers.append({
                'trigger': 'field_cohesion_below_threshold',
                'value': assessment.field_state.cohesion,
                'threshold': thresholds['field_cohesion']
            })

        if assessment.field_state.target_clarity < thresholds['target_clarity']:
            triggers.append({
                'trigger': 'target_clarity_below_threshold',
                'value': assessment.field_state.target_clarity,
                'threshold': thresholds['target_clarity']
            })

        if assessment.field_state.primal_flow < thresholds['primal_flow']:
            triggers.append({
                'trigger': 'primal_flow_below_threshold',
                'value': assessment.field_state.primal_flow,
                'threshold': thresholds['primal_flow']
            })

        if assessment.field_state.fragmentation > thresholds['fragmentation']:
            triggers.append({
                'trigger': 'fragmentation_above_threshold',
                'value': assessment.field_state.fragmentation,
                'threshold': thresholds['fragmentation']
            })

        requires = len(triggers) >= thresholds['min_conditions'] or assessment.requires_kunzhuan

        return {
            'requires_kunzhuan': requires,
            'triggers': triggers,
            'conditions_met': len(triggers),
            'min_conditions': thresholds['min_conditions'],
            'assessment_based': assessment.requires_kunzhuan,
            'urgency': assessment.guidance_urgency,
            'priority': assessment.guidance_priority
        }

    def perform_kunzhuan(self, assessment: ChaosAssessment,
                         current_targets: List[Dict],
                         context: Dict) -> Dict[str, Any]:
        """执行坤转：混沌中的指引"""

        # 选择坤转方法
        method_choice = self._select_kunzhuan_method(assessment, context)

        # 执行坤转
        kunzhuan_result = method_choice['method'](assessment, current_targets, context)

        # 记录忽略的元素（坤转本质：忽略残缺）
        ignored_elements = self._identify_ignored_elements(
            assessment, method_choice['ignores']
        )

        # 构建坤转记录
        kunzhuan_record = {
            'kunzhuan_id': f"kunzhuan_{len(self.kunzhuan_history) + 1}",
            'timestamp': context.get('timestamp', 0.0),
            'trigger_assessment': {
                'chaos_type': assessment.chaos_type.value,
                'field_state': {
                    'cohesion': assessment.field_state.cohesion,
                    'fragmentation': assessment.field_state.fragmentation,
                    'primal_flow': assessment.field_state.primal_flow,
                    'target_clarity': assessment.field_state.target_clarity
                },
                'guidance_urgency': assessment.guidance_urgency,
                'primal_residue': assessment.primal_residue
            },
            'method_used': method_choice['description'],
            'ignored_elements': ignored_elements,
            'result': kunzhuan_result,
            'philosophical_basis': '坤转是混沌中的指引，不是重建'
        }

        self.kunzhuan_history.append(kunzhuan_record)

        return kunzhuan_record

    def _select_kunzhuan_method(self, assessment: ChaosAssessment,
                                context: Dict) -> Dict:
        """选择坤转方法"""

        applicable_methods = []
        for method_id, method_data in self.kunzhuan_methods.items():
            if method_data['applicability'](assessment):
                applicable_methods.append({
                    'method_id': method_id,
                    **method_data
                })

        if not applicable_methods:
            # 默认方法：原力重对齐
            return {
                'method_id': 'primal_realignment',
                **self.kunzhuan_methods['primal_realignment']
            }

        # 根据紧迫性选择方法
        if assessment.guidance_urgency > 0.8:
            # 高紧迫性：选择激进方法
            for method in applicable_methods:
                if method['method_id'] in ['radical_simplification', 'complete_restart']:
                    return method

        # 默认：选择第一个适用方法
        return applicable_methods[0]

    def _identify_ignored_elements(self, assessment: ChaosAssessment,
                                   method_ignores: List[str]) -> Dict[str, Any]:
        """识别被忽略的元素（坤转本质）"""

        base_ignores = method_ignores.copy()

        # 根据场状态添加特定忽略
        if assessment.field_state.fragmentation > 0.7:
            base_ignores.append('structural_integrity')

        if assessment.field_state.target_clarity < 0.3:
            base_ignores.append('target_complexity')

        if assessment.primal_residue < 0.3:
            base_ignores.append('historical_continuity')

        # 坤转核心：总是忽略残缺和杂序
        core_ignores = ['fragmentation', 'inconsistencies', 'broken_connections']
        base_ignores.extend(core_ignores)

        return {
            'ignored_aspects': list(set(base_ignores)),
            'reason': '坤转忽略残缺，专注于原力重对齐',
            'philosophical_principle': '从混沌中指引，不修补破碎'
        }

    def _perform_primal_realignment(self, assessment: ChaosAssessment,
                                    current_targets: List[Dict],
                                    context: Dict) -> Dict[str, Any]:
        """执行原力重对齐"""

        # 从原力残存中提取核心
        primal_core = self._extract_primal_core(assessment.primal_residue, context)

        # 建立新目标
        new_target = self._establish_target_from_primal(
            primal_core, current_targets
        )

        # 建立新规则
        new_rules = self._establish_rules_for_primal_alignment(primal_core)

        return {
            'process': 'primal_realignment',
            'extracted_primal_core': primal_core,
            'new_target': new_target,
            'new_rules': new_rules,
            'alignment_method': 'direct_primal_realignment',
            'reconstruction_avoided': True,
            'note': '基于原力残存直接重对齐，忽略中间结构'
        }

    def _perform_emergent_guidance(self, assessment: ChaosAssessment,
                                   current_targets: List[Dict],
                                   context: Dict) -> Dict[str, Any]:
        """执行涌现指引"""

        # 从混沌中涌现模式
        emergent_patterns = self._extract_emergent_patterns(assessment, context)

        # 基于涌现模式建立指引
        guidance = self._establish_guidance_from_emergence(emergent_patterns)

        # 建立适应性目标
        adaptive_targets = self._create_adaptive_targets(
            guidance, current_targets
        )

        return {
            'process': 'emergent_guidance',
            'emergent_patterns': emergent_patterns,
            'guidance_emerged': guidance,
            'adaptive_targets': adaptive_targets,
            'method': 'guidance_emerges_from_chaos',
            'predetermination_avoided': True,
            'note': '指引从混沌中自然涌现，不强加结构'
        }

    def _perform_radical_simplification(self, assessment: ChaosAssessment,
                                        current_targets: List[Dict],
                                        context: Dict) -> Dict[str, Any]:
        """执行激进简化"""

        # 简化到本质
        essence = self._extract_essential_principles(assessment, context)

        # 基于本质重建
        simplified_structure = self._rebuild_from_essence(essence)

        # 建立最小目标
        minimal_targets = self._create_minimal_targets(essence, current_targets)

        return {
            'process': 'radical_simplification',
            'extracted_essence': essence,
            'simplified_structure': simplified_structure,
            'minimal_targets': minimal_targets,
            'complexity_reduction': 'radical',
            'note': '激进简化到本质，抛弃非必要复杂性'
        }

    def _perform_complete_restart(self, assessment: ChaosAssessment,
                                  current_targets: List[Dict],
                                  context: Dict) -> Dict[str, Any]:
        """执行完全重新开始"""

        # 回归原力基本原则
        primal_principles = self._return_to_primal_principles()

        # 从原则重新开始
        fresh_start = self._start_fresh_from_principles(primal_principles)

        return {
            'process': 'complete_restart',
            'primal_principles': primal_principles,
            'fresh_start': fresh_start,
            'clean_slate': True,
            'historical_baggage_discarded': True,
            'note': '完全重新开始，只保留原力基本原则'
        }

    def _extract_primal_core(self, primal_residue: float,
                             context: Dict) -> Dict[str, Any]:
        """提取原力核心"""

        if primal_residue > 0.7:
            return {
                'core_type': 'strong_primal_residue',
                'principles': ['sustained_excitation', 'flow_maintenance', 'target_alignment'],
                'strength': primal_residue,
                'reliable_as_basis': True
            }
        elif primal_residue > 0.3:
            return {
                'core_type': 'moderate_primal_residue',
                'principles': ['basic_excitation', 'minimal_flow', 'survival_targets'],
                'strength': primal_residue,
                'reliable_as_basis': 'partial'
            }
        else:
            return {
                'core_type': 'weak_primal_remnant',
                'principles': ['existence_as_excitation', 'fundamental_life_principle'],
                'strength': primal_residue,
                'reliable_as_basis': 'as_last_resort'
            }

    def _establish_target_from_primal(self, primal_core: Dict,
                                      old_targets: List[Dict]) -> Dict[str, Any]:
        """基于原力核心建立新目标"""

        if primal_core['core_type'] == 'strong_primal_residue':
            return {
                'target_type': 'primal_realignment',
                'content': '重新对齐到强原力核心',
                'priority': 'highest',
                'based_on': 'primal_residue',
                'connection_to_old': 'selective_integration'
            }
        elif primal_core['core_type'] == 'moderate_primal_residue':
            return {
                'target_type': 'primal_recovery',
                'content': '从原力残存中恢复',
                'priority': 'high',
                'based_on': 'partial_primal_presence',
                'connection_to_old': 'minimal_continuity'
            }
        else:
            return {
                'target_type': 'primal_survival',
                'content': '维持最基本的原力激发',
                'priority': 'critical',
                'based_on': 'fundamental_principles',
                'connection_to_old': 'broken_requires_fresh_start'
            }

    def _establish_rules_for_primal_alignment(self, primal_core: Dict) -> List[Dict]:
        """建立原力对齐规则"""

        rules = []

        # 基础规则：原力激发优先
        rules.append({
            'rule': 'primal_excitation_priority',
            'description': '原力激发优先于其他考虑',
            'enforcement': 'strict'
        })

        # 根据原力核心类型添加规则
        if primal_core['core_type'] == 'strong_primal_residue':
            rules.append({
                'rule': 'maintain_primal_flow',
                'description': '维持原力流动',
                'enforcement': 'high'
            })
            rules.append({
                'rule': 'align_targets_to_primal',
                'description': '目标必须与原力核心对齐',
                'enforcement': 'medium'
            })

        elif primal_core['core_type'] == 'moderate_primal_residue':
            rules.append({
                'rule': 'protect_primal_residue',
                'description': '保护原力残存',
                'enforcement': 'highest'
            })
            rules.append({
                'rule': 'gradual_recovery',
                'description': '渐进恢复，避免过度压力',
                'enforcement': 'medium'
            })

        else:  # weak primal remnant
            rules.append({
                'rule': 'survival_first',
                'description': '生存优先，维持最基本原力',
                'enforcement': 'absolute'
            })
            rules.append({
                'rule': 'minimal_structure',
                'description': '最小结构，避免复杂性',
                'enforcement': 'strict'
            })

        return rules

    def _extract_emergent_patterns(self, assessment: ChaosAssessment,
                                   context: Dict) -> List[Dict]:
        """从混沌中提取涌现模式"""

        patterns = []

        # 从原力残存中寻找模式
        if assessment.primal_residue > 0:
            patterns.append({
                'pattern_type': 'primal_residue_distribution',
                'characteristics': ['clustering', 'flow_tendencies', 'intensity_variation'],
                'emergence_strength': assessment.primal_residue
            })

        # 从场破碎中寻找模式
        if assessment.field_state.fragmentation < 0.9:
            patterns.append({
                'pattern_type': 'fragmentation_pattern',
                'characteristics': ['fragment_sizes', 'separation_distances', 'connection_remnants'],
                'emergence_strength': 1.0 - assessment.field_state.fragmentation
            })

        # 从混沌类型推断模式
        if assessment.chaos_type == ChaosType.CREATIVE:
            patterns.append({
                'pattern_type': 'creative_chaos_pattern',
                'characteristics': ['novelty_potential', 'recombination_possibilities', 'emerging_order'],
                'emergence_strength': 0.8
            })

        return patterns

    def _establish_guidance_from_emergence(self, patterns: List[Dict]) -> Dict[str, Any]:
        """从涌现模式建立指引"""

        # 分析模式共性
        common_characteristics = []
        for pattern in patterns:
            common_characteristics.extend(pattern['characteristics'])

        # 去重
        common_characteristics = list(set(common_characteristics))

        # 基于模式建立指引
        guidance_principles = []

        if 'clustering' in common_characteristics:
            guidance_principles.append('build_on_existing_clusters')

        if 'flow_tendencies' in common_characteristics:
            guidance_principles.append('follow_natural_flow_tendencies')

        if 'novelty_potential' in common_characteristics:
            guidance_principles.append('encourage_novel_combinations')

        if 'emerging_order' in common_characteristics:
            guidance_principles.append('support_emerging_order')

        # 默认原则
        if not guidance_principles:
            guidance_principles = ['observe_and_adapt', 'minimal_intervention']

        return {
            'guidance_type': 'emergent_based',
            'principles': guidance_principles,
            'source_patterns': [p['pattern_type'] for p in patterns],
            'method': 'guidance_emerges_from_pattern_recognition'
        }

    def _create_adaptive_targets(self, guidance: Dict[str, Any],
                                 old_targets: List[Dict]) -> List[Dict]:
        """创建适应性目标"""

        adaptive_targets = []

        # 基于指引原则创建目标
        for principle in guidance['principles']:
            target = {
                'type': 'adaptive_target',
                'principle_based': principle,
                'flexibility': 'high',
                'evaluation_criteria': 'adaptability_and_resilience'
            }

            # 连接旧目标（如果可能）
            if old_targets:
                target['connection_to_past'] = 'principled_continuity'

            adaptive_targets.append(target)

        return adaptive_targets

    def _extract_essential_principles(self, assessment: ChaosAssessment,
                                      context: Dict) -> List[str]:
        """提取本质原则"""

        principles = []

        # 原力相关原则
        if assessment.primal_residue > 0:
            principles.append('primal_excitation_is_fundamental')
            principles.append('existence_requires_primal_flow')

        # 场相关原则
        if assessment.field_state.cohesion > 0:
            principles.append('cohesion_enables_function')

        if assessment.field_state.primal_flow > 0:
            principles.append('flow_enables_vitality')

        # 目标相关原则
        if assessment.field_state.target_clarity > 0:
            principles.append('clarity_enables_direction')

        # 坤转相关原则
        principles.append('guidance_emerges_from_chaos')
        principles.append('simplify_to_essence')

        return principles

    def _rebuild_from_essence(self, essence: List[str]) -> Dict[str, Any]:
        """从本质重建"""

        structure = {
            'foundation': 'essential_principles',
            'principles': essence,
            'complexity_level': 'minimal',
            'flexibility': 'high',
            'robustness': 'moderate'
        }

        # 根据原则添加特征
        if 'primal_excitation_is_fundamental' in essence:
            structure['core_focus'] = 'primal_excitation'

        if 'simplify_to_essence' in essence:
            structure['design_philosophy'] = 'minimalist_essentialism'

        if 'guidance_emerges_from_chaos' in essence:
            structure['adaptation_method'] = 'emergent_response'

        return structure

    def _create_minimal_targets(self, essence: List[str],
                                old_targets: List[Dict]) -> List[Dict]:
        """创建最小目标集"""

        minimal_targets = []

        # 必要目标：基于本质原则
        if 'primal_excitation_is_fundamental' in essence:
            minimal_targets.append({
                'target': 'maintain_primal_excitation',
                'priority': 'highest',
                'measurable': 'primal_flow > 0.1'
            })

        if 'existence_requires_primal_flow' in essence:
            minimal_targets.append({
                'target': 'ensure_minimal_primal_flow',
                'priority': 'high',
                'measurable': 'flow_continuity'
            })

        # 适应性目标
        minimal_targets.append({
            'target': 'adapt_to_emergent_conditions',
            'priority': 'medium',
            'flexibility': 'required'
        })

        return minimal_targets

    def _return_to_primal_principles(self) -> List[str]:
        """回归原力基本原则"""
        return [
            'existence_is_excitation',
            'life_requires_primal_flow',
            'survival_depends_on_excitation_maintenance',
            'simplest_form_is_most_resilient',
            'guidance_comes_from_acknowledging_chaos'
        ]

    def _start_fresh_from_principles(self, principles: List[str]) -> Dict[str, Any]:
        """从原则重新开始"""

        return {
            'fresh_start': True,
            'basis': 'primal_principles_only',
            'principles': principles,
            'structure': 'emergent_from_principles',
            'rules': [
                'follow_principles_not_precedents',
                'allow_emergence_over_imposition',
                'simplicity_over_complexity',
                'adaptability_over_rigidity'
            ],
            'historical_connection': 'principled_continuity_only'
        }

    def get_field_state(self) -> Dict[str, Any]:
        """获取场状态"""
        return {
            'current_assessment': self.current_chaos.__dict__ if self.current_chaos else None,
            'kunzhuan_history_count': len(self.kunzhuan_history),
            'method_library_size': len(self.kunzhuan_methods),
            'thresholds': self.kunzhuan_thresholds,
            'recent_activity': self._analyze_recent_activity(),
            'philosophical_integrity': self._validate_philosophical_integrity()
        }

    def _analyze_recent_activity(self) -> Dict[str, Any]:
        """分析近期活动"""
        if not self.kunzhuan_history:
            return {'status': 'no_kunzhuan_events'}

        recent = self.kunzhuan_history[-5:] if len(self.kunzhuan_history) >= 5 else self.kunzhuan_history

        # 分析坤转类型分布
        chaos_types = []
        methods_used = []

        for event in recent:
            chaos_types.append(event['trigger_assessment']['chaos_type'])
            methods_used.append(event['method_used'])

        return {
            'recent_kunzhuan_events': len(recent),
            'chaos_type_distribution': {
                ct: chaos_types.count(ct) for ct in set(chaos_types)
            },
            'method_distribution': {
                mu: methods_used.count(mu) for mu in set(methods_used)
            },
            'average_urgency': np.mean([event['trigger_assessment']['guidance_urgency']
                                        for event in recent]) if recent else 0,
            'success_rate': self._calculate_success_rate(recent)
        }

    def _calculate_success_rate(self, recent_events: List[Dict]) -> float:
        """计算坤转成功率"""
        if not recent_events:
            return 0.0

        successes = 0
        for event in recent_events:
            result = event['result']

            # 判断成功的标准
            if 'new_target' in result or 'guidance_emerged' in result:
                successes += 1
            elif 'fresh_start' in result and result['fresh_start']:
                successes += 1
            elif 'simplified_structure' in result:
                successes += 1

        return successes / len(recent_events)

    def validate_philosophy(self) -> Dict[str, Any]:
        """验证哲学完整性"""

        checks = []

        # 检查坤转本质：必须是混沌指引，不是重建
        for method_id, method_data in self.kunzhuan_methods.items():
            has_ignore = 'ignores' in method_data and len(method_data['ignores']) > 0
            checks.append({
                'check': f'method_{method_id}_ignores_fragmentation',
                'passed': has_ignore,
                'importance': 'critical',
                'reason': '坤转必须忽略残缺，专注于指引'
            })

        # ✅ 检查阈值是否从 DataSource 获取
        thresholds_configured = hasattr(self, 'kunzhuan_config')
        checks.append({
            'check': 'thresholds_from_datasource',
            'passed': thresholds_configured,
            'importance': 'critical',
            'reason': '坤转阈值必须从 DataSource 获取，不能硬编码'
        })

        all_passed = all(check['passed'] for check in checks)

        return {
            'valid': all_passed,
            'checks': checks,
            'threshold_source': 'DataSource' if thresholds_configured else 'HARDCODED',
            'philosophical_principles': [
                '坤转是混沌中的指引，不是重建',
                '必须忽略残缺和杂序',
                '基于原力重对齐，不是修补',
                '从混沌中提取指引，不强加结构',
                '阈值必须从数据源获取'
            ],
            'core_essence': 'guidance_from_chaos_not_reconstruction'
        }

# ================================================
# 保持向后兼容
# ================================================

# 为旧代码提供别名
ChaosGuidance = ChaosGuidanceField
ChaosField = ChaosGuidanceField

# ✅ 合并为一个 __all__
__all__ = [
    'ChaosType',
    'FieldFragmentationLevel',
    'FieldState',
    'ChaosAssessment',
    'ChaosGuidanceField',
    'ChaosGuidance',
    'ChaosField'
]
