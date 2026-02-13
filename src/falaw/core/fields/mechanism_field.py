import random
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from falaw.core.data_source import get_data_source


class MechanismCorrespondenceField:
    def __init__(self, config=None):
        self.data = get_data_source(config)
        # ... 其余初始化代码 ...

    def validate_philosophy(self):
        """验证哲学完整性"""
        return {
            'valid': True,
            'philosophical_basis': 'all_phenomena_have_mechanisms',
            'data_source_connected': hasattr(self, 'data'),
            'details': {
                'principle': '机制对应场',
                'implementation': '所有现象均有秩法元素解释路径',
                'registry_size': len(getattr(self, 'registry', {}))
            }
        }

class ExplanationConfidence(Enum):
    """解释置信度"""
    HIGH = 0.9
    MEDIUM = 0.6
    LOW = 0.3
    FALLBACK = 0.1


@dataclass
class Mechanism:
    """机制定义"""
    mechanism_id: str
    name: str
    description: str

    # 能解释的现象
    phenomena: List[str]

    # 解释逻辑
    logic: str
    primal_basis: str  # 如何连接到原力激发

    # 验证函数：判断机制是否适用于给定上下文
    validation_function: Callable[[Dict], bool]

    # 解释生成函数：为现象生成具体解释
    explanation_function: Callable[[Dict, Dict], Dict]

    # 参数
    parameters: Dict[str, Any] = field(default_factory=dict)

    # 相关机制
    related_mechanisms: List[str] = field(default_factory=list)

    # 坤转含义
    kunzhuan_implications: Optional[str] = None

    def explain(self, phenomenon: Dict, context: Dict) -> Dict[str, Any]:
        """为现象生成解释"""
        if not self.validation_function(context):
            return None

        base_explanation = self.explanation_function(phenomenon, context)

        return {
            'mechanism_id': self.mechanism_id,
            'mechanism_name': self.name,
            'explanation': base_explanation,
            'logic': self.logic,
            'primal_basis': self.primal_basis,
            'confidence': self._calculate_confidence(context),
            'applicability_score': self._calculate_applicability(context),
            'parameters_used': self._extract_used_parameters(context),
            'kunzhuan_related': self.kunzhuan_implications is not None
        }

    def _calculate_confidence(self, context: Dict) -> float:
        """计算置信度"""
        # 基于上下文匹配度
        match_factors = []

        if 'phenomenon_intensity' in context:
            intensity = context['phenomenon_intensity']
            match_factors.append(1.0 - abs(intensity - 0.5))  # 中等强度最可信

        if 'primal_present' in context:
            match_factors.append(1.0 if context['primal_present'] else 0.3)

        if match_factors:
            base_confidence = np.mean(match_factors)
        else:
            base_confidence = 0.7

        # 调整到最近的置信度等级
        levels = [c.value for c in ExplanationConfidence]
        closest = min(levels, key=lambda x: abs(x - base_confidence))

        return closest

    def _calculate_applicability(self, context: Dict) -> float:
        """计算适用性分数"""
        # 简单实现：基于验证函数返回值的置信度
        try:
            if self.validation_function(context):
                return 0.8 + random.uniform(-0.1, 0.1)
            else:
                return 0.2 + random.uniform(-0.1, 0.1)
        except:
            return 0.5

    def _extract_used_parameters(self, context: Dict) -> Dict[str, Any]:
        """提取使用的参数"""
        used = {}
        for param, default in self.parameters.items():
            if param in context:
                used[param] = context[param]
            else:
                used[param] = default
        return used


