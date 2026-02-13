import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from falaw.core.fields import (
    PrimalField,
    ChaosGuidanceField,
    IndividualCollectiveTargetField,  # ✅ 使用实际类名
    MechanismCorrespondenceField,
    CoordinationField
)

from falaw.models.entities import (
    Entity,
    Individual,
    Collective,
    PrimalValue,
    LifeState
)

from falaw.core.data_source import get_data_source


class FALawSimulator:
    def __init__(self, config=None):
        self.data = get_data_source(config)
        self.kunzhuan_config = self.data.get_kunzhuan_thresholds()
        # ... 移除所有硬编码的 DynamicsParameters ...

    def check_kunzhuan(self, element_states):
        """检查坤转条件——使用 DataSource 阈值"""
        thresholds = self.kunzhuan_config
        tension = self.data.get_tension(element_states)

        # 计算满足的条件数量
        conditions_met = 0
        # ... 你的坤转判断逻辑 ...

        return conditions_met >= thresholds['min_conditions']

class FALawSimulator:
    """秩法图统一模拟器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.simulation_id = self.config.get('simulation_id',
                                             f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # 初始化场系统
        self.fields = self._initialize_fields()

        # 初始化实体系统
        self.entities: Dict[str, Entity] = {}

        # 模拟状态
        self.current_step = 0
        self.start_time = None
        self.end_time = None
        self.running = False

        # 结果记录
        self.history: List[Dict[str, Any]] = []
        self.kunzhuan_events: List[Dict[str, Any]] = []
        self.elimination_events: List[Dict[str, Any]] = []

        # 性能统计
        self.stats = {
            'steps_completed': 0,
            'entities_created': 0,
            'entities_eliminated': 0,
            'kunzhuan_count': 0,
            'consensus_formed': 0,
            'primal_energy_generated': 0.0
        }

    def _initialize_fields(self) -> Dict[str, Any]:
        """初始化所有场"""
        fields = {}

        # 原力激发场
        fields['primal'] = PrimalField('primal_field', {
            'sensitivity': 0.8,
            'excitation_threshold': 0.05,
            'monitor_frequency': 1.0
        })

        # 目标追求场
        fields['target'] = TargetField('target_field', {
            'justification_required': True,
            'target_hierarchy': ['survival', 'resource', 'collective', 'primal'],
            'record_all_eliminations': True
        })

        # 机制对应场
        fields['mechanism'] = MechanismField({
            'require_fallback_system': True,
            'mechanism_library_size': 100,
            'explanation_completeness_required': 1.0
        })

        # 混沌指引场
        fields['chaos'] = ChaosGuidanceField({
            'trigger_condition': 'field_cannot_maintain',
            'method': 'guidance_from_chaos',
            'ignores': ['fragmentation', 'inconsistencies'],
            'basis': 'primal_excitation_realignment'
        })

        # 统筹协调场
        fields['coordination'] = CoordinationField('coordination_field', {
            'consensus_threshold': 0.7,
            'conflict_resolution': 'primal_priority',
            'kunzhuan_alert_threshold': 0.8
        })

        # 注册场到协调器
        field_ids = ['primal_field', 'target_field', 'mechanism_field', 'chaos_field']
        fields['coordination'].register_fields(field_ids)

        print(f"[Simulator] 初始化完成: {len(fields)} 个场")
        for field_name, field in fields.items():
            validation = field.validate_philosophy()
            status = "✅" if validation['valid'] else "❌"
            print(f"  {status} {field_name}: {validation.get('philosophical_basis', 'No basis')}")

        return fields

    def create_entity(self, entity_type: str, **kwargs) -> Entity:
        """创建新实体"""
        entity_id = kwargs.get('id', f"{entity_type}_{len(self.entities) + 1}")

        if entity_type.lower() == 'individual':
            entity = Individual(
                id=entity_id,
                name=kwargs.get('name', f"Individual_{entity_id}"),
                primal_strength=PrimalValue(kwargs.get('primal_strength', 0.5)),
                excitation_capacity=kwargs.get('excitation_capacity', 0.7)
            )

            # 如果有初始目标，添加到 current_targets
            initial_targets = kwargs.get('targets', ['survive', 'grow'])
            for target_content in initial_targets:
                entity.current_targets.append({
                    'type': 'initial',
                    'content': target_content,
                    'timestamp': 0.0
                })
        elif entity_type.lower() == 'collective':
            members = kwargs.get('members', [])
            if not members:
                # 自动创建成员
                members = [self.create_entity('individual', id=f"member_{i}")
                           for i in range(kwargs.get('min_members', 3))]

            entity = Collective(
                id=entity_id,
                name=kwargs.get('name', f"Collective_{entity_id}"),
                members=members,
                collective_primal=PrimalValue(kwargs.get('collective_primal', 0.6)),
                collective_targets=kwargs.get('collective_targets', ['maintain_cohesion', 'grow'])
            )
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")

        self.entities[entity_id] = entity
        self.stats['entities_created'] += 1

        print(f"[Simulator] 创建实体: {entity_id} ({entity_type})")
        return entity

    def run_scenario(self, scenario: Union[str, Dict[str, Any]],
                     steps: int = 100,
                     step_duration: float = 1.0) -> Dict[str, Any]:
        """运行模拟场景"""

        print("\n" + "=" * 70)
        print(f"秩法图模拟开始 | 场景: {scenario if isinstance(scenario, str) else 'custom'}")
        print(f"模拟ID: {self.simulation_id} | 步数: {steps}")
        print("=" * 70)

        self.start_time = datetime.now()
        self.running = True

        # 加载或解析场景
        scenario_data = self._load_scenario(scenario)

        # 初始设置
        self._setup_scenario(scenario_data)

        # 主模拟循环
        for step in range(steps):
            if not self.running:
                break

            self.current_step = step
            print(f"\n--- 步骤 {step + 1}/{steps} ---")

            # 执行步骤
            step_result = self._execute_step(step, scenario_data)
            self.history.append(step_result)

            # 检查模拟结束条件
            if self._check_termination_conditions(step_result):
                print(f"[Simulator] 模拟提前结束于步骤 {step + 1}")
                break

            # 短暂暂停（用于观察）
            if step_duration > 0:
                time.sleep(step_duration)

        # 模拟结束
        self.end_time = datetime.now()
        self.running = False

        # 生成最终报告
        final_report = self._generate_final_report()

        print("\n" + "=" * 70)
        print("模拟完成")
        print(f"总耗时: {(self.end_time - self.start_time).total_seconds():.2f}秒")
        print(
            f"实体状态: {len([e for e in self.entities.values() if e.life_state == LifeState.ALIVE])}存活 / {self.stats['entities_eliminated']}淘汰")
        print(f"坤转事件: {self.stats['kunzhuan_count']}次")
        print("=" * 70)

        return final_report

    def _load_scenario(self, scenario: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """加载或解析场景"""

        if isinstance(scenario, dict):
            return scenario

        # 内置场景
        builtin_scenarios = {
            'survival_competition': {
                'name': '生存竞争',
                'description': '多个实体竞争生存资源',
                'entities': [
                    {'type': 'individual', 'count': 5, 'primal_strength': 0.6},
                    {'type': 'collective', 'count': 2, 'min_members': 3}
                ],
                'phenomena': ['competition', 'cooperation', 'elimination'],
                'target_focus': 'survival',
                'duration': 50
            },
            'kunzhuan_preparation': {
                'name': '坤转准备',
                'description': '场逐渐失效，准备坤转',
                'entities': [
                    {'type': 'individual', 'count': 3, 'primal_strength': 0.4}
                ],
                'field_degradation': True,
                'kunzhuan_expected': True,
                'phenomena': ['field_failure', 'consensus_breakdown', 'chaos_emergence'],
                'duration': 30
            },
            'complex_interaction': {
                'name': '复杂交互',
                'description': '多实体、多现象的复杂交互',
                'entities': [
                    {'type': 'individual', 'count': 8, 'primal_strength': 0.5},
                    {'type': 'collective', 'count': 3, 'min_members': 4}
                ],
                'phenomena': ['competition', 'cooperation', 'elimination',
                              'field_interaction', 'consensus_formation'],
                'interaction_complexity': 'high',
                'duration': 100
            }
        }

        if scenario in builtin_scenarios:
            print(f"[Simulator] 加载内置场景: {builtin_scenarios[scenario]['name']}")
            return builtin_scenarios[scenario]

        # 尝试从文件加载
        scenario_path = Path(scenario)
        if scenario_path.exists():
            with open(scenario_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 默认场景
        print(f"[Simulator] 使用默认场景")
        return {
            'name': 'default',
            'description': '默认模拟场景',
            'entities': [{'type': 'individual', 'count': 3}],
            'phenomena': ['existence', 'interaction'],
            'duration': 20
        }

    def _setup_scenario(self, scenario_data: Dict[str, Any]):
        """设置场景初始状态"""

        print(f"[Simulator] 设置场景: {scenario_data.get('name', 'Unnamed')}")

        # 创建实体
        entity_specs = scenario_data.get('entities', [])
        for spec in entity_specs:
            entity_type = spec['type']
            count = spec.get('count', 1)

            for i in range(count):
                entity_id = f"{entity_type}_{len(self.entities) + 1}"
                self.create_entity(entity_type, id=entity_id, **spec)

        # 设置场参数
        if scenario_data.get('field_degradation'):
            # 故意降低场健康度以触发坤转
            for field in self.fields.values():
                field.coherence = 0.3
                field.stability = 0.4

        # 记录初始状态
        initial_state = {
            'step': 0,
            'timestamp': datetime.now().isoformat(),
            'entities_count': len(self.entities),
            'alive_entities': len([e for e in self.entities.values()
                                   if e.life_state == LifeState.ALIVE]),
            'field_states': {name: field.get_state() for name, field in self.fields.items()},
            'scenario': scenario_data.get('name', 'unknown')
        }

        self.history.append(initial_state)

        print(f"[Simulator] 初始状态: {initial_state['entities_count']}个实体, "
              f"{initial_state['alive_entities']}个存活")

    def _execute_step(self, step: int, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个模拟步骤"""

        step_start = datetime.now()
        step_events = []

        # 1. 更新实体状态
        entity_updates = self._update_entities(step)
        step_events.extend(entity_updates.get('events', []))

        # 2. 收集当前现象
        current_phenomena = self._collect_phenomena(step, scenario_data)

        # 3. 对每个现象进行场分析
        field_analyses = {}
        for phenomenon in current_phenomena:
            context = {
                'phenomenon': phenomenon,
                'step': step,
                'timestamp': datetime.now().isoformat(),
                'entities_state': self._get_entities_state_summary(),
                'scenario_context': scenario_data
            }

            # 各场分析
            for field_name, field in self.fields.items():
                if field_name == 'coordination':
                    continue  # 协调场最后分析

                analysis = field.analyze(context)
                field_analyses[f"{field_name}_{phenomenon}"] = analysis

        # 4. 协调场进行统一分析
        coordination_context = {
            'phenomena': current_phenomena,
            'step': step,
            'field_analyses': field_analyses,
            'entities_summary': self._get_entities_state_summary(),
            'scenario': scenario_data.get('name', 'unknown')
        }

        coordination_result = self.fields['coordination'].analyze(coordination_context)

        # 5. 检查坤转触发
        if coordination_result.get('kunzhuan_required', False):
            kunzhuan_event = self._trigger_kunzhuan(step, coordination_result)
            step_events.append(kunzhuan_event)
            self.kunzhuan_events.append(kunzhuan_event)
            self.stats['kunzhuan_count'] += 1

        # 6. 执行行动建议
        actions_executed = self._execute_actions(coordination_result.get('recommended_actions', []))

        # 7. 更新统计数据
        self._update_stats(entity_updates, coordination_result, actions_executed)

        # 构建步骤结果
        step_result = {
            'step': step + 1,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - step_start).total_seconds(),
            'entities_alive': len([e for e in self.entities.values()
                                   if e.life_state == LifeState.ALIVE]),
            'entities_total': len(self.entities),
            'phenomena_observed': current_phenomena,
            'coordination_result': {
                'consensus_achieved': coordination_result.get('consensus_achieved', False),
                'consensus_type': coordination_result.get('consensus_type', 'none'),
                'kunzhuan_required': coordination_result.get('kunzhuan_required', False),
                'field_health': coordination_result.get('field_health', {})
            },
            'events': step_events,
            'actions_executed': actions_executed,
            'stats_snapshot': self.stats.copy()
        }

        # 打印步骤摘要
        self._print_step_summary(step_result)

        return step_result

    def _update_entities(self, step: int) -> Dict[str, Any]:
        """更新所有实体状态"""
        events = []
        eliminations = []
        primal_energy = 0.0

        alive_entities = [e for e in self.entities.values()
                          if e.life_state == LifeState.ALIVE]

        for entity in alive_entities:
            # 实体原力激发
            if hasattr(entity, 'excite_primal'):
                excitation = entity.excite_primal()
                primal_energy += excitation.get('excitation_generated', 0.0)

                events.append({
                    'type': 'primal_excitation',
                    'entity': entity.id,
                    'excitation': excitation,
                    'step': step
                })

            # 实体目标追求
            if hasattr(entity, 'pursue_targets'):
                target_results = entity.pursue_targets()

                for result in target_results:
                    if result.get('type') == 'elimination' and result.get('eliminated_entity'):
                        # 记录消灭事件
                        elimination_event = {
                            'type': 'elimination',
                            'eliminator': entity.id,
                            'eliminated': result['eliminated_entity'],
                            'justification': result.get('justification', 'survival'),
                            'step': step,
                            'target_based': True
                        }

                        eliminations.append(elimination_event)
                        events.append(elimination_event)
                        self.elimination_events.append(elimination_event)

                        # 更新统计
                        self.stats['entities_eliminated'] += 1

            # 实体可能自然消亡
            if hasattr(entity, 'check_survival'):
                survival = entity.check_survival()
                if not survival['alive']:
                    events.append({
                        'type': 'natural_extinction',
                        'entity': entity.id,
                        'reason': survival.get('reason', 'primal_depletion'),
                        'step': step
                    })

        return {
            'events': events,
            'eliminations': eliminations,
            'primal_energy_generated': primal_energy,
            'alive_count': len(alive_entities) - len(eliminations)
        }

    def _collect_phenomena(self, step: int, scenario_data: Dict[str, Any]) -> List[str]:
        """收集当前步骤观察到的现象"""
        phenomena = []

        # 从场景中获取预设现象
        scenario_phenomena = scenario_data.get('phenomena', [])
        phenomena.extend(scenario_phenomena)

        # 从实体状态推断现象
        alive_count = len([e for e in self.entities.values()
                           if e.life_state == LifeState.ALIVE])

        if alive_count > 1:
            phenomena.append('interaction')

        if any(e for e in self.entities.values()
               if hasattr(e, 'collective_primal') and isinstance(e, Collective)):
            phenomena.append('collective_behavior')

        # 检查是否有消灭事件
        recent_eliminations = [e for e in self.elimination_events
                               if e.get('step', 0) >= step - 2]
        if recent_eliminations:
            phenomena.append('elimination')

        # 检查是否有坤转
        recent_kunzhuan = [k for k in self.kunzhuan_events
                           if k.get('step', 0) >= step - 2]
        if recent_kunzhuan:
            phenomena.append('kunzhuan_preparation')

        # 确保至少有基础现象
        if not phenomena:
            phenomena = ['existence', 'primal_manifestation']

        return list(set(phenomena))  # 去重

    def _get_entities_state_summary(self) -> Dict[str, Any]:
        """获取实体状态摘要"""
        alive_entities = [e for e in self.entities.values()
                          if e.life_state == LifeState.ALIVE]

        individuals = [e for e in alive_entities if isinstance(e, Individual)]
        collectives = [e for e in alive_entities if isinstance(e, Collective)]

        avg_primal = 0.0
        if alive_entities:
            primal_values = []
            for entity in alive_entities:
                if hasattr(entity, 'primal_strength'):
                    primal_values.append(entity.primal_strength.value)
                elif hasattr(entity, 'collective_primal'):
                    primal_values.append(entity.collective_primal.value)

            if primal_values:
                avg_primal = sum(primal_values) / len(primal_values)

        return {
            'total_alive': len(alive_entities),
            'individuals': len(individuals),
            'collectives': len(collectives),
            'avg_primal_strength': avg_primal,
            'recent_eliminations': len([e for e in self.elimination_events
                                        if e.get('step', 0) >= self.current_step - 3]),
            'recent_kunzhuan': len([k for k in self.kunzhuan_events
                                    if k.get('step', 0) >= self.current_step - 3])
        }

    def _trigger_kunzhuan(self, step: int, coordination_result: Dict[str, Any]) -> Dict[str, Any]:
        """触发坤转事件"""

        print(f"⚡️ [坤转触发] 步骤 {step + 1} - 场无法维持，寻求混沌指引")

        # 使用混沌场执行坤转
        chaos_context = {
            'trigger': 'field_cannot_maintain',
            'current_state': coordination_result,
            'step': step,
            'method': 'guidance_from_chaos',
            'ignores': ['fragmentation', 'inconsistencies'],
            'basis': 'primal_excitation_realignment'
        }

        kunzhuan_result = self.fields['chaos'].analyze(chaos_context)

        kunzhuan_event = {
            'type': 'kunzhuan',
            'step': step,
            'timestamp': datetime.now().isoformat(),
            'trigger': 'field_cannot_maintain',
            'method': 'guidance_from_chaos',
            'ignores': ['fragmentation', 'inconsistencies'],
            'basis': 'primal_excitation_realignment',
            'result': kunzhuan_result,
            'description': '从混沌中寻求新指引，不是重建旧秩序',
            'philosophical_basis': 'kunzhuan_is_guidance_not_reconstruction'
        }

        # 坤转影响：可能改变实体状态
        self._apply_kunzhuan_effects(kunzhuan_event)

        return kunzhuan_event

    def _apply_kunzhuan_effects(self, kunzhuan_event: Dict[str, Any]):
        """应用坤转效果"""
        # 坤转可能导致实体原力重对齐
        for entity in self.entities.values():
            if entity.life_state == LifeState.ALIVE:
                if hasattr(entity, 'primal_strength'):
                    # 随机调整原力值（模拟混沌指引）
                    adjustment = (np.random.random() - 0.5) * 0.3
                    entity.primal_strength.value = max(0.1, min(1.0,
                                                                entity.primal_strength.value + adjustment))

                elif hasattr(entity, 'collective_primal'):
                    adjustment = (np.random.random() - 0.5) * 0.2
                    entity.collective_primal.value = max(0.2, min(1.0,
                                                                  entity.collective_primal.value + adjustment))

        # 坤转后重置场警报
        self.fields['coordination'].kunzhuan_alert_level = 0.0
        self.fields['coordination'].field_failure_detected = False

    def _execute_actions(self, recommended_actions: List[str]) -> List[Dict[str, Any]]:
        """执行推荐行动"""
        executed = []

        for action in recommended_actions:
            action_result = {'action': action, 'executed': False, 'result': None}

            if action == 'Implement consensus-based actions':
                # 执行共识行动
                action_result['executed'] = True
                action_result['result'] = 'Consensus actions implemented'

            elif action == 'Focus on primal excitation optimization':
                # 优化原力激发
                for entity in self.entities.values():
                    if entity.life_state == LifeState.ALIVE:
                        if hasattr(entity, 'primal_strength'):
                            entity.primal_strength.increase(0.05)

                action_result['executed'] = True
                action_result['result'] = 'Primal excitation optimized'

            elif action == 'Prepare for kunzhuan guidance':
                # 准备坤转
                action_result['executed'] = True
                action_result['result'] = 'Kunzhuan preparation initiated'

            elif action == 'Initiate kunzhuan guidance process':
                # 已在_trigger_kunzhuan中处理
                action_result['executed'] = True
                action_result['result'] = 'Kunzhuan already triggered'

            executed.append(action_result)

        return executed

    def _update_stats(self, entity_updates: Dict[str, Any],
                      coordination_result: Dict[str, Any],
                      actions_executed: List[Dict[str, Any]]):
        """更新统计数据"""
        self.stats['steps_completed'] += 1
        self.stats['primal_energy_generated'] += entity_updates.get('primal_energy_generated', 0.0)

        if coordination_result.get('consensus_achieved'):
            self.stats['consensus_formed'] += 1

        # 计算执行的动作
        executed_count = sum(1 for a in actions_executed if a['executed'])
        self.stats['actions_executed'] = self.stats.get('actions_executed', 0) + executed_count

    def _print_step_summary(self, step_result: Dict[str, Any]):
        """打印步骤摘要"""
        step = step_result['step']
        alive = step_result['entities_alive']
        total = step_result['entities_total']
        consensus = step_result['coordination_result']['consensus_achieved']
        kunzhuan = step_result['coordination_result']['kunzhuan_required']

        status_parts = []
        status_parts.append(f"实体: {alive}/{total}存活")

        if consensus:
            status_parts.append("✅共识达成")
        else:
            status_parts.append("❌无共识")

        if kunzhuan:
            status_parts.append("⚡️坤转中")

        phenomena = step_result['phenomena_observed']
        if phenomena:
            status_parts.append(f"现象: {len(phenomena)}种")

        print(f"步骤{step:3d}: {' | '.join(status_parts)}")

    def _check_termination_conditions(self, step_result: Dict[str, Any]) -> bool:
        """检查模拟终止条件"""

        # 条件1：所有实体消亡
        if step_result['entities_alive'] == 0:
            print("[Simulator] 终止条件：所有实体已消亡")
            return True

        # 条件2：多次坤转后系统稳定
        recent_kunzhuan = len([k for k in self.kunzhuan_events
                               if k.get('step', 0) >= self.current_step - 5])
        if recent_kunzhuan >= 3:
            print("[Simulator] 终止条件：多次坤转后系统趋于稳定")
            return True

        # 条件3：达成持续共识
        recent_consensus = 0
        for i in range(max(0, len(self.history) - 5), len(self.history)):
            if self.history[i].get('coordination_result', {}).get('consensus_achieved'):
                recent_consensus += 1

        if recent_consensus >= 5:
            print("[Simulator] 终止条件：持续达成共识")
            return True

        return False

    def _generate_final_report(self) -> Dict[str, Any]:
        """生成最终模拟报告"""

        alive_entities = [e for e in self.entities.values()
                          if e.life_state == LifeState.ALIVE]

        # 计算原力总量
        total_primal = 0.0
        for entity in alive_entities:
            if hasattr(entity, 'primal_strength'):
                total_primal += entity.primal_strength.value
            elif hasattr(entity, 'collective_primal'):
                total_primal += entity.collective_primal.value

        # 哲学一致性验证
        philosophy_validation = self._validate_philosophy_consistency()

        report = {
            'simulation_id': self.simulation_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_steps': self.current_step + 1,
            'final_state': {
                'entities_alive': len(alive_entities),
                'entities_total': len(self.entities),
                'total_primal_energy': total_primal,
                'avg_primal_per_entity': total_primal / len(alive_entities) if alive_entities else 0.0,
                'field_states': {name: field.get_state() for name, field in self.fields.items()}
            },
            'statistics': self.stats,
            'key_events': {
                'kunzhuan_events_count': len(self.kunzhuan_events),
                'elimination_events_count': len(self.elimination_events),
                'consensus_formed_count': self.stats['consensus_formed'],
                'primal_energy_generated': self.stats['primal_energy_generated']
            },
            'philosophy_validation': philosophy_validation,
            'summary': self._generate_summary_text(),
            'history_summary': {
                'total_records': len(self.history),
                'first_step': self.history[0] if self.history else None,
                'last_step': self.history[-1] if self.history else None
            }
        }

        return report

    def _validate_philosophy_consistency(self) -> Dict[str, Any]:
        """验证模拟的哲学一致性"""

        validation_results = {}

        # 原则1：原力激发原理
        primal_check = {
            'principle': 'existence_is_excitation',
            'check': 'living_entities_have_primal',
            'details': {}
        }

        alive_without_primal = 0
        for entity in self.entities.values():
            if entity.life_state == LifeState.ALIVE:
                has_primal = False
                if hasattr(entity, 'primal_strength'):
                    has_primal = entity.primal_strength.is_significant
                elif hasattr(entity, 'collective_primal'):
                    has_primal = entity.collective_primal.is_significant

                if not has_primal:
                    alive_without_primal += 1

        primal_check['valid'] = alive_without_primal == 0
        primal_check['details'] = {
            'alive_entities': len([e for e in self.entities.values()
                                   if e.life_state == LifeState.ALIVE]),
            'alive_without_primal': alive_without_primal,
            'requirement': 'All alive entities must have significant primal excitation'
        }

        validation_results['primal_principle'] = primal_check

        # 原则2：消灭即目标追求
        elimination_check = {
            'principle': 'elimination_as_target_pursuit',
            'check': 'eliminations_have_target_basis',
            'details': {}
        }

        unjustified_eliminations = 0
        for event in self.elimination_events:
            if not event.get('target_based', False):
                unjustified_eliminations += 1

        elimination_check['valid'] = unjustified_eliminations == 0
        elimination_check['details'] = {
            'total_eliminations': len(self.elimination_events),
            'unjustified_eliminations': unjustified_eliminations,
            'requirement': 'All eliminations must be target-based'
        }

        validation_results['elimination_principle'] = elimination_check

        # 原则3：坤转本质
        kunzhuan_check = {
            'principle': 'kunzhuan_is_guidance_not_reconstruction',
            'check': 'kunzhuan_follows_correct_logic',
            'details': {}
        }

        incorrect_kunzhuan = 0
        for event in self.kunzhuan_events:
            if (event.get('method') != 'guidance_from_chaos' or
                    'reconstruction' in event.get('description', '').lower()):
                incorrect_kunzhuan += 1

        kunzhuan_check['valid'] = incorrect_kunzhuan == 0
        kunzhuan_check['details'] = {
            'total_kunzhuan': len(self.kunzhuan_events),
            'incorrect_kunzhuan': incorrect_kunzhuan,
            'requirement': 'Kunzhuan must be guidance from chaos, not reconstruction'
        }

        validation_results['kunzhuan_principle'] = kunzhuan_check

        # 总体验证
        all_valid = all(check['valid'] for check in validation_results.values())

        return {
            'all_valid': all_valid,
            'checks': validation_results,
            'summary': '✅ 通过所有检查' if all_valid else '❌ 存在哲学不一致'
        }

    def _generate_summary_text(self) -> str:
        """生成模拟摘要文本"""

        alive = len([e for e in self.entities.values()
                     if e.life_state == LifeState.ALIVE])
        total = len(self.entities)

        summary = f"模拟 '{self.simulation_id}' 完成\n"
        summary += f"• 总步数: {self.current_step + 1}\n"
        summary += f"• 实体状态: {alive}存活 / {total}总数\n"
        summary += f"• 坤转事件: {self.stats['kunzhuan_count']}次\n"
        summary += f"• 共识形成: {self.stats['consensus_formed']}次\n"
        summary += f"• 消灭事件: {self.stats['entities_eliminated']}次\n"
        summary += f"• 原力生成: {self.stats['primal_energy_generated']:.2f} PU\n"

        # 哲学验证摘要
        validation = self._validate_philosophy_consistency()
        if validation['all_valid']:
            summary += "• 哲学一致性: ✅ 完美符合秩法图公理\n"
        else:
            summary += "• 哲学一致性: ❌ 存在不一致\n"

        return summary

    def save_report(self, filename: Optional[str] = None):
        """保存模拟报告到文件"""
        if filename is None:
            filename = f"{self.simulation_id}_report.json"

        report = self._generate_final_report()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"[Simulator] 报告已保存: {filename}")

        # 同时保存简版摘要
        summary_filename = filename.replace('.json', '_summary.txt')
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(self._generate_summary_text())

        return filename

    def visualize(self, visualization_type: str = 'simple'):
        """可视化模拟结果（简单版本）"""

        try:
            import matplotlib.pyplot as plt

            if visualization_type == 'simple':
                self._simple_visualization()
            elif visualization_type == 'detailed':
                self._detailed_visualization()
            else:
                print(f"[Simulator] 未知的可视化类型: {visualization_type}")

        except ImportError:
            print("[Simulator] 需要matplotlib库进行可视化")
            print("安装: pip install matplotlib")

    def _simple_visualization(self):
        """简单可视化"""
        import matplotlib.pyplot as plt

        # 提取历史数据
        steps = []
        alive_counts = []
        primal_energy = []
        consensus_flags = []
        kunzhuan_flags = []

        for i, record in enumerate(self.history):
            steps.append(record['step'])
            alive_counts.append(record['entities_alive'])

            # 原力能量（简化）
            primal = record.get('stats_snapshot', {}).get('primal_energy_generated', 0)
            primal_energy.append(primal)

            # 共识标志
            consensus = record.get('coordination_result', {}).get('consensus_achieved', False)
            consensus_flags.append(1 if consensus else 0)

            # 坤转标志
            kunzhuan = record.get('coordination_result', {}).get('kunzhuan_required', False)
            kunzhuan_flags.append(1 if kunzhuan else 0)

        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # 1. 实体存活数量
        ax = axes[0, 0]
        ax.plot(steps, alive_counts, 'b-', linewidth=2, label='存活实体')
        ax.set_xlabel('模拟步骤')
        ax.set_ylabel('存活实体数量')
        ax.set_title('实体存活状态')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # 2. 原力能量累积
        ax = axes[0, 1]
        ax.plot(steps, primal_energy, 'g-', linewidth=2, label='原力能量')
        ax.set_xlabel('模拟步骤')
        ax.set_ylabel('原力能量 (PU)')
        ax.set_title('原力激发累积')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # 3. 共识和坤转事件
        ax = axes[1, 0]

        # 共识事件
        consensus_steps = [steps[i] for i, flag in enumerate(consensus_flags) if flag == 1]
        if consensus_steps:
            ax.scatter(consensus_steps, [1] * len(consensus_steps),
                       c='green', s=100, marker='o', label='共识达成', alpha=0.7)

        # 坤转事件
        kunzhuan_steps = [steps[i] for i, flag in enumerate(kunzhuan_flags) if flag == 1]
        if kunzhuan_steps:
            ax.scatter(kunzhuan_steps, [0.5] * len(kunzhuan_steps),
                       c='red', s=150, marker='*', label='坤转发生', alpha=0.8)

        ax.set_xlabel('模拟步骤')
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(['', '坤转', '共识'])
        ax.set_title('关键事件时间线')
        ax.grid(True, alpha=0.3, axis='x')
        ax.legend()

        # 4. 消灭事件累积
        ax = axes[1, 1]

        eliminations_cumulative = []
        current = 0
        for record in self.history:
            elims = record.get('stats_snapshot', {}).get('entities_eliminated', 0)
            current += elims
            eliminations_cumulative.append(current)

        ax.plot(steps, eliminations_cumulative, 'r-', linewidth=2, label='消灭累积')
        ax.set_xlabel('模拟步骤')
        ax.set_ylabel('消灭事件数量')
        ax.set_title('目标追求活动（消灭）')
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.suptitle(f'秩法图模拟结果 - {self.simulation_id}', fontsize=14)
        plt.tight_layout()
        plt.show()

        print(f"[Simulator] 可视化完成 - 显示 {len(steps)} 个步骤的数据")

    def run_demo(self):
        """运行演示场景"""
        print("\n" + "=" * 70)
        print("秩法图框架演示")
        print("=" * 70)

        print("\n1. 创建模拟器实例...")
        simulator = FALawSimulator({
            'simulation_id': 'demo_run',
            'log_level': 'info'
        })

        print("\n2. 运行生存竞争场景...")
        report = simulator.run_scenario('survival_competition', steps=30, step_duration=0.1)

        print("\n3. 生成可视化...")
        simulator.visualize('simple')

        print("\n4. 保存报告...")
        simulator.save_report()

        print("\n" + "=" * 70)
        print("演示完成！")
        print(f"模拟ID: {simulator.simulation_id}")
        print(f"最终报告已保存")
        print("=" * 70)

        return simulator
