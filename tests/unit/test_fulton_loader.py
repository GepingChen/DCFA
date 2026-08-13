from __future__ import annotations

import csv

import pytest

from dcfa.errors import DCFAError, ErrorCode
from dcfa.tabcf_iv.fulton import FULTON_EXPECTED_ROWS, load_fulton_csv


def _write_fixture(path) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("rownames", "lavgprc", "wave2", "ltotqty"))
        writer.writeheader()
        for index in range(FULTON_EXPECTED_ROWS):
            writer.writerow(
                {
                    "rownames": index + 1,
                    "lavgprc": 1.0 + index / 100.0,
                    "wave2": 0.5 + index / 200.0,
                    "ltotqty": 2.0 - index / 300.0,
                }
            )


def test_fulton_loader_records_provenance_and_roles(tmp_path) -> None:
    path = tmp_path / "fish.csv"
    _write_fixture(path)
    dataset = load_fulton_csv(
        path,
        exact_source="https://example.test/fish.csv",
        retrieval_date="2026-08-08",
        license_note="Local research-use fixture.",
    )
    assert dataset.manifest.row_count == FULTON_EXPECTED_ROWS
    assert dataset.manifest.source_kind == "real_iv_application_without_oracle"
    assert dataset.manifest.evidence_status.value == "development_only"
    assert set(dataset.columns) == {"Z", "X", "Y"}


def test_fulton_loader_refuses_missing_provenance_before_file_access(tmp_path) -> None:
    with pytest.raises(DCFAError) as exc_info:
        load_fulton_csv(
            tmp_path / "missing.csv",
            exact_source="",
            retrieval_date="",
            license_note="",
        )
    assert exc_info.value.code is ErrorCode.INVALID_DATA
