# USC Detector — 可升级智能合约检测工具

基于 **正则匹配 + 静态扫描（AST）** 的规则化工具，用于识别可升级智能合约（Upgradeable Smart Contracts, USC）。

## 功能概览

- **规则库**：若合约同时包含 `delegatecall` 与 EIP-1967 标准存储槽常量，则判定为「标准代理合约」。
- **检测方式**：正则匹配 + 可选 AST 解析（通过 solc 编译得到 AST 后对树节点做逻辑匹配）。
- **输出**：JSON 或 CSV，包含合约地址/文件路径、检测到的模式类型、置信度。

## 项目结构

```
usc_detector/
  __init__.py       # 包入口
  patterns.py       # USC 代码模式与 EIP-1967 常量定义
  regex_detector.py # 正则匹配（全文）
  ast_detector.py   # 简单 AST 扫描 + 调用精确分析
  precise_analyzer.py # 更精确：合约/函数级 AST 匹配
  slither_backend.py  # 可选：Slither 深度分析
  rules.py          # 规则引擎：分类与置信度
  scanner.py        # 扫描入口（单文件/目录）
  main.py           # CLI（JSON/CSV 输出）
requirements.txt
```

## 更精确的分析算法（三层）

| 层级 | 方式 | 精度说明 | 依赖 |
|------|------|----------|------|
| **1. 正则** | 全文正则匹配 | 快速，可能受注释/多合约干扰 | 无 |
| **2. AST 合约级** | 解析 AST，按合约/函数粒度检测 | delegatecall 仅在函数体内统计；实现槽按合约内字面量；可区分多合约文件中“哪个是代理” | solc + py-solc-x + py-solc-ast |
| **3. Slither** | CFG/IR 分析 | 通过 IR 识别 delegatecall、存储引用，可扩展为数据流分析 | slither-analyzer + solc |

- **默认**：启用 AST 时自动使用 **合约级精确分析**（`precise_analyzer`）。同一文件中多个合约会逐合约检查 delegatecall/实现槽/upgradeTo/_fallback，并选出最像代理的合约用于分类，置信度会略提高。
- **可选 Slither**：安装 `slither-analyzer` 后，可在自己的脚本中调用 `usc_detector.slither_backend.analyze_file(path)` 做进一步分析；当前 CLI 仍以正则 + AST 为主。

## 安装

```bash
cd d:\poly\Security\Project
pip install -r usc_detector/requirements.txt
```

可选：安装 solc 以启用 **更精确的 AST 分析**（合约/函数级）：

```bash
pip install py-solc-x
# 首次编译前可指定版本，例如：python -c "import solcx; solcx.install_solc('0.8.20')"
```

可选：安装 Slither 用于深度分析（需 Python 3.10+ 与 solc）：

```bash
pip install slither-analyzer
# 在代码中: from usc_detector.slither_backend import analyze_file; analyze_file("path/to.sol")
```

## 使用

### 命令行

从项目根目录运行：

```bash
# 对 contracts/ 里每个合约分别输出：每个合约一个 JSON 文件 + 终端逐条结果
python run_usc_detector.py contracts --output-dir results --no-ast

# 输出目录 results/ 下会生成：
#   <合约名>.json  — 每个合约一份独立检测结果
#   summary.json   — 所有结果的汇总
# 终端会打印：文件 | 模式类型 | 置信度（每行一个合约）
```

```bash
# 扫描单个文件，输出 JSON（默认）
python run_usc_detector.py path/to/contract.sol

# 合并为一个文件
python run_usc_detector.py contracts --output out.json --no-ast
python run_usc_detector.py contracts --output out.csv --format csv --no-ast
```

或直接运行包内 main：

```bash
python -m usc_detector.main --input path/to/contract.sol -o out.json -f json
python -m usc_detector.main --input path/to/contracts/ -o out.csv -f csv --no-ast
```

### 输出格式

- **JSON**：`{"results": [...], "count": N}`，每条结果包含 `contract_address`（或文件路径）、`pattern_type`、`confidence`、`details`。
- **CSV**：列名为 `contract_address`、`file`、`pattern_type`、`confidence`、`details`。

### USC 四类分类（pattern_type）

| 类型 | 说明 |
|------|------|
| `simple_proxy` | **简单代理**：delegatecall + 实现槽(0x3608...)，可有 _fallback |
| `transparent_proxy` | **透明代理**：带 Admin/TransparentUpgradeableProxy 的代理 |
| `uups` | **通用可升级代理 (UUPS)**：含 upgradeTo/upgradeToAndCall 或 UUPSUpgradeable |
| `diamond_beacon` | **插件/钻石模式**：Diamond (diamondCut/facets) 或 Beacon 代理 |
| `delegatecall_only` | 仅含 delegatecall，无标准实现槽 |
| `eip1967_slot_only` | 仅含 EIP-1967 槽位，无 delegatecall |
| `generic_upgradeable` | 通用可升级特征 |
| `unknown` | 未匹配到上述规则 |

### 代码特征（pattern_extraction）

每条结果包含 **pattern_extraction**，对应三项提取特征：

| 特征 | 含义 |
|------|------|
| **key_instruction_delegatecall** | 关键指令：是否包含 `delegatecall` |
| **storage_implementation_slot** | 存储特征：是否使用特定存储槽（如 `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc`）存放逻辑合约地址 |
| **function_upgrade_to** | 函数特征：是否存在 `upgradeTo()` / `_upgradeTo()` / `upgradeToAndCall()` |
| **function_fallback** | 函数特征：是否存在 `_fallback()` / `_delegate()` / `fallback() external` / `receive() external` |

## 规则逻辑简述

- **简单代理**：包含 delegatecall + 实现槽(0x3608...)，且无强 UUPS/Transparent/Diamond 标记；有 _fallback 时置信度更高。
- **透明代理**：delegatecall + TransparentUpgradeableProxy/ProxyAdmin 或 admin 相关标记。
- **UUPS**：delegatecall + upgradeTo/upgradeToAndCall 或 UUPSUpgradeable。
- **Diamond/Beacon**：diamondCut、facets 等 Diamond 特征，或 Beacon 槽/BeaconProxy、UpgradeableBeacon。
- 分类优先级：Diamond/Beacon > Transparent > UUPS > Simple Proxy。

## 自动测试（每次运行自动扫描 contracts/）

测试套件会**自动对 `contracts/` 文件夹内所有 `.sol` 合约**进行扫描（自动排除 `node_modules`）。每次跑测试即会检测这些合约。

```bash
# 在项目根目录执行
pytest
# 或
python -m pytest usc_detector/tests/test_usc_detector.py -v
```

测试内容包含：`contracts/` 存在、存在至少一个 `.sol` 文件、全量扫描无报错、结果数量与文件数一致、每条结果含必要字段、逐文件扫描不抛异常。

## 依赖说明

- **正则检测**：仅需 Python 3，无额外依赖。
- **AST 检测**：需要 `py-solc-ast`、`py-solc-x` 以及系统/虚拟环境中可用的 `solc`。未安装或编译失败时自动退化为仅正则。

## 引用

- [EIP-1967: Proxy Storage Slots](https://eips.ethereum.org/EIPS/eip-1967)
- OpenZeppelin ERC1967Proxy / ERC1967Upgrade 参考实现
