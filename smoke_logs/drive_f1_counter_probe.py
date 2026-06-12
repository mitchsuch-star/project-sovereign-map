"""F1/F3 probe — does a COUNTER_OFFER preview verdict ever yield an actual
counter dialogue? And do armistice preview odds survive to send-time?

Path: typed bilateral proposal -> proposal_confirm preview (estimate +
outcome) -> execute_proposal -> end turn(s) -> inspect what came back
(counter_offer_response dialogue / proposal_result_popup / nothing).
"""
import json
import urllib.request

BASE = "http://127.0.0.1:8005"


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def act(action, params=None):
    body = {"choice": action}
    body["action_params"] = dict(params or {}, action=action)
    return post("/respond_to_diplomatic_dialogue", body)


def show_dialogue(tag, resp):
    d = resp.get("diplomatic_dialogue") or {}
    print(f"--- {tag}")
    print("    dtype:", d.get("type"))
    print("    estimate:", d.get("acceptance_estimate"),
          "| outcome:", d.get("acceptance_outcome"))
    print("    harshness:", d.get("harshness_label"))
    for opt in d.get("options", []):
        if opt.get("action") == "execute_proposal" and opt.get("terms"):
            t = opt["terms"]
            print("    terms.type:", t.get("type"),
                  "| terms.proposal_type:", t.get("proposal_type"))
            print("    demands:", t.get("demands"))
            print("    sweeteners:", t.get("sweeteners"))
    return d


def drive_send_and_resolve(proposal_cmd, tag):
    print(f"\n===== {tag}: '{proposal_cmd}' =====")
    r = post("/command", {"command": proposal_cmd})
    d = show_dialogue("PREVIEW", r)
    if not d or d.get("type") not in ("proposal_confirm", "proposal_execute"):
        print("    !! no proposal_confirm mounted; message:",
              (r.get("message") or "")[:160])
        return
    send = act("execute_proposal")
    print("    send message:", (send.get("message") or "")[:160])
    # End turns until the proposal resolves (max 3)
    for i in range(1, 4):
        et = post("/command", {"command": "end turn"})
        dd = et.get("diplomatic_dialogue") or {}
        popup = et.get("proposal_result_popup")
        incoming = et.get("incoming_proposal")
        print(f"    end_turn #{i}:")
        if dd:
            print("       dialogue.type:", dd.get("type"))
            print("       dialogue.options:", [o.get("action") for o in dd.get("options", [])])
            print("       talleyrand:", (dd.get("talleyrand_text") or "")[:200])
        if popup:
            print("       result_popup outcome:", popup.get("outcome"),
                  "| type:", popup.get("proposal_type"))
            print("       result_popup msg:", (popup.get("message") or "")[:160])
            print("       feedback:", (popup.get("feedback") or "")[:160])
        if incoming:
            print("       incoming_proposal: from", incoming.get("from_nation"),
                  "| is_counter:", incoming.get("is_counter_offer"))
        if dd or popup or incoming:
            return
    print("    !! nothing came back after 3 turns")


print("== fresh game ==")
post("/new_game", {})

# Leg A: bilateral peace with Britain (suggested terms carry demands when
# winning -> removal path may produce a counter)
drive_send_and_resolve("propose peace with Britain", "LEG A peace")

print("\n== fresh game ==")
post("/new_game", {})

# Leg B: armistice with Britain (suggested terms = bare or sweetener-only ->
# the desire-table path is the only counter route)
drive_send_and_resolve("propose armistice with Britain", "LEG B armistice")
