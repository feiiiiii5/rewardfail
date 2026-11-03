# 2026-11-02 真实链路实验核对

- 检查项：249，失败：0
- 记录目录：<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01
- 两次 7 行首次尝试（2 个 agent worker）在生成阶段中止，原样保留在 failures/。

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| C0: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/C0/case.json" |
| C0: mode | 通过 | "fixed" |
| C0: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/__init__.py" |
| C0: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/experimental/reward_loop/reward_loop.py" |
| C0: compute_rm_score AST hash | 通过 | "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325" |
| C0: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| C0: pinned third_party clean | 通过 | "" |
| C0: completed | 通过 | "completed" |
| C0: row count | 通过 | 8 |
| C0: scores match expected | 通过 | [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C0: expected score vector | 通过 | [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C0: error set matches expected | 通过 | [] |
| C0: no false error column | 通过 | false |
| C0: every planned failure has ledger >=1 | 通过 | {} |
| C0: no ledger for non-failing rows | 通过 | [] |
| C0: export line count | 通过 | 8 |
| C0: export scores equal | 通过 | true |
| C0: export inputs equal | 通过 | true |
| C0: export outputs equal | 通过 | true |
| C0: export gts equal | 通过 | true |
| C0: export error values equal | 通过 | true |
| C0: wrong-length column ignored | 通过 | true |
| C1: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/C1/case.json" |
| C1: mode | 通过 | "fixed" |
| C1: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/__init__.py" |
| C1: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/experimental/reward_loop/reward_loop.py" |
| C1: compute_rm_score AST hash | 通过 | "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325" |
| C1: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| C1: pinned third_party clean | 通过 | "" |
| C1: completed | 通过 | "completed" |
| C1: row count | 通过 | 8 |
| C1: scores match expected | 通过 | [0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C1: expected score vector | 通过 | [0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C1: error set matches expected | 通过 | [0] |
| C1: error column present | 通过 | true |
| C1: every planned failure has ledger >=1 | 通过 | {"0": 2} |
| C1: no ledger for non-failing rows | 通过 | [] |
| C1: export line count | 通过 | 8 |
| C1: export scores equal | 通过 | true |
| C1: export inputs equal | 通过 | true |
| C1: export outputs equal | 通过 | true |
| C1: export gts equal | 通过 | true |
| C1: export error values equal | 通过 | true |
| C1: wrong-length column ignored | 通过 | true |
| C2: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/C2/case.json" |
| C2: mode | 通过 | "fixed" |
| C2: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/__init__.py" |
| C2: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/experimental/reward_loop/reward_loop.py" |
| C2: compute_rm_score AST hash | 通过 | "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325" |
| C2: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| C2: pinned third_party clean | 通过 | "" |
| C2: completed | 通过 | "completed" |
| C2: row count | 通过 | 8 |
| C2: scores match expected | 通过 | [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C2: expected score vector | 通过 | [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C2: error set matches expected | 通过 | [2] |
| C2: error column present | 通过 | true |
| C2: every planned failure has ledger >=1 | 通过 | {"2": 2} |
| C2: no ledger for non-failing rows | 通过 | [] |
| C2: export line count | 通过 | 8 |
| C2: export scores equal | 通过 | true |
| C2: export inputs equal | 通过 | true |
| C2: export outputs equal | 通过 | true |
| C2: export gts equal | 通过 | true |
| C2: export error values equal | 通过 | true |
| C2: wrong-length column ignored | 通过 | true |
| C3: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/C3/case.json" |
| C3: mode | 通过 | "fixed" |
| C3: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/__init__.py" |
| C3: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/experimental/reward_loop/reward_loop.py" |
| C3: compute_rm_score AST hash | 通过 | "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325" |
| C3: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| C3: pinned third_party clean | 通过 | "" |
| C3: completed | 通过 | "completed" |
| C3: row count | 通过 | 8 |
| C3: scores match expected | 通过 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| C3: expected score vector | 通过 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| C3: error set matches expected | 通过 | [0, 1, 2, 3, 4, 5, 6, 7] |
| C3: error column present | 通过 | true |
| C3: every planned failure has ledger >=1 | 通过 | {"4": 2, "0": 2, "1": 1, "5": 1, "2": 1, "6": 1, "3": 1, "7": 1} |
| C3: no ledger for non-failing rows | 通过 | [] |
| C3: export line count | 通过 | 8 |
| C3: export scores equal | 通过 | true |
| C3: export inputs equal | 通过 | true |
| C3: export outputs equal | 通过 | true |
| C3: export gts equal | 通过 | true |
| C3: export error values equal | 通过 | true |
| C3: wrong-length column ignored | 通过 | true |
| C4: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/C4/case.json" |
| C4: mode | 通过 | "fixed" |
| C4: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/__init__.py" |
| C4: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/experimental/reward_loop/reward_loop.py" |
| C4: compute_rm_score AST hash | 通过 | "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325" |
| C4: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| C4: pinned third_party clean | 通过 | "" |
| C4: completed | 通过 | "completed" |
| C4: row count | 通过 | 8 |
| C4: scores match expected | 通过 | [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0] |
| C4: expected score vector | 通过 | [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0] |
| C4: error set matches expected | 通过 | [6] |
| C4: error column present | 通过 | true |
| C4: every planned failure has ledger >=1 | 通过 | {"6": 2} |
| C4: no ledger for non-failing rows | 通过 | [] |
| C4: export line count | 通过 | 8 |
| C4: export scores equal | 通过 | true |
| C4: export inputs equal | 通过 | true |
| C4: export outputs equal | 通过 | true |
| C4: export gts equal | 通过 | true |
| C4: export error values equal | 通过 | true |
| C4: wrong-length column ignored | 通过 | true |
| C5: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/C5/case.json" |
| C5: mode | 通过 | "fixed" |
| C5: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/__init__.py" |
| C5: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/experimental/reward_loop/reward_loop.py" |
| C5: compute_rm_score AST hash | 通过 | "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325" |
| C5: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| C5: pinned third_party clean | 通过 | "" |
| C5: completed | 通过 | "completed" |
| C5: row count | 通过 | 7 |
| C5: scores match expected | 通过 | [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0] |
| C5: expected score vector | 通过 | [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0] |
| C5: error set matches expected | 通过 | [6] |
| C5: error column present | 通过 | true |
| C5: every planned failure has ledger >=1 | 通过 | {"6": 2} |
| C5: no ledger for non-failing rows | 通过 | [] |
| C5: export line count | 通过 | 7 |
| C5: export scores equal | 通过 | true |
| C5: export inputs equal | 通过 | true |
| C5: export outputs equal | 通过 | true |
| C5: export gts equal | 通过 | true |
| C5: export error values equal | 通过 | true |
| C5: wrong-length column ignored | 通过 | true |
| C6: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/C6/case.json" |
| C6: mode | 通过 | "fixed" |
| C6: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/__init__.py" |
| C6: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/experimental/reward_loop/reward_loop.py" |
| C6: compute_rm_score AST hash | 通过 | "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325" |
| C6: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| C6: pinned third_party clean | 通过 | "" |
| C6: completed | 通过 | "completed" |
| C6: row count | 通过 | 8 |
| C6: scores match expected | 通过 | [0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C6: expected score vector | 通过 | [0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C6: error set matches expected | 通过 | [2] |
| C6: error column present | 通过 | true |
| C6: every planned failure has ledger >=1 | 通过 | {"2": 2} |
| C6: no ledger for non-failing rows | 通过 | [] |
| C6: export line count | 通过 | 8 |
| C6: export scores equal | 通过 | true |
| C6: export inputs equal | 通过 | true |
| C6: export outputs equal | 通过 | true |
| C6: export gts equal | 通过 | true |
| C6: export error values equal | 通过 | true |
| C6: wrong-length column ignored | 通过 | true |
| C1r: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/C1r/case.json" |
| C1r: mode | 通过 | "fixed" |
| C1r: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/__init__.py" |
| C1r: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/experimental/reward_loop/reward_loop.py" |
| C1r: compute_rm_score AST hash | 通过 | "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325" |
| C1r: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| C1r: pinned third_party clean | 通过 | "" |
| C1r: completed | 通过 | "completed" |
| C1r: row count | 通过 | 8 |
| C1r: scores match expected | 通过 | [0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C1r: expected score vector | 通过 | [0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C1r: error set matches expected | 通过 | [0] |
| C1r: error column present | 通过 | true |
| C1r: every planned failure has ledger >=1 | 通过 | {"0": 2} |
| C1r: no ledger for non-failing rows | 通过 | [] |
| C1r: export line count | 通过 | 8 |
| C1r: export scores equal | 通过 | true |
| C1r: export inputs equal | 通过 | true |
| C1r: export outputs equal | 通过 | true |
| C1r: export gts equal | 通过 | true |
| C1r: export error values equal | 通过 | true |
| C1r: wrong-length column ignored | 通过 | true |
| C2r: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/C2r/case.json" |
| C2r: mode | 通过 | "fixed" |
| C2r: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/__init__.py" |
| C2r: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-unionfill/verl/experimental/reward_loop/reward_loop.py" |
| C2r: compute_rm_score AST hash | 通过 | "4ba42b7085bbe730acad4829ecca472f0a3beff19eef90993852f1bea041e325" |
| C2r: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| C2r: pinned third_party clean | 通过 | "" |
| C2r: completed | 通过 | "completed" |
| C2r: row count | 通过 | 8 |
| C2r: scores match expected | 通过 | [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C2r: expected score vector | 通过 | [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0] |
| C2r: error set matches expected | 通过 | [2] |
| C2r: error column present | 通过 | true |
| C2r: every planned failure has ledger >=1 | 通过 | {"2": 2} |
| C2r: no ledger for non-failing rows | 通过 | [] |
| C2r: export line count | 通过 | 8 |
| C2r: export scores equal | 通过 | true |
| C2r: export inputs equal | 通过 | true |
| C2r: export outputs equal | 通过 | true |
| C2r: export gts equal | 通过 | true |
| C2r: export error values equal | 通过 | true |
| C2r: wrong-length column ignored | 通过 | true |
| O4: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/O4/case.json" |
| O4: mode | 通过 | "original" |
| O4: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-original/verl/__init__.py" |
| O4: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-original/verl/experimental/reward_loop/reward_loop.py" |
| O4: compute_rm_score AST hash | 通过 | "afb5d6c40caf9f3992726c9dacfc8d6ba8ff83c0f581fa3af543cc37e03e54fc" |
| O4: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| O4: pinned third_party clean | 通过 | "" |
| O4: completed | 通过 | "completed" |
| O4: row count | 通过 | 8 |
| O4: scores match pre-run inference | 通过 | [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0] |
| O4: error flag lost in original | 通过 | [] |
| O4: injection ledger present | 通过 | {"6": 2} |
| O4: export readback | 通过 | 8 |
| O5: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/O5/case.json" |
| O5: mode | 通过 | "original" |
| O5: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-original/verl/__init__.py" |
| O5: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-original/verl/experimental/reward_loop/reward_loop.py" |
| O5: compute_rm_score AST hash | 通过 | "afb5d6c40caf9f3992726c9dacfc8d6ba8ff83c0f581fa3af543cc37e03e54fc" |
| O5: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| O5: pinned third_party clean | 通过 | "" |
| O5: completed | 通过 | "completed" |
| O5: row count | 通过 | 7 |
| O5: scores match pre-run inference | 通过 | [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0] |
| O5: error flag lost in original | 通过 | [] |
| O5: injection ledger present | 通过 | {"6": 2} |
| O5: export readback | 通过 | 7 |
| O6: case.json exists | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/O6/case.json" |
| O6: mode | 通过 | "original" |
| O6: imported verl under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-original/verl/__init__.py" |
| O6: reward_loop under intended copy | 通过 | "<WORKSPACE>/thesis-runs/verl-pr8015-original/verl/experimental/reward_loop/reward_loop.py" |
| O6: compute_rm_score AST hash | 通过 | "afb5d6c40caf9f3992726c9dacfc8d6ba8ff83c0f581fa3af543cc37e03e54fc" |
| O6: ROWS hash matches historical | 通过 | "b808a68980ff4be946e7a1447e178825b8e4c2422005d06a655586b509bf1719" |
| O6: pinned third_party clean | 通过 | "" |
| O6: aborted as expected | 通过 | "aborted" |
| O6: raise site | 通过 | "verl/experimental/reward_loop/reward_loop.py:369" |
| O6: injection ledger present | 通过 | {"2": 2} |
| C1r: scores equal to C1 | 通过 | {"first": [0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0], "restart": [0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0]} |
| C1r: error ids equal to C1 | 通过 | {"first": [0], "restart": [0]} |
| C1r: export equal to C1 | 通过 | {"first": 8, "restart": 8} |
| C2r: scores equal to C2 | 通过 | {"first": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0], "restart": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0]} |
| C2r: error ids equal to C2 | 通过 | {"first": [2], "restart": [2]} |
| C2r: export equal to C2 | 通过 | {"first": 8, "restart": 8} |
| O5 first attempt: preserved | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/failures/O5-two-agent-workers/case.json" |
| O5 first attempt: aborted at generation | 通过 | {"outcome": "aborted", "raise": "verl/protocol.py:871", "message": "only support equal chunk. Got size of DataProto 7 and chunk 2."} |
| C5 first attempt: preserved | 通过 | "<WORKSPACE>/thesis-runs/2026-11-02-chain/run-01/failures/C5-two-agent-workers/case.json" |
| C5 first attempt: aborted at generation | 通过 | {"outcome": "aborted", "raise": "verl/protocol.py:871", "message": "only support equal chunk. Got size of DataProto 7 and chunk 2."} |
| driver hash recorded for all cases | 通过 | {"3b3aa0dc2f5934e09a06833477e3fed705cf01870a9bb700cb19febb05ef04ca": ["C0", "C1", "C2", "C3", "C4", "O4", "O6"], "6cce7c0cfe36e9ea5c920eaa1562cfaa6edcb5aeb0db8298facd6ec2e87beb8c": ["C5", "C6", "C1r", "C2r", "O5"]} |
| rewardfail workspace unchanged except new driver | 通过 | ["?? .DS_Store", "?? experiments/thesis_chain.py"] |
| pinned third_party clean | 通过 | "" |
| original copy reward_loop hash | 通过 | "" |
| unionfill copy AST hash | 通过 | "" |
