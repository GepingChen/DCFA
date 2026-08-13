# Locked remote TabPFN runner contract

The macOS development environment is not a release environment. The only
allowed path for a future remote Linux/GPU Track T run is a fully populated copy
of `evaluation/configs/tabpfn_locked_runtime.example.json`.

The manifest freezes the exact Python, NumPy, SciPy, scikit-learn, PyTorch, and
TabPFN versions; the inspected TabCF source commit; the TabPFN checkpoint path
and SHA-256; and the immutable container image digest. The runner must expose
that digest as `DCFA_RUNTIME_IMAGE_DIGEST`. Validation fails before model import
or fit when any value is missing, a placeholder remains, the source checkout is
different, or a hash differs.

After the image and checkpoint have been provisioned by the operator, validate
the host with:

```bash
dcfa validate-tabpfn-runtime /absolute/path/to/tabpfn_locked_runtime.json
```

A successful validation only establishes environment identity. It does not by
itself establish estimator quality, statistical validity, or release readiness.
The locked Track T pipeline must still be run, its artifacts independently
verified, and its release gate passed. The local sklearn fallback must never be
installed into or substituted within that locked run.
