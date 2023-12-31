import json
import sys

import random
import string

# 从所有字母和数字中生成随机字符串
def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

# 读取每个panel中的 target
# 将 target 的 legend 命名为 namespace + subsystem + title + [name]
def read_targets(file_name, target_id_len = 5):
    with open(file_name, 'r', encoding="utf-8") as f:
        data = json.load(f)
    
    targets = []
    current_namespace = data["title"]
    current_subsystem = ""

    for panel in data["panels"]:
        if panel["type"] == "row":
            # do row
            current_subsystem = panel["title"]
           
        elif panel["type"] == "timeseries":
            # do timeseries
            current_name = panel["title"]
            
            for target in panel["targets"]:
                target["refId"] = generate_random_string(target_id_len)

                legend = [current_namespace, current_subsystem, current_name]
                if target["legendFormat"] != "__auto":
                    legend.append(target["legendFormat"])
                    
                legend = ' '.join(legend).replace(' ', '_').lower()
                target["legendFormat"] = legend

                targets.append(target)
    return targets


target_id_len = 5
grafana_jsons = ["./host.json", "./libvirt.json"]

targets = []
for file in grafana_jsons:
    targets = targets + read_targets(file, target_id_len) 

result_json = "./all_in_one.json"
with open(result_json, 'r') as f:
    data = json.load(f)

    try:
        data["panels"][0]["targets"] = targets
    except:
        print("invalid grafana format")
        sys.exit(1)
    
with open(result_json, 'w') as f:
    json.dump(data, f)


schemas = [{"targetField": target["legendFormat"], "destinationType": "number"} for target in targets]

schemas.append({"targetField": "\"Time\"", "destinationType": "time"})
offline_json = "./offline.json"
with open(offline_json, 'r') as f:
    data = json.load(f)

    try:
        data["panels"][0]["transformations"][0]["options"]["conversions"] = schemas
        
    except:
        print("invalid grafana format")
        sys.exit(1)

with open(offline_json, 'w') as f:
    json.dump(data, f)


