# 决策记录 004：研究代码与核心代码分离原则

## 状态
✅ 已采纳（2026-02-13）

## 问题
早期项目中，研究脚本（pressure_excitation_study*.py、optimal_targets_study.py）
与核心数学组件混放在 `src/falaw/core/math/`，导致：
- 用户无法区分「这是理论」还是「这是实验」
- 包体积膨胀
- 导入时执行打印语句，干扰正常使用

## 分离原则
| 类型 | 存放位置 | 特征 |
|------|------|------|
| ✅ 核心代码 | `src/falaw/` | 无打印语句，可被 import |
| ✅ 研究代码 | `research/archive/scripts/` | 有 main()，可独立执行 |
| ✅ 实验数据 | `research/results/` | JSON/PNG 文件 |

## 迁移记录
- 2026-02-13: 将 5 个研究脚本移出 `src/`
- 所有核心数学文件已保留：
  - `expansion.py` —— 可能性空间
  - `indirect.py` —— 间接影响
  - `tension.py` —— 张力场计算（待从 study6 提取）

## 后续维护
- 禁止在 `src/` 下创建以 `*study*.py` 命名的文件
- 研究阶段的探索代码一律放在 `research/`
- 只有经过决策记录（001–003）确认的代码才能进入 `src/`