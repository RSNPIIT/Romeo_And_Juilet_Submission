# The One Introduction Problem: Sequential Reciprocal Matching Under Uncertainty
## Research Approach Note & Technical Formulation
**Competition:** Romeo & Juliet × IIT Madras — Applied Machine Learning Programme & Hackathon  
**Track:** Round 1 Research Submission  
**Author / Team:** Ramrup Satpati (`RSNPIIT`)  
**Date:** October 2026  
**Document Version:** 1.0.0 (Compliant with Participant Specification v1.0.0)

---

## Executive Summary

The sequential matching problem requires an autonomous decision policy to operate over a dynamic population of synthetic agents across a 60-day decision horizon, followed by a 40-day observation window. At each discrete day $t$, the policy faces a dual decision:
1. **Active Clarification:** Allocating a constrained daily budget of 12 inquiry units to acquire missing self-reported features without exceeding rate limits or re-asking declined fields.
2. **Combinatorial Allocation:** Constructing a set of disjoint, feasible reciprocal introductions that maximize cumulative successful outcomes while trading off immediate pairing against the option value of waiting for superior future arrivals.

This approach note presents a mathematically principled, two-phase policy architecture:
- **Phase I: Value-of-Information (VoI) Targeted Clarification:** Prioritizes unlocking near-feasible candidate pairs blocked by single hard-constraint missingness, completely avoiding unpromising or isolated candidates.
- **Phase II: Maximum-Weight Bipartite/General Matching with Reservation Thresholds:** Replaces sub-optimal pairwise greedy matching with global graph optimization (Edmonds' Blossom / Maximum Weight Matching) augmented with a time-adaptive acceptance reservation threshold to prevent premature suboptimal commitments.

---

## 1. Problem Formulation & Decision Objective

### 1.1 The Sequential Optimization Problem
Let $P_t$ denote the set of currently available, active members in pool $\mathcal{P}$ at day $t \in \{0, 1, \dots, 59\}$. Each member $i \in P_t$ has observed demographic attributes $x_i$, observable questionnaire features $q_i(t)$, a missingness mask $m_i(t) \in \{\text{observed}, \text{not\_asked}, \text{declined}\}$, and a status indicator $\text{available}_i(t) \in \{0, 1\}$.

The global objective is to maximize the cumulative **Mutual Second Meeting Intention (MSMI)** over the episode while maintaining equitable distinct-member coverage:

$$\max_{\{\mathcal{A}_t, \mathcal{M}_t\}_{t=0}^{59}} \mathbb{E} \left[ \sum_{(i,j) \in \bigcup_t \mathcal{M}_t} Y_{ij}^{\text{MSMI}} \right]$$

Subject to the following operational and contract constraints:
1. **Reciprocal Hard Feasibility:** For every introduced pair $(i,j) \in \mathcal{M}_t$, $\text{Eligibility}(i, j) = \text{feasible}$.
2. **At-Most-Once Concurrency:** $\forall i \in P_t, \sum_{j} \mathbb{I}[(i,j) \in \mathcal{M}_t] \le 1$.
3. **No Duplicate Introductions:** $\mathcal{M}_t \cap \mathcal{M}_{t'} = \emptyset \quad \forall t \ne t'$.
4. **Daily Clarification Budget:** $\text{Cost}(\mathcal{A}_t) \le 12 \text{ units/day}$, where bundle cost is 3 units and single soft-field cost is 1 unit.
5. **Irreversibility of Declines:** If $m_{i,k}(t) = \text{declined}$, field $k$ can never be queried or observed.

---

## 2. Reciprocal Eligibility & Compatibility Scoring

### 2.1 The Two-Sided Hard Constraint Filter
Pair feasibility is strictly non-negotiable. An introduction is invalid unless both directional checks succeed across all 11 hard constraints:

$$\text{Feasible}(i, j) = \bigwedge_{k \in \text{HARD}} \Big( C_k(i \to j) \land C_k(j \to i) \Big)$$

- **Age Reciprocity:** $j.\text{age} \in [i.\text{age\_min}, i.\text{age\_max}] \land i.\text{age} \in [j.\text{age\_min}, j.\text{age\_max}]$.
- **Gender Compatibility:** $j.\text{gender} \in i.\text{who\_to\_meet} \land i.\text{gender} \in j.\text{who\_to\_meet}$.
- **Geographic Proximity:** $j.\text{zone} \in i.\text{acceptable\_zones} \land i.\text{zone} \in j.\text{acceptable\_zones}$.
- **Structure & Lifestyle:** $i.\text{structure} = j.\text{structure}$, mutually compatible smoking habits, and non-conflicting parental intentions.
- **Temporal Synchronization:** $|i.\text{schedule} \cap j.\text{schedule}| \ge 1$.

### 2.2 Probabilistic Compatibility Scoring
For any verified feasible pair $(i,j)$, compatibility is decomposed into two directional acceptance probabilities and a mutual joint outcome:

$$p_A(i \to j) = \sigma\left(\mathbf{w}_A^T \phi(i, j)\right), \quad p_B(j \to i) = \sigma\left(\mathbf{w}_B^T \phi(j, i)\right)$$

Where $\phi(i, j)$ represents directional reciprocal feature vectors:
- **Lifestyle Alignment:** Exact or soft overlap across `lifestyle`, `conversations`, and `relationship_pace`.
- **Goal Congruence:** Indicator of matching `relationship_goal` (e.g. `long_term` vs. `exploring`).
- **Emotional Readiness:** Alignment between `emotional_availability` and `space_for_relationship`.

The joint pairwise weight assigned to edge $(i,j)$ is:

$$W_{ij} = p(i \leftrightarrow j) = p_A(i \to j) \cdot p_B(j \to i) \cdot \gamma_{\text{synergy}}(i,j)$$

Where $\gamma_{\text{synergy}}$ captures interaction terms between complementary traits.

---

## 3. Global Allocation: Beyond Pairwise Greedy

### 3.1 The Failure of Greedy Pair Selection
Greedy matching sorts candidate pairs by score $W_{ij}$ and iteratively locks the top pair. In reciprocal networks, this creates negative externalities:

```
    [A] ------- 0.90 ------- [B]
      \                     /
       0.65               0.65
        \                 /
        [D]              [C]
```
- **Greedy Choice:** Matches $(A, B)$ (weight 0.90), stranding $C$ and $D$ with near-zero match (total value = 0.95).
- **Optimal Global Matching:** Selects $(A, D)$ and $(B, C)$ (total value = $0.65 + 0.65 = 1.30$, a $+36.8\%$ gain in societal welfare).

### 3.2 Maximum Weight Matching Formulation
On each day $t$, we construct an undirected compatibility graph $G_t = (V_t, E_t)$ where vertices $V_t = P_t$ and edges $E_t = \{(i,j) \mid \text{Feasible}(i,j) \land W_{ij} \ge \tau_t\}$.

The allocation is solved using **Maximum Weight General Matching (Edmonds' Blossom Algorithm)**:

$$\mathcal{M}_t^* = \arg\max_{\mathcal{M} \subseteq E_t} \sum_{(i,j) \in \mathcal{M}} W_{ij} \quad \text{s.t.} \quad \sum_{e \in \mathcal{M}: v \in e} 1 \le 1 \quad \forall v \in V_t$$

### 3.3 Dynamic Reservation Threshold & The Value of Waiting
A key vulnerability of myopic policies is matching a newly arrived member to a mediocre partner immediately. We implement a time-varying reservation threshold $\tau_t$:

$$\tau_t = \tau_0 \cdot \left(1 - \frac{t}{T}\right)^{\alpha} + \tau_{\min}$$

- Early in the episode ($t < 20$), $\tau_t$ is high: the policy only executes high-confidence pairs, preserving available supply for upcoming arrivals.
- Late in the episode ($t > 45$), $\tau_t \to \tau_{\min}$: the policy relaxes standards to clear unserved members before the horizon closes, maximizing coverage.

---

## 4. Value-of-Information (VoI) Active Clarification Policy

A daily budget of 12 units is severely scarce across a pool of 200 members. Blind exploration wastes budget on unmatchable members.

### 4.1 Prioritization Hierarchy
1. **Marginal Feasibility Unlock:** Identify pairs $(i, j)$ where 10 of 11 hard constraints are confirmed compatible, but exactly one member has an unasked hard constraint bundle.
   - Cost: 3 units.
   - Expected Gain: Converts an inactive edge into a feasible edge with high probability.
2. **Top-Tier Tie-Breaking:** If remaining budget exists ($< 3$ units), query soft fields (`relationship_goal`, `lifestyle`) for candidates involved in multiple competing edges to disambiguate the optimal matching.
3. **Strict Negative Pruning:**
   - Never ask a candidate with zero potential matches across known demographic filters (`age`, `gender`, `zone`).
   - Never re-query any field marked `declined`.

---

## 5. Temporal Integrity & Leakage Prevention

The competition environment simulates real-world asynchronous delays:
- **Observation Lag:** Introduction outcomes take up to 7 days to materialize; feedback is released strictly on the scheduled observation day.
- **Strict Anti-Leakage Pipeline:**
  - The policy state maintains an internal event queue indexed strictly by $t_{\text{observed}} \le t_{\text{current}}$.
  - Missing values (`null`) are explicitly modeled as missing completely at random or missing not at random; they are never imputed with zero or negative sentiment.
  - The policy state is completely wiped between episodes, ensuring no cross-episode or cross-seed leakage.

---

## 6. Empirical Baseline Benchmarks & Analysis

We evaluated the three supplied baselines across all six official scenario variants on seed `101` using `evaluate.py`. The results demonstrate clear structural performance bottlenecks:

| Scenario Variant | Baseline Policy | MSMI / 100 Members | Coverage (%) | Mutual Accept / 100 | Ask Cost |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`development`** | `greedy` | 0.50 | 46.0% | 9.0 | 198 |
| | `no_asks` | 0.50 | 19.5% | 8.5 | 0 |
| | `random` | 0.00 | 47.0% | 7.0 | 198 |
| **`sparse`** (12 zones) | `greedy` | **0.00** | 17.0% | 2.0 | 192 |
| | `no_asks` | 0.00 | 8.0% | 0.5 | 0 |
| | `random` | 0.00 | 18.0% | 2.0 | 192 |
| **`cold_start`** | `greedy` | 0.50 | 43.0% | 7.5 | 246 |
| | `no_asks` | 0.00 | 14.0% | 3.0 | 0 |
| | `random` | 0.50 | 43.5% | 7.0 | 246 |
| **`delayed`** | `greedy` | 1.00 | 46.0% | 9.5 | 198 |
| | `no_asks` | 0.50 | 21.0% | 8.5 | 0 |
| | `random` | 0.50 | 46.0% | 6.5 | 198 |
| **`shift`** | `greedy` | 0.50 | 46.0% | 9.5 | 198 |
| | `no_asks` | 0.50 | 21.0% | 9.5 | 0 |
| | `random` | 0.00 | 46.5% | 6.5 | 198 |
| **`drift`** | `greedy` | 0.50 | 46.0% | 8.0 | 198 |
| | `no_asks` | 0.50 | 20.0% | 9.5 | 0 |
| | `random` | 0.50 | 46.0% | 7.0 | 198 |
| **Overall Average** | **`greedy`** | **0.50** | **40.75%** | **7.58** | **205.0** |
| | **`no_asks`** | **0.33** | **17.42%** | **6.58** | **0.0** |
| | **`random`** | **0.25** | **41.17%** | **6.00** | **205.0** |

### Key Diagnostic Insights
1. **The Infeasibility Trap of `no_asks`:** Disabling clarification cuts coverage from **40.75% down to 17.42%** (a 57.3% collapse). Without asking hard constraints, massive numbers of viable matches remain permanently blocked.
2. **The `sparse` Collapse:** In the 12-zone geographic fragmentation scenario, `greedy` scores **0.00 MSMI/100** and coverage drops to 17%. Greedy fails because isolated clusters require deliberate multi-hop or delayed pairing rather than immediate consumption of viable members.
3. **Random Matching Hazard:** Random matching generates comparable coverage to greedy (~41%) but halves the MSMI rate (0.25 vs 0.50), proving that soft preference alignment significantly governs post-introduction meeting success.

---

## 7. Proposed Ablation Study Design

To isolate the causal drivers of performance in Round 2, we declare three targeted ablations:

1. **Ablation 1 (Allocation Mechanism):** Global Maximum Weight Matching vs. Pairwise Greedy.
   - *Hypothesis:* Maximum Weight Matching will prevent network stranding, improving MSMI by $\ge 25\%$ especially in `sparse` and `development` scenarios.
2. **Ablation 2 (Clarification Policy):** Targeted VoI (Pair-Unlock) vs. Baseline Greedy Asks vs. Zero Asks.
   - *Hypothesis:* Spending budget exclusively on pairs that unlock reciprocal feasibility will yield equal coverage with $\ge 35\%$ lower total ask cost.
3. **Ablation 3 (Temporal Reservation):** Adaptive Thresholding $\tau_t$ vs. Static Threshold vs. Zero Threshold (Match immediately).
   - *Hypothesis:* Holding high standards early in the episode will raise average match quality for early cohort arrivals without sacrificing end-of-episode coverage.

---

## 8. Failure Modes & Edge Case Analysis

| Challenge / Edge Case | System Behavior & Mitigation |
| :--- | :--- |
| **Severely Sparse Pools (`sparse`)** | Broaden soft threshold criteria; prioritize geographic budget queries (`acceptable_zones`) over lifestyle questions. |
| **High Refusal Rate (`declined`)** | Immediately freeze declined fields; reroute matching engine to exploit observable surrogate features without penalty. |
| **Late Arrival Bursts ($t \in [15, 20]$)** | Buffer uncommitted candidates who have broad compatibility profiles to pair with incoming arrivals. |
| **Deadlock / Unmatched Subgraphs** | End-of-episode relaxation: on days $50 \le t \le 59$, execute all valid feasible pairs regardless of soft score to minimize unserved penalties. |

---

## 9. Real-World Limitations & Ethical Boundaries

- **Synthetic Domain Boundary:** The dataset and simulator are purely synthetic mathematical environments. Simulator performance does not imply the ability to predict genuine human romantic or emotional outcomes.
- **Fairness & Non-Discrimination:** Real-world matchmaking systems must guard against disparate impact across protected demographic categories, feedback loops that reinforce historical biases, and intrusive clarification burdens.
- **Autonomy & Privacy:** Refusal to answer questions (`declined`) must always be respected without punitive exclusion from basic service access.

---

## 10. Round 2 Implementation Roadmap

1. **Phase 1 (Days 1–3):** Implementation of the `NetworkX` / Edmonds Maximum Weight Matching engine within `policy.py`.
2. **Phase 2 (Days 4–5):** Calibration of the Value-of-Information (VoI) clarification logic and arrival rate estimators.
3. **Phase 3 (Days 6–7):** Docker container packaging, validation across 120 local test episodes, and reproducible artifact generation.
