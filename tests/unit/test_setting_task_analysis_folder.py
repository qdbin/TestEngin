import json
import os

import pytest

from app.setting import LMSetting


@pytest.mark.unit
def test_task_analysis_reads_task_folder_case_json(monkeypatch, tmp_path):
    monkeypatch.setattr("app.setting.DATA_PATH", str(tmp_path))

    task_id = "t1"
    collection_id = "c1"
    task_dir = tmp_path / task_id / collection_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "100.json").write_text("{}", encoding="utf-8")
    (task_dir / "200.json").write_text("{}", encoding="utf-8")

    task = {
        "taskId": task_id,
        "taskType": "normal",
        "downloadUrl": "http://example.invalid/file.zip",
        "testCollectionList": [
            {
                "collectionId": collection_id,
                "testCaseList": [
                    {"caseId": "100", "index": 3, "caseType": "API"},
                ],
            }
        ],
    }

    monkeypatch.setattr(LMSetting, "data_pull", lambda _self: None)
    monkeypatch.setattr(LMSetting, "file_unzip", lambda _self, _path: None)

    setting = LMSetting(task)
    plan = setting.task_analysis()

    assert collection_id in plan
    assert len(plan[collection_id]) == 2

    by_case = {item["test_case"].split("_")[1]: item for item in plan[collection_id]}
    assert by_case["100"]["test_case"] == "case_100_3"
    assert by_case["100"]["test_type"] == "API"
    assert os.path.basename(by_case["100"]["test_data"]) == "100.json"
    assert by_case["200"]["test_case"].startswith("case_200_")
    assert os.path.basename(by_case["200"]["test_data"]) == "200.json"


@pytest.mark.unit
def test_task_analysis_debug_materializes_case_json(monkeypatch, tmp_path):
    monkeypatch.setattr("app.setting.DATA_PATH", str(tmp_path))

    task = {
        "taskId": "t2",
        "taskType": "debug",
        "testCollectionList": [
            {
                "collectionId": "c9",
                "testCaseList": [{"caseId": "900", "index": 1, "caseType": "API"}],
            }
        ],
        "debugData": {
            "caseId": "900",
            "caseName": "demo",
            "comment": None,
            "functions": [],
            "params": {},
            "apiList": [],
        },
    }

    setting = LMSetting(task)
    plan = setting.task_analysis()
    case_path = plan["c9"][0]["test_data"]
    assert os.path.exists(case_path)
    with open(case_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    assert content["caseId"] == "900"
