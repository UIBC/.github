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

## 证据索引：公开面不许凭记忆说话

`registry/evidence-index.json` 把"本组织关于自身状态的公开说法"变成行：每条都有 `state`（present / absent）、`as_of`、`measured`、以及带 `sha256` 与字节数的见证文件。

起因是 2026-11-24 一天之内**同一类错误犯了三次**：把已有的第二实现（`verify-js`，18/19 项）说成缺失、把已有的验证器基准记录说成没有、把已有比特币区块锚证（高度 976735）说成 Pending。三次都不是谎话，是凭记忆或旧快照写的句子——散文没有摘要，所以它会静默漂移。

规则（`registry/check_evidence_index.py`）：

- **present**：逐个抓取见证文件，比对 sha256 与长度；且至少一个见证不是 `.md/.txt` —— 一段散文不能给自己作证。
- **absent**：必须带 `absent_check`，去抓一份机器可读账本并比对某个路径的值。账本一旦显示非零，这一行就被拒 —— 这就是"少报"被拦住的方式。
- **link**：锚证里记载的 `proof.sha256` 必须等于实际 `.ots` 容器的摘要（当前两条都对上）。
- **离线可复核**：`--cache <dir>` 从本地镜像读取（键为 `sha256(url)`），给无法直连的人一条同等的复核路径；`--no-network` 只查结构，并打印 `UNVERIFIED`，不会悄悄算通过。

实跑（本地镜像复核，7 个见证全部抓取）：

```
EVIDENCE INDEX OK - 5 entries, 4 present, 1 absent; 7 witnesses fetched, digests and lengths match.
```

三个负对照都被拦住：改错见证摘要 → `R2 digest mismatch`；把账本改成 `headline=1` → `R3 claims absence but headline=1 ... the claim is stale, not the ledger`；改坏锚证里的 `proof.sha256` → `R4 ... does not match`。

一条要说清的局限：**"外部独立运行不存在"这类 absence，永远只能靠我们自己维护的账本证明**，账本可能长期不更新。所以它是"机器核过的 0"，不是"没人跑过"的证据。

