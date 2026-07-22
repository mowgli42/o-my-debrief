# o-my-sim / live Redis capture notes (omd-h3a.11)

## Topics the recorder should subscribe to

Aligned with `o-my-sim` `uci_common.topics` and debrief `DEFAULT_TOPICS`:

| Topic | Typical publisher | Debrief event_type |
|-------|-------------------|--------------------|
| `uci.platform.status` | `platform-status-sim` | `systemStatus` (XML PlatformStatusReport) |
| `uci.task` / `uci.task.status` | tasking / engagement sims | `task` |
| `uci.signal.report` | sensor / feed publishers | `sensorCollect` (heuristic) |
| `uci.commlink.status` | commlink sims | `dissemination` / other |
| `uci.engagement.result` | BDA / engagement | `bda` / other |
| `uci.scenario.clock` | scenario clock | optional sync (future) |

## XML fidelity

`normalize_message()` accepts raw XML strings from Redis and extracts:

- Header: MessageID, Timestamp, MessageType
- Body fields: Callsign, Latitude/Longitude, FuelPercent, WeaponsRemaining, Readiness

Unit coverage: `tests/test_recorder.py` (no live Redis required).

## Live proof (manual)

```bash
# Terminal A — o-my-sim publishers + Redis
# Terminal B
python -m omy_debrief.recorder.cli --mode redis \
  --redis-url redis://127.0.0.1:6379/0 \
  --duration 60 --mission live-omy-sim --out data/debrief

# Then
curl -s 'http://127.0.0.1:8020/api/missions' | jq .
```

Success criteria: parquet row count > 0, at least one `systemStatus` with lat/lon/fuel, manifest lists `live-omy-sim`.
