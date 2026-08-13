# DCFA architecture and evidence flow

```mermaid
flowchart TB
    UI[Public TabCF-only UI or CLI] --> C[Typed specification compiler]
    C --> S[Explicit agent state machine]
    S --> T

    subgraph T[Track T continuous-IV adapter]
        G1[Role, no-W, backend, hash gates]
        B1[Explicit statistical backend]
        ST1[Stage 1 F of X given Z]
        DG[Empirical diagnostics and support gate]
        ST2[Stage 2 F of Y given X and V plus mean]
        ES[CDF, mean, quantile, risk, contrast tools]
        G1 --> B1 --> ST1 --> DG --> ST2 --> ES
    end

    subgraph H[Offline Track H policy adapter]
        D2[Provenance and categorical-action gates]
        H0[Missingness and baseline-balance audit]
        SP[Arm-stratified 60/20/20 split]
        TR[Training fit and validation selection]
        FR[Content-addressed policy freeze]
        TG[Test-outcome access gate]
        PV[Randomized effects; held-out DR, IPW, direct and paired contrasts]
        D2 --> H0 --> SP --> TR --> FR --> TG --> PV
    end

    subgraph A[Track A recorded benchmark]
        FX[Versioned cases and identical tool fixtures]
        FW[Fixed workflow]
        FA[Full explicit agent]
        GR[Deterministic graders; case-level pairing]
        FX --> FW --> GR
        FX --> FA --> GR
    end

    ES --> RB[Validated result bundle]
    PV --> RB
    GR --> AB[Test-only benchmark bundle]
    RB --> EL[Shared evidence ledger]
    RB --> AU[Append-only audit trail]
    EL --> RP[Text, tables and plots from the same bundle]
    AU --> AV[Independent identity, source-tree, hash and report verifier]
    RP --> AV

    H -. evaluation only; no public route .- UI
```

The dotted Hillstrom/UI edge is a prohibition, not a routing option. Numerical
causal calculations remain inside deterministic tools. The state machine may
compile, route, retry once, validate, cache, and explain; it may not calculate a
headline value or silently change the estimator, roles, policy, or evidence
track.

## Fail-closed release path

```mermaid
flowchart LR
    R[Candidate result] --> M{Markers and hashes match?}
    M -- no --> X[Block]
    M -- yes --> E{Every displayed value resolves to evidence?}
    E -- no --> X
    E -- yes --> W{Warnings and support preserved?}
    W -- no --> X
    W -- yes --> K{Track-specific release inputs complete?}
    K -- no --> X
    K -- yes --> P[Eligible report]
```

For Track T, the last gate includes a real TabPFN backend, locked execution,
release-eligible evidence, exact upstream commit, checkpoint hash, and runtime
image digest. For Track H real-RCT output, it includes provenance-complete real
data and a matching policy frozen before test-outcome access.
