# UI Wiring Checklist

Every backend feature that needs UI display MUST verify this chain:

## The Chain

```
1. Backend Logic      -> Does X happen?
2. Return Value       -> Is X included in function return?
3. Endpoint Response  -> Is X in the JSON response?
4. Godot Receives     -> Does GDScript parse X?
5. Godot Displays     -> Does UI show X?
```

## Verification Steps

### Step 1: Backend Logic
- [ ] Feature has unit tests
- [ ] Tests verify the data is generated

### Step 2: Return Value
- [ ] Function returns the data (not just generates it)
- [ ] Caller captures the return value
- [ ] Data flows up to endpoint handler

### Step 3: Endpoint Response
- [ ] `main.py` endpoint includes data in response
- [ ] Test with: `curl -X POST http://localhost:8005/command -H "Content-Type: application/json" -d '{"command": "end turn"}'`
- [ ] Verify JSON contains expected fields

### Step 4: Godot Receives
- [ ] GDScript has callback for this endpoint
- [ ] Callback parses the relevant fields
- [ ] Add `print()` to verify: `print("Received: ", data)`

### Step 5: Godot Displays
- [ ] UI scene exists (.tscn)
- [ ] Scene is instantiated when data arrives
- [ ] Scene receives and displays the data
- [ ] Scene has dismiss/continue flow

## Red Flags (Wiring Gaps)

- "Backend tests pass but UI doesn't show it" -> Check steps 2-5
- "Works in curl but not in Godot" -> Check steps 4-5
- "Godot receives data but nothing appears" -> Check step 5
- "Data is None in Godot" -> Check step 3

## Features Wiring Status

| Feature | Endpoint | main.py passes? | Godot Handler | Popup/Display |
|---------|----------|-----------------|---------------|---------------|
| Strategic Reports | /command (end_turn) | Yes | main.gd:482 | strategic_report_popup |
| Interrupt Popup | /command (end_turn) | Yes | main.gd:164 | interrupt_popup |
| Clarification | /command | Yes | main.gd:172 | clarification_popup |
| Enemy Phase | /command (end_turn) | Yes | main.gd:472 | enemy_phase_dialog |
| Objection | /command | Yes | main.gd | objection handling |
| Independent Report | /command (end_turn) | Yes | main.gd | independent report |

## Known Bug Pattern

The most common wiring gap: **executor returns data but main.py doesn't include it in the response dict.**

main.py builds its response dict explicitly (lines 235-242). Any new field from executor must be explicitly added after the base dict construction. Pattern:

```python
# In main.py, after building base response dict:
if result.get("new_feature_data"):
    response["new_feature_data"] = result["new_feature_data"]
```
