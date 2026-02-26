Today: February 23, 2026

8 weeks from now: April 20, 2026

# **OVERARCHING OBJECTIVE (SMART)**

Specific:

Build and publish three quantum software artifacts:

1. Qiskit-based circuit benchmarking suite

2. Variational algorithm experiment with gradient variance scaling analysis

3. Transpilation / compilation optimization experiment with measurable depth reductions

Measurable:

Each artifact must include:

* Code

* Tests

* Benchmarks

* Plots

* Reproducible instructions

* Clear README with results table

Achievable:

Given your systems \+ HPC background, this is realistic in 8 weeks with disciplined focus.

Relevant:

Directly addresses missing quantum SWE signals:

* Framework usage

* Algorithmic depth

* Gradient behavior

* Compilation awareness

* Noise modeling

Time-bound:

Complete by April 20, 2026\.

---

# **STRUCTURE OF THE 8-WEEK PLAN**

We split into 4 phases:

* Weeks 1–2: Framework Fluency \+ Circuit Benchmarking

* Weeks 3–4: Noise Modeling \+ Shot Scaling

* Weeks 5–6: Variational Algorithm \+ Gradient Scaling Study

* Weeks 7–8: Transpilation Optimization \+ Final Polish

Each phase produces a tangible artifact.

---

# **WEEKS 1–2 (Feb 23 – March 8\)**

## **Phase 1: Qiskit Fluency \+ Benchmark Suite**

### **Objective**

Build a Qiskit-based benchmarking harness and compare against your custom simulator.

---

## **Deliverables by March 8**

1. Repo: quantum-benchmark-suite

2. Implement:

   * Random circuit generator

   * IQP-style circuit generator (commuting diagonal gates)

   * Configurable qubit count (2–12)

   * Configurable depth

3. Run on:

   * Qiskit Aer simulator

   * Your custom statevector simulator

4. Measure:

   * Runtime vs qubits

   * Runtime vs depth

   * Memory footprint (where possible)

5. Produce:

   * 2–3 plots

   * Results table in README

---

## **Methodology**

* Fixed seeds

* 5 runs per config

* Report mean ± std

* Use consistent hardware

* Store configs in YAML

---

## **Success Criteria**

You can answer:

* How does Aer compare to your simulator?

* Where does scaling break?

* What is the constant factor difference?

---

# **WEEKS 3–4 (March 9 – March 22\)**

## **Phase 2: Noise \+ Shot Scaling**

### **Objective**

Demonstrate understanding of noise and measurement cost.

---

## **Deliverables by March 22**

1. Add noise models:

   * Amplitude damping

   * Depolarizing

2. Implement shot-based sampling experiments

3. Measure:

   * Fidelity vs noise parameter

   * Variance vs shot count

   * Shot cost vs precision

4. Add:

   * Noise sweep plots

   * Shot scaling plots

---

## **Methodology**

* Sweep γ ∈ \[0, 0.2\]

* Sweep shots ∈ \[128, 256, 512, 1024, 2048\]

* Compute:

  * Variance of estimator

  * Convergence behavior

---

## **Success Criteria**

You can answer:

* How many shots are needed for stable estimation?

* How does noise impact expectation estimation?

* Where do classical simulation assumptions break?

---

# **WEEKS 5–6 (March 23 – April 5\)**

## **Phase 3: Variational Algorithm \+ Gradient Scaling**

This is the make-or-break phase.

---

## **Objective**

Implement a small variational experiment and study gradient variance vs qubits.

---

## **Deliverables by April 5**

1. Implement:

   * Simple VQE or IQP-based MMD experiment

2. Compute:

   * Gradient via parameter-shift rule

3. Sweep:

   * Qubits: 2–10

4. Measure:

   * Gradient variance

   * Loss landscape roughness

5. Plot:

   * Variance vs n

   * Gradient norm distribution

---

## **Methodology**

* Random parameter initialization

* 20 samples per n

* Fixed seed control

* Track exponential decay behavior

---

## **Success Criteria**

You can answer:

* Does variance decay exponentially?

* Does IQP structure mitigate barren plateau?

* What scaling regime do you observe?

Even negative results are fine.

---

# **WEEKS 7–8 (April 6 – April 20\)**

## **Phase 4: Transpilation / Compilation Experiment**

This phase signals maturity.

---

## **Objective**

Demonstrate compilation awareness.

---

## **Deliverables by April 20**

Option A (Recommended):

* Custom transpiler pass:

  * Cancel adjacent inverse gates

  * Merge rotations

* Measure:

  * Circuit depth before/after

  * Gate count reduction

Option B:

* Compare optimization levels (0–3)

* Measure:

  * Depth reduction

  * Runtime difference

---

## **Add:**

* Table:

| Circuit | Depth Before | Depth After | % Reduction |
| :---: | :---: | :---: | :---: |

---

## **Success Criteria**

You can answer:

* How does transpilation change depth?

* What optimizations matter most?

* How does hardware topology affect mapping?

---

# **FINAL OUTPUT BY APRIL 20**

You will have:

1. Simulator \+ benchmarking

2. Noise \+ shot scaling study

3. Variational gradient scaling study

4. Transpilation optimization experiment

That’s 4 artifacts.

Now you are interviewable.

---

# **WEEKLY CHECKPOINT STRUCTURE**

Every Sunday:

* Update README

* Add plots

* Refactor code

* Ensure reproducibility

* Tag release version

---

# **HOW THIS CHANGES YOUR PROFILE**

Current:

Systems engineer exploring quantum.

After 8 weeks:

Quantum software engineer with algorithmic \+ performance \+ compilation depth.

Massive difference.

---

# **Risk Management**

Biggest risks:

* Over-scoping

* Writing too much theory

* Not publishing intermediate results

Rule:

Publish partial results early.

---

