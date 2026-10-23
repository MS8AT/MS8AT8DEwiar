"""MCP contract with a synthetic service; no real memory or model."""
from pathlib import Path
import sys
import json
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/core"))
from human_memory_stdio import dispatch
service=Mock()
service.health.return_value={"db_exists":True,"read_only":True,"model_calls":0}
def ask(method, **params):
    return dispatch({"id":1,"jsonrpc":"2.0","method":method,"params":params},service)
assert ask("initialize")["result"]["protocolVersion"] == "2025-06-18"
tools=ask("tools/list")["result"]["tools"]
assert len(tools)==2 and all(t["annotations"]["readOnlyHint"] for t in tools)
assert json.loads(ask("tools/call",name="human_memory_health",arguments={})["result"]["content"][0]["text"])["read_only"]
service.recall.side_effect=ValueError("SYNTHETIC-PRIVATE")
bad=ask("tools/call",name="human_memory_recall",arguments={"request":{}})
assert bad["result"]["isError"] and "SYNTHETIC-PRIVATE" not in json.dumps(bad)
assert ask("write")["error"]["code"] == -32601
print("ALL OK: PATCH-019; model_calls=0; network=0")
