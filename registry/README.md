# Registry · 六态与目录

这是 UIBC 的**目录**，不是认证机构的名录。它只记录一件事：某个包/某套向量，在**谁**的机器上跑过、字节是否仍与 receipt 一致、以及当前处于哪个状态。

一句话：**目录记录我们核到什么，不记录我们认为谁值得信任。**

## 六态

| 状态 | 含义 | 进入需要 | 它**不**意味着 |
|---|---|---|---|
| `submitted` | 收到 receipt 或 issue，尚未复核 | 一份 `uibc-receipt/1` 或一条 issue | 任何形式的认可 |
| `checked` | receipt 通过 `check_receipt.py`（字节与仓内一致），但 runner 是作者侧（`code: author`） | receipt URL + evidence URL | 独立验证 |
| `independent` | runner 为第三方（`code: independent`），receipt 通过 | 同上，且 `code` 必须为 `independent` | 该 runner 的身份被核过（receipt 不证明运行者存在） |
| `superseded` | 被新版本取代，历史保留 | `superseded_by` 指向新条目 id | 旧结论失效（旧字节仍在，仍可复算） |
| `revoked` | 撤销，且**绑定 root** | `target_root`（64 位 hex）；root 与包当前 root 不符即拒绝适用 | 撤销原因被公布（原因写在 notes，可缺省） |
| `withdrawn` | 提交者主动撤回 | 无需额外字段 | 任何负面结论 |

## 转移规则（由 `check_registry.py` 强制）

```
submitted → checked | withdrawn
checked   → independent | superseded | revoked | withdrawn
independent → superseded | revoked | withdrawn
superseded → （终态，只可被新条目取代）
revoked    → （终态）
withdrawn  → （终态）
```

倒退（如 `independent → checked`）与跨级（`submitted → independent`）都会被拒。拒绝理由会打印到 stdout。

## 为什么撤销必须绑 root

`revoked` 不带 `target_root` 是**最危险的一种错误**：一条旧撤销会静默地套到后来新产出的内容上，或者反过来，撤销了一条而新包照样通过。规范 §7 写明：撤销所适用的 root 与包当前 root 不符时必须拒用。目录把这条约束落成 schema 的 `if/then`。

## 怎么加一条

1. 按 `vectors` 的 `make_receipt.py` 生成 receipt，`check_receipt.py` 必须打印 `ACCEPTABLE`。
2. 开 issue（`Independent run receipt` 模板），附 receipt。
3. 维护者按上表判定状态，改 `index.json`，跑 `python registry/check_registry.py`。
4. CI（`.github/workflows/registry-check.yml`）在每次 push/PR 上重跑同一条命令。

## 现在里面有什么

一条：`uibc-vectors-six-row-2026-11-23`，状态 `checked`、`code: author`。**独立条目 0 条**——这不是遗漏，是事实，写在这里以免被读成"已完成"。（该条目的矩阵已在其源头扩到八行；id 保留旧名以免已引用的链接失效。）

## 跑一遍

```bash
python registry/check_registry.py            # 期望：REGISTRY OK - 1 entry, 0 independent, transitions valid
```

纯标准库，无第三方依赖。
