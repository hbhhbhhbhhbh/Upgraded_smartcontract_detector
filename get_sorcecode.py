import requests
import json
import os
import time

# --- 配置区 ---
API_KEY = 'Your API KEY'
BASE_URL = 'https://api.etherscan.io/v2/api'   # 修正为正确的 endpoint


def get_contract_source(address):
    params = {
        'module': 'contract',
        'action': 'getsourcecode',
        'address': address,
        'apikey': API_KEY,
        'chainid': '1'
    }
    headers = {
        'User-Agent': 'Your user-agent'
    }

    try:
        response = requests.get(BASE_URL, params=params, headers=headers)
        response.raise_for_status()  # 检查 HTTP 错误
        data = response.json()

        if data['status'] == '1' and data['result']:
            result = data['result'][0]
            source_code = result['SourceCode']
            contract_name = result['ContractName']
            return contract_name, source_code
        else:
            print(f"抓取失败: {address} - {data.get('message', '未知错误')}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {address} - {e}")
        return None, None
    except json.JSONDecodeError:
        print(f"响应不是有效的 JSON，可能 API 地址错误或服务异常: {address}")
        # 可选：打印响应内容前200字符以便调试
        # print(response.text[:200])
        return None, None


def save_source(address, name, source):
    folder = "contracts"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # 检查是否是 JSON 格式（多文件项目通常以 {{ 开头）
    if source.startswith('{{'):
        # 处理 Etherscan 特有的双大括号格式
        json_content = source[1:-1]  # 去掉外层的一对大括号
        try:
            source_data = json.loads(json_content)
        except json.JSONDecodeError:
            print(f"多文件 JSON 解析失败，将作为单文件保存: {address}")
            # 降级为单文件保存
            file_path = os.path.join(folder, f"{name}_{address}.sol")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(source)
            return "single", file_path

        # 创建子文件夹存放多文件
        subfolder = os.path.join(folder, f"{name}_{address}")
        os.makedirs(subfolder, exist_ok=True)

        # 遍历所有源文件
        for file_path, content in source_data.get('sources', {}).items():
            full_path = os.path.join(subfolder, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content.get('content', ''))
        print(f"✅ 多文件保存成功: {subfolder}")
        return "multi", subfolder
    else:
        # 单文件直接保存
        file_path = os.path.join(folder, f"{name}_{address}.sol")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(source)
        print(f"✅ 单文件保存成功: {file_path}")
        return "single", file_path


# --- 测试运行 ---
verified_contract = {
    'contracts address'
}

for test_address in verified_contract:
    print(f"正在处理: {test_address}")
    contract_name, source_code = get_contract_source(test_address)  # 接收两个返回值
    if contract_name and source_code:
        save_source(test_address, contract_name, source_code)
    else:
        print(f"跳过地址: {test_address}")
    time.sleep(0.2)  # 避免超过速率限制（免费版每秒最多5次）