class MechanismRegistry:
    """机制注册表"""

    def __init__(self):
        self.mechanisms: Dict[str, Mechanism] = {}
        self.phenomenon_index: Dict[str, List[str]] = {}  # 现象->机制映射

        # 初始化内置机制
        self._initialize_builtin_mechanisms()

    def _initialize_builtin_mechanisms(self):
        """初始化内置机制"""

        # 1. 原力激发基础机制
        primal_mechanism = Mechanism(
            mechanism_id="primal_excitation_core",
            name="原力激发核心机制",
            description="所有现象都是原力激发的表现",
            phenomena=["*"],  # 通配符，匹配所有现象
            logic="存在即原力激发，任何现象都是原力激发的某种形式",
            primal_basis="直接连接到原力激发原理",
            validation_function=lambda ctx: True,  # 总是适用
            explanation_function=lambda phen, ctx: {
                'core_interpretation': f"现象{phen.get('name', '')}是原力激发的表现",
                'primal_form': self._determine_primal_form(phen, ctx),
                'excitation_level': ctx.get('primal_intensity', 0.5),
                'universality': "所有现象都基于原力激发"
            },
            parameters={
                'primal_form_detection': 'auto',
                'excitation_threshold': 0.05
            }
        )

        self.register_mechanism(primal_mechanism)

        # 2. 生存竞争机制
        survival_mechanism = Mechanism(
            mechanism_id="survival_competition",
            name="生存竞争机制",
            description="通过竞争实现生存目标",
            phenomena=["competition", "predation", "resource_scarcity", "war"],
            logic="生存是最基本的目标，竞争是追求生存目标的手段",
            primal_basis="生存需求驱动原力激发，竞争增强原力流动",
            validation_function=lambda ctx: ctx.get('involves_survival', False) or
                                            ctx.get('resource_related', False),
            explanation_function=lambda phen, ctx: {
                'survival_goal': "个体或集体生存",
                'competitive_method': self._determine_competitive_method(phen, ctx),
                'primal_outcome': "竞争增强原力激发强度",
                'target_pursuit_nature': "竞争是目标追求的特殊形式",
                'elimination_possibility': ctx.get('elimination_possible', False)
            },
            parameters={
                'survival_priority': 'highest',
                'competition_intensity': 0.7
            },
            kunzhuan_implications="生存竞争失败可能导致场无法维持"
        )

        self.register_mechanism(survival_mechanism)

        # 3. 合作协同机制
        cooperation_mechanism = Mechanism(
            mechanism_id="cooperation_synergy",
            name="合作协同机制",
            description="通过合作实现集体目标",
            phenomena=["cooperation", "symbiosis", "social_organization", "trade"],
            logic="合作能更有效地追求集体目标，产生原力协同效应",
            primal_basis="合作创造原力流动网络，增强总体原力激发",
            validation_function=lambda ctx: ctx.get('involves_multiple_agents', False) and
                                            ctx.get('mutual_benefit_possible', True),
            explanation_function=lambda phen, ctx: {
                'collective_goal': "共同目标或互惠利益",
                'synergy_level': self._calculate_synergy(ctx),
                'primal_network': "合作形成原力流动网络",
                'field_strengthening': "合作增强场凝聚力",
                'long_term_stability': ctx.get('long_term', False)
            },
            parameters={
                'synergy_factor': 0.8,
                'trust_requirement': 0.6
            }
        )

        self.register_mechanism(cooperation_mechanism)

        # 4. 创新突破机制
        innovation_mechanism = Mechanism(
            mechanism_id="innovation_breakthrough",
            name="创新突破机制",
            description="通过创新打破现有模式",
            phenomena=["innovation", "discovery", "revolution", "paradigm_shift"],
            logic="创新创造新的原力激发路径，突破现有限制",
            primal_basis="创新释放被抑制的原力，创造新的激发可能性",
            validation_function=lambda ctx: ctx.get('novelty_level', 0) > 0.5 or
                                            ctx.get('breakthrough_possible', False),
            explanation_function=lambda phen, ctx: {
                'breakthrough_type': self._determine_breakthrough_type(phen),
                'old_constraints': "突破原有模式限制",
                'new_possibilities': "创造新的原力激发路径",
                'primal_unlocking': "释放被抑制的原力潜能",
                'kunzhuan_connection': "创新可能引发或防止坤转"
            },
            parameters={
                'novelty_threshold': 0.7,
                'risk_level': 0.5
            },
            kunzhuan_implications="创新可能导致场重构，类似温和坤转"
        )

        self.register_mechanism(innovation_mechanism)

        # 5. 适应性演化机制
        adaptation_mechanism = Mechanism(
            mechanism_id="adaptive_evolution",
            name="适应性演化机制",
            description="通过适应环境变化而演化",
            phenomena=["adaptation", "learning", "evolution", "cultural_change"],
            logic="适应是维持原力激发的必要调整",
            primal_basis="适应性变化维持原力激发在变化环境中的持续性",
            validation_function=lambda ctx: ctx.get('environment_changing', False) or
                                            ctx.get('adaptation_needed', False),
            explanation_function=lambda phen, ctx: {
                'adaptation_pressure': ctx.get('environmental_pressure', 0.5),
                'adaptive_response': self._determine_adaptive_response(phen, ctx),
                'primal_maintenance': "适应维持原力激发水平",
                'evolutionary_trajectory': "向更高原力激发效率演化",
                'resilience_enhancement': True
            },
            parameters={
                'adaptation_speed': 0.5,
                'learning_capacity': 0.7
            }
        )

        self.register_mechanism(adaptation_mechanism)

    def _determine_primal_form(self, phenomenon: Dict, context: Dict) -> str:
        """确定原力形式"""
        forms = [
            "直接激发", "间接表达", "冲突形式", "协同形式",
            "抑制状态", "释放状态", "转化过程", "循环流动"
        ]

        # 基于现象特征选择
        if context.get('intensity', 0) > 0.7:
            return random.choice(["直接激发", "释放状态", "冲突形式"])
        elif context.get('cooperative', False):
            return random.choice(["协同形式", "循环流动"])
        elif context.get('transformative', False):
            return "转化过程"
        else:
            return random.choice(forms)

    def _determine_competitive_method(self, phenomenon: Dict, context: Dict) -> str:
        """确定竞争方法"""
        methods = [
            "资源竞争", "空间竞争", "配偶竞争", "地位竞争",
            "知识竞争", "影响力竞争", "生存权竞争"
        ]

        if phenomenon.get('name') == 'war':
            return "生存权竞争"
        elif 'resource' in str(phenomenon.get('name', '')).lower():
            return "资源竞争"
        else:
            return random.choice(methods)

    def _calculate_synergy(self, context: Dict) -> float:
        """计算协同效应"""
        base = 0.5
        if context.get('trust_level', 0) > 0.7:
            base += 0.2
        if context.get('complementarity', 0) > 0.6:
            base += 0.2
        if context.get('communication_quality', 0) > 0.5:
            base += 0.1

        return min(1.0, base)

    def _determine_breakthrough_type(self, phenomenon: Dict) -> str:
        """确定突破类型"""
        types = [
            "技术突破", "认知突破", "社会突破", "文化突破",
            "组织突破", "范式突破", "方法突破"
        ]

        name = str(phenomenon.get('name', '')).lower()
        if 'tech' in name or 'invent' in name:
            return "技术突破"
        elif 'learn' in name or 'discover' in name:
            return "认知突破"
        elif 'social' in name or 'cultural' in name:
            return "社会突破"
        else:
            return random.choice(types)

    def _determine_adaptive_response(self, phenomenon: Dict, context: Dict) -> str:
        """确定适应性响应"""
        responses = [
            "行为调整", "结构改变", "策略优化", "能力发展",
            "关系重构", "目标修正", "价值调整"
        ]

        pressure = context.get('environmental_pressure', 0.5)
        if pressure > 0.7:
            return random.choice(["结构改变", "关系重构", "价值调整"])
        elif pressure > 0.4:
            return random.choice(["策略优化", "能力发展", "目标修正"])
        else:
            return "行为调整"

    def register_mechanism(self, mechanism: Mechanism):
        """注册机制"""
        if mechanism.mechanism_id in self.mechanisms:
            raise ValueError(f"机制ID已存在: {mechanism.mechanism_id}")

        self.mechanisms[mechanism.mechanism_id] = mechanism

        # 更新现象索引
        for phenomenon in mechanism.phenomena:
            if phenomenon not in self.phenomenon_index:
                self.phenomenon_index[phenomenon] = []

            if mechanism.mechanism_id not in self.phenomenon_index[phenomenon]:
                self.phenomenon_index[phenomenon].append(mechanism.mechanism_id)

    def find_mechanisms_for_phenomenon(self, phenomenon_name: str) -> List[Mechanism]:
        """查找能解释现象的机制"""
        mechanism_ids = []

        # 精确匹配
        if phenomenon_name in self.phenomenon_index:
            mechanism_ids.extend(self.phenomenon_index[phenomenon_name])

        # 通配符匹配
        if "*" in self.phenomenon_index:
            mechanism_ids.extend(self.phenomenon_index["*"])

        # 去重
        mechanism_ids = list(set(mechanism_ids))

        return [self.mechanisms[mid] for mid in mechanism_ids if mid in self.mechanisms]

    def explain_phenomenon(self, phenomenon: Dict, context: Dict) -> List[Dict[str, Any]]:
        """为现象生成所有可能的解释"""
        explanations = []

        # 查找适用的机制
        mechanisms = self.find_mechanisms_for_phenomenon(phenomenon.get('name', ''))

        for mechanism in mechanisms:
            explanation = mechanism.explain(phenomenon, context)
            if explanation:
                explanations.append(explanation)

        # 如果没有任何解释，使用后备系统
        if not explanations:
            explanations = self._generate_fallback_explanations(phenomenon, context)

        # 按置信度排序
        explanations.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        return explanations

    def _generate_fallback_explanations(self, phenomenon: Dict,
                                        context: Dict) -> List[Dict[str, Any]]:
        """生成后备解释"""
        fallbacks = []

        # 后备1：原力激发角度
        fallbacks.append({
            'mechanism_id': "fallback_primal",
            'mechanism_name': "原力激发后备解释",
            'explanation': {
                'interpretation': f"现象{phenomenon.get('name', '未知')}是原力激发的复杂表现",
                'primal_complexity': "现象可能涉及多层原力激发交互",
                'observation_note': "当前机制库需要扩展以更好解释此现象"
            },
            'logic': "所有现象最终都可追溯到原力激发",
            'primal_basis': "现象的存在证明原力激发的普遍性",
            'confidence': ExplanationConfidence.FALLBACK.value,
            'applicability_score': 0.5,
            'parameters_used': {'fallback_type': 'primal_universal'},
            'kunzhuan_related': False,
            'is_fallback': True
        })

        # 后备2：目标追求角度
        fallbacks.append({
            'mechanism_id': "fallback_target",
            'mechanism_name': "目标追求后备解释",
            'explanation': {
                'interpretation': f"现象{phenomenon.get('name', '未知')}涉及对某种目标的追求",
                'target_nature': "目标的具体性质需要进一步分析",
                'pursuit_method': "追求方法可能多样且复杂"
            },
            'logic': "所有行动都隐含某种目标追求",
            'primal_basis': "目标追求驱动原力激发",
            'confidence': ExplanationConfidence.FALLBACK.value,
            'applicability_score': 0.4,
            'parameters_used': {'fallback_type': 'target_universal'},
            'kunzhuan_related': False,
            'is_fallback': True
        })

        return fallbacks

    def analyze_coverage(self) -> Dict[str, Any]:
        """分析机制覆盖情况"""
        # 统计所有已注册现象
        all_phenomena = set()
        for mechanism in self.mechanisms.values():
            all_phenomena.update(mechanism.phenomena)

        # 计算通配符覆盖率
        wildcard_present = "*" in all_phenomena

        # 统计机制数量
        mechanism_count = len(self.mechanisms)

        # 计算平均每个现象的机制数
        phenomenon_mechanism_counts = []
        for phen in all_phenomena:
            if phen != "*":
                count = len(self.phenomenon_index.get(phen, []))
                phenomenon_mechanism_counts.append(count)

        avg_mechanisms_per_phenomenon = (
            np.mean(phenomenon_mechanism_counts) if phenomenon_mechanism_counts else 0
        )

        return {
            'total_mechanisms': mechanism_count,
            'covered_phenomena': len(all_phenomena) - (1 if wildcard_present else 0),
            'wildcard_mechanism_present': wildcard_present,
            'average_mechanisms_per_phenomenon': float(avg_mechanisms_per_phenomenon),
            'coverage_guarantee': "100% (通过后备系统)",
            'recommendations': self._generate_coverage_recommendations()
        }

    def _generate_coverage_recommendations(self) -> List[str]:
        """生成覆盖建议"""
        recommendations = []

        # 检查现象覆盖
        if "*" not in self.phenomenon_index:
            recommendations.append("添加通配符机制以确保100%覆盖")

        # 检查机制多样性
        mechanism_count = len(self.mechanisms)
        if mechanism_count < 10:
            recommendations.append(f"增加机制数量（当前{mechanism_count}个）")

        return recommendations


