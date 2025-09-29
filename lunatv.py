from io import BytesIO
import random
import string
import sys
import argparse
from huggingface_hub import HfApi

# ----------------- 参数解析 -----------------
parser = argparse.ArgumentParser(description="创建Hugging Face Space")
parser.add_argument("--token", type=str, required=True, help="Hugging Face Token需要写权限")
parser.add_argument("--image", type=str, default="", help="Docker 镜像地址")
parser.add_argument("--admin", type=str, required=True, help="管理员用户名（必填）")
parser.add_argument("--password", type=str, required=True, help="管理员密码（必填）")
parser.add_argument("--upstash", type=str, required=True, help="Upstash Token（必填）")
parser.add_argument("--endpoint", type=str, required=True, help="Upstash HTTPS Endpoint（必填）")

args = parser.parse_args()

# ----------------- 工具函数 -----------------
def generate_random_string(length=2):
    """生成包含至少一个字母的随机字符串"""
    if length < 1:
        return ""
    chars = string.ascii_letters + string.digits
    mandatory_letter = random.choice(string.ascii_letters)
    remaining_chars = random.choices(chars, k=length - 1)
    full_chars = remaining_chars + [mandatory_letter]
    random.shuffle(full_chars)
    return "".join(full_chars)

# ----------------- 主逻辑 -----------------
if __name__ == "__main__":
    token = args.token
    if not token:
        print("Token 不能为空")
        sys.exit(1)

    api = HfApi(token=token)
    user_info = api.whoami()
    if not user_info.get("name"):
        print("未获取到用户名信息，程序退出。")
        sys.exit(1)

    # 默认镜像
    userid = user_info.get("name")
    image = args.image or "ghcr.io/zxlwq/lunatv:latest"
    admin = args.admin
    password = args.password

    # 随机生成 Space 名称
    space_name = generate_random_string(2)
    repoid = f"{userid}/{space_name}"

    # 创建 README.md
    readme_content = f"""
---
title: {space_name}
emoji: 😻
colorFrom: red
colorTo: blue
sdk: docker
app_port: 3000
pinned: false
---
Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
"""
    readme_obj = BytesIO(readme_content.encode("utf-8"))

    # 创建 Space 并注入环境变量
    api.create_repo(
        repo_id=repoid,
        repo_type="space",
        space_sdk="docker",
        space_secrets=[
            {"key": "USERNAME", "value": admin},
            {"key": "PASSWORD", "value": password},
            {"key": "NEXT_PUBLIC_STORAGE_TYPE", "value": "upstash"},
            {"key": "UPSTASH_URL", "value": args.endpoint},
            {"key": "UPSTASH_TOKEN", "value": args.upstash},
        ],
    )

    # 上传 README.md
    api.upload_file(
        repo_id=repoid,
        path_in_repo="README.md",
        path_or_fileobj=readme_obj,
        repo_type="space",
    )

    # 上传 Dockerfile
dockerfile_content = f"""FROM {image}
RUN chmod -R 777 /app/public
"""
api.upload_file(
    repo_id=repoid,
    path_in_repo="Dockerfile",
    path_or_fileobj=BytesIO(dockerfile_content.encode("utf-8")),
    repo_type="space",
)


    print(f"Space 创建成功: {repoid}")
