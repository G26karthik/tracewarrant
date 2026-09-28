# Optimization — proposed, not implemented

Decision variables begin as finite replica counts. Objective is cost over an explicit horizon; constraints cover P(successful completion within deadline), resource/provider limits, quality floor, budget and calibration envelope. Failed, rejected and timed-out work counts against the SLO. A plan outside the model envelope is unknown, not feasible.

Enumerate tiny spaces exactly and publish every candidate's measured/simulated evidence. Compare greedy allocation and later CP-SAT/MILP only where cost warrants them; the nonlinear stochastic simulator is not automatically a linear constraint system. Return a Pareto set for cost, latency and reliability. Energy appears only when supported by measurements.

Use common random numbers for paired candidate comparison, then independent seeds and held-out traces for finalists. Evaluate pessimistic correlated scenarios and report decision sensitivity. Abstain when plausible model errors change the preferred action or relevant inputs are extrapolated. A candidate recommendation is an experimental plan, never an automated deployment action.