class MultiMechanismCorrespondenceField:
    """多机制对应场"""

    def __init__(self, registry: Optional[MechanismRegistry] = None):
        self.registry = registry or MechanismRegistry()

        # 解释历史
        self.explanation_history: List[Dict] = []

        # 共识形成记录
        self.consensus_history: List[Dict] = []

    def analyze_phenomenon(self, phenomenon: Dict, context: Dict) -> Dict[str, Any]:
        """分析现象，生成机制解释"""

        # 生成所有可能的解释
        explanations = self.registry.explain_phenomenon(phenomenon, context)

        # 分析解释模式
        explanation_patterns = self._analyze_explanation_patterns(explanations)

        # 记录历史
        record = {
            'phenomenon': phenomenon,
            'context': context,
            'explanations': explanations,
            'timestamp': 0.0,  # 实际应记录时间
            'primary_mechanism': explanations[0] if explanations else None,
            'explanation_count': len(explanations),
            'pattern_analysis': explanation_patterns
        }

        self.explanation_history.append(record)

        return record

    def _analyze_explanation_patterns(self, explanations: List[Dict]) -> Dict[str, Any]:
        """分析解释模式"""
        if not explanations:
            return {'status': 'no_explanations'}

        # 置信度分布
        confidence_levels = [exp.get('confidence', 0) for exp in explanations]

        # 机制类型分布
        mechanism_types = {}
        for exp in explanations:
            mech_id = exp.get('mechanism_id', 'unknown')
            mechanism_types[mech_id] = mechanism_types.get(mech_id, 0) + 1

        # 是否使用后备
        fallback_used = any(exp.get('is_fallback', False) for exp in explanations)

        # 坤转相关性
        kunzhuan_related = any(exp.get('kunzhuan_related', False) for exp in explanations)

        return {
            'total_explanations': len(explanations),
            'confidence_distribution': {
                'mean': float(np.mean(confidence_levels)),
                'std': float(np.std(confidence_levels)),
                'max': float(np.max(confidence_levels)),
                'min': float(np.min(confidence_levels))
            },
            'mechanism_distribution': mechanism_types,
            'fallback_used': fallback_used,
            'kunzhuan_related': kunzhuan_related,
            'consensus_possibility': self._assess_consensus_possibility(explanations)
        }

    def _assess_consensus_possibility(self, explanations: List[Dict]) -> Dict[str, Any]:
        """评估共识可能性"""
        if len(explanations) <= 1:
            return {'possible': True, 'reason': 'single_explanation'}

        # 检查解释间的一致性
        confidence_range = max(exp.get('confidence', 0) for exp in explanations) - \
                           min(exp.get('confidence', 0) for exp in explanations)

        # 检查机制互补性
        mechanism_ids = [exp.get('mechanism_id', '') for exp in explanations]
        unique_mechanisms = len(set(mechanism_ids))

        if confidence_range < 0.3 and unique_mechanisms <= 3:
            # 解释间差异小，容易形成共识
            return {
                'possible': True,
                'ease': 'easy',
                'method': 'select_highest_confidence'
            }
        elif any('fallback' in mid for mid in mechanism_ids):
            # 涉及后备解释，可能难以共识
            return {
                'possible': True,
                'ease': 'difficult',
                'method': 'require_additional_analysis',
                'note': 'fallback_explanations_present'
            }
        else:
            # 需要协调
            return {
                'possible': True,
                'ease': 'medium',
                'method': 'multi_mechanism_coordination',
                'recommendation': 'consider_synthesizing_multiple_perspectives'
            }

    def find_consensus(self, phenomenon: Dict, context: Dict,
                       proposed_consensus: Optional[Dict] = None,
                       alternative_approaches: Optional[List[str]] = None) -> Dict[str, Any]:
        """寻找共识"""

        # 获取所有解释
        analysis = self.analyze_phenomenon(phenomenon, context)
        explanations = analysis['explanations']

        # 如果没有解释，使用元共识
        if not explanations:
            return self._form_meta_consensus(phenomenon, context)

        # 尝试首选共识
        if proposed_consensus and self._validate_consensus(proposed_consensus, explanations):
            consensus_record = {
                'consensus': proposed_consensus,
                'method': 'proposed_accepted',
                'supporting_mechanisms': [exp['mechanism_id'] for exp in explanations
                                          if self._supports_consensus(exp, proposed_consensus)],
                'confidence': np.mean([exp.get('confidence', 0) for exp in explanations
                                       if self._supports_consensus(exp, proposed_consensus)]),
                'consensus_type': 'primary'
            }

            self.consensus_history.append(consensus_record)
            return consensus_record

        # 尝试替代方法
        if alternative_approaches:
            for approach in alternative_approaches:
                alt_consensus = self._generate_alternative_consensus(approach, explanations)
                if self._validate_consensus(alt_consensus, explanations):
                    consensus_record = {
                        'consensus': alt_consensus,
                        'method': f'alternative_{approach}',
                        'supporting_mechanisms': [exp['mechanism_id'] for exp in explanations
                                                  if self._supports_consensus(exp, alt_consensus)],
                        'confidence': np.mean([exp.get('confidence', 0) for exp in explanations
                                               if self._supports_consensus(exp, alt_consensus)]),
                        'consensus_type': 'alternative',
                        'approach_used': approach
                    }

                    self.consensus_history.append(consensus_record)
                    return consensus_record

        # 无法达成具体共识，建立新场
        new_field_consensus = self._establish_new_field_consensus(phenomenon, explanations)

        consensus_record = {
            'consensus': new_field_consensus,
            'method': 'new_field_creation',
            'new_field': new_field_consensus['new_field'],
            'reason': 'irreconcilable_differences',
            'consensus_type': 'meta',
            'agreement': 'agree_to_disagree_within_new_field'
        }

        self.consensus_history.append(consensus_record)
        return consensus_record

    def _validate_consensus(self, consensus: Dict, explanations: List[Dict]) -> bool:
        """验证共识的有效性"""
        # 至少需要一个机制支持
        supporting = [exp for exp in explanations
                      if self._supports_consensus(exp, consensus)]

        if not supporting:
            return False

        # 支持机制的置信度需要足够高
        avg_confidence = np.mean([exp.get('confidence', 0) for exp in supporting])

        return avg_confidence > 0.4 and len(supporting) >= 1

    def _supports_consensus(self, explanation: Dict, consensus: Dict) -> bool:
        """检查解释是否支持共识"""
        # 简单实现：检查机制ID是否在共识支持列表中
        mech_id = explanation.get('mechanism_id', '')
        consensus_mechanisms = consensus.get('supported_mechanisms', [])

        if consensus_mechanisms:
            return mech_id in consensus_mechanisms

        # 如果没有指定支持机制，检查逻辑兼容性
        explanation_logic = explanation.get('logic', '').lower()
        consensus_logic = consensus.get('logic', '').lower()

        # 简单关键词匹配
        common_words = set(explanation_logic.split()) & set(consensus_logic.split())
        return len(common_words) > 2

    def _form_meta_consensus(self, phenomenon: Dict, context: Dict) -> Dict[str, Any]:
        """形成元共识"""
        return {
            'consensus': {
                'content': f"关于现象{phenomenon.get('name', '')}需要进一步研究",
                'type': 'meta_consensus',
                'agreement': 'agree_on_need_for_more_analysis',
                'next_steps': ['extend_mechanism_library', 'gather_more_context']
            },
            'method': 'meta_consensus_formation',
            'reason': 'no_adequate_explanations_available',
            'consensus_type': 'procedural',
            'philosophical_basis': '承认无知也是共识的一种形式'
        }

    def _generate_alternative_consensus(self, approach: str,
                                        explanations: List[Dict]) -> Dict:
        """生成替代共识"""
        if approach == 'synthesis':
            # 综合多个解释
            return {
                'content': '综合多个角度的理解',
                'type': 'synthetic_consensus',
                'supported_mechanisms': [exp['mechanism_id'] for exp in explanations],
                'logic': '多重机制共同解释现象的复杂性',
                'synthesis_method': 'complementary_integration'
            }
        elif approach == 'pragmatic':
            # 实用主义共识
            highest_conf = max(explanations, key=lambda x: x.get('confidence', 0))
            return {
                'content': '采用最可信的解释作为工作共识',
                'type': 'pragmatic_consensus',
                'primary_mechanism': highest_conf['mechanism_id'],
                'logic': '在不确定中选择最可信的解释',
                'pragmatic_acceptance': 'tentative_acceptance'
            }
        elif approach == 'evolutionary':
            # 演化共识
            return {
                'content': '共识本身需要演化发展',
                'type': 'evolutionary_consensus',
                'logic': '共识随时间和新证据演化',
                'current_best': explanations[0]['mechanism_id'] if explanations else None,
                'open_to_revision': True
            }
        else:
            # 默认：选择最高置信度
            if explanations:
                best = max(explanations, key=lambda x: x.get('confidence', 0))
                return {
                    'content': f"采用{best['mechanism_name']}作为共识基础",
                    'type': 'confidence_based',
                    'primary_mechanism': best['mechanism_id'],
                    'confidence': best['confidence']
                }
            else:
                return {'content': '无法形成共识', 'type': 'failure'}

    def _establish_new_field_consensus(self, phenomenon: Dict,
                                       explanations: List[Dict]) -> Dict:
        """建立新场共识"""
        field_id = f"field_{phenomenon.get('name', 'unknown').lower()}_{len(self.consensus_history)}"

        # 收集不同观点
        divergent_views = []
        for exp in explanations:
            divergent_views.append({
                'mechanism': exp['mechanism_id'],
                'explanation': exp['explanation'],
                'confidence': exp['confidence']
            })

        return {
            'content': f"关于现象{phenomenon.get('name', '')}存在不可调和的分歧",
            'type': 'new_field_consensus',
            'new_field': {
                'field_id': field_id,
                'purpose': f"容纳对{phenomenon.get('name', '')}的不同解释",
                'divergent_views': divergent_views,
                'coexistence_principle': 'multiple_perspectives_coexist',
                'interaction_rules': 'respectful_engagement_with_differences'
            },
            'agreement': 'agree_to_disagree_within_structured_field',
            'philosophical_basis': '复杂现象可能需要在不同场中理解'
        }

    def get_field_state(self) -> Dict[str, Any]:
        """获取场状态"""
        return {
            'mechanism_count': len(self.registry.mechanisms),
            'explanation_history_count': len(self.explanation_history),
            'consensus_history_count': len(self.consensus_history),
            'coverage_analysis': self.registry.analyze_coverage(),
            'recent_activity': self._analyze_recent_activity(),
            'philosophical_integrity': self._validate_philosophical_integrity()
        }

    def _analyze_recent_activity(self) -> Dict[str, Any]:
        """分析近期活动"""
        if not self.explanation_history:
            return {'status': 'no_activity'}

        recent = self.explanation_history[-10:] if len(self.explanation_history) >= 10 else self.explanation_history

        phenomenon_names = [record['phenomenon'].get('name', 'unknown')
                            for record in recent]

        unique_phenomena = len(set(phenomenon_names))

        # 计算后备使用率
        fallback_usage = sum(1 for record in recent
                             if any(exp.get('is_fallback', False)
                                    for exp in record['explanations']))

        return {
            'recent_explanations': len(recent),
            'unique_phenomena_recent': unique_phenomena,
            'fallback_usage_rate': fallback_usage / len(recent) if recent else 0,
            'consensus_attempts': len([r for r in self.consensus_history[-5:]])
            if self.consensus_history else 0
        }

    def validate_philosophy(self) -> Dict[str, Any]:
        """验证哲学一致性（简化版）"""
        return {
            'valid': True,
            'philosophical_basis': 'phenomena_have_mechanisms',
            'details': {
                'principle': '现象必有机制对应',
                'implementation': '所有现象均存在可解释的机制'
            }
        }

    def extend_mechanism_library(self, new_mechanism_data: Dict) -> Dict[str, Any]:
        """扩展机制库"""
        try:
            # 创建新机制
            new_mechanism = Mechanism(
                mechanism_id=new_mechanism_data['mechanism_id'],
                name=new_mechanism_data['name'],
                description=new_mechanism_data['description'],
                phenomena=new_mechanism_data['phenomena'],
                logic=new_mechanism_data['logic'],
                primal_basis=new_mechanism_data['primal_basis'],
                validation_function=eval(new_mechanism_data['validation_function']),
                explanation_function=eval(new_mechanism_data['explanation_function']),
                parameters=new_mechanism_data.get('parameters', {}),
                related_mechanisms=new_mechanism_data.get('related_mechanisms', []),
                kunzhuan_implications=new_mechanism_data.get('kunzhuan_implications')
            )

            # 注册机制
            self.registry.register_mechanism(new_mechanism)

            return {
                'success': True,
                'mechanism_id': new_mechanism.mechanism_id,
                'phenomena_added': new_mechanism.phenomena,
                'total_mechanisms_now': len(self.registry.mechanisms)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'required_fields': [
                    'mechanism_id', 'name', 'description', 'phenomena',
                    'logic', 'primal_basis', 'validation_function',
                    'explanation_function'
                ]
            }

# ================================================
# 保持向后兼容
# ================================================

MechanismField = MultiMechanismCorrespondenceField

__all__ = [
    'ExplanationConfidence',
    'Mechanism',
    'MechanismRegistry',
    'MultiMechanismCorrespondenceField',
    'MechanismField'
]