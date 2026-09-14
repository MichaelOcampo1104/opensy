import json

with open("catalogue_local.json", encoding="utf-8-sig") as f:
    local = json.load(f)
with open("catalogue_remote.json", encoding="utf-8-sig") as f:
    remote = json.load(f)
merged = {}
for entry in remote:
    merged[entry["UniqueID"]] = entry
for entry in local:
    merged[entry["UniqueID"]] = entry  # local wins if same UniqueID exists on both sides

result = list(merged.values())

with open("opensees_catalogue.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"Merged {len(result)} entries (local had {len(local)}, remote had {len(remote)})")