# step.py
import json
import secrets
import string
import threading
import time
import uuid
from pathlib import Path
from django.conf import settings
from django.template.defaultfilters import random
from pydantic import UUID1

from utils import test1_code_ge
from utils.websocket_service import websocket_service

compile_path = str(Path(settings.MEDIA_ROOT) / 'compile').replace('\\', '/') + '/'
save_path = str(Path(settings.MEDIA_ROOT) / 'output').replace('\\', '/') + '/'
jason_path = str(Path(settings.MEDIA_ROOT) / 'history').replace('\\', '/') + '/'
modular_path = Path(settings.MEDIA_ROOT) / 'compile' / 'modular.c'
structural_path = Path(settings.MEDIA_ROOT) / 'compile' / 'structural.c'
procedural_path = Path(settings.MEDIA_ROOT) / 'compile' / 'procedural.c'


def send_to_topic(topic_id, status, message, step):
    process_step = {
        "type": "CODE_GEN",
        "step": step,
        "content": message,
        "status": status,
        "role": "ai"
    }
    websocket_service.send_to_topic(topic_id=topic_id, data=process_step)


def send_to_topic_suggestion(topic_id, description, output="output.c",):
    data = {
        "type": "OUTPUT_CODE",
        "content": [{
            "key": generate_numeric_id(),
            "icon": "CoffeeOutlined",
            "description": description,
            "output": output
        },{
            "key": generate_numeric_id(),
            "icon": "FireOutlined",
            "description": 'Click to open Proteus 8 Professional',
            "output": 'open.exe'
        }],
        "role": "suggestion"
    }
    websocket_service.send_to_topic(topic_id=topic_id, data=data)
def send_to_topic_ai(topic_id, content="output.c"):
    data = {
        "type": "AI_RELY",
        "content": content,
        "role": "ai"
    }
    websocket_service.send_to_topic(topic_id=topic_id, data=data)

def send_to_topic_file(topic_id, file_name="output.c"):
    data = {
        "key": generate_numeric_id(),
        "type": "OUTPUT_CODE",
        "content": [{
            "uid": generate_numeric_id(),
            "name": file_name,
            "size": 100,
            "description": 'Click to download file',
        }],
        "role": "file"
    }
    websocket_service.send_to_topic(topic_id=topic_id, data=data)


def start_async(file_path1, file_path2, topic_id=''):
    """异步启动函数 - 立即返回，不阻塞"""
    thread = threading.Thread(
        target=_process_code_generation,
        args=(file_path1, file_path2, topic_id),
        name=f"CodeGen-{topic_id}"  # 给线程命名，便于调试
    )
    thread.daemon = True  # 守护线程，主程序退出时自动结束
    thread.start()
    print(f"已启动异步任务，线程ID: {thread.ident}, 主题ID: {topic_id}")


def ask_async(topic_id='',message=''):
    """异步启动函数 - 立即返回，不阻塞"""
    thread = threading.Thread(
        target=ask,
        args=( topic_id,message),
        name=f"CodeGen-{topic_id}"  # 给线程命名，便于调试
    )
    thread.daemon = True  # 守护线程，主程序退出时自动结束
    thread.start()
    print(f"已启动异步任务，线程ID: {thread.ident}, 主题ID: {topic_id}")

def ask(topic_id,message):
    content = test1_code_ge.test2_ask_question(jason_path=jason_path,chat_content=message)
    send_to_topic_ai(topic_id,content)


def _process_code_generation(file_path1, file_path2, topic_id=''):
    try:
        print(f"开始处理代码生成任务，主题ID: {topic_id}")
        # 发送开始消息
        test1_code_ge.test1_with_compile_feedback(
            path=file_path1,
            compile_path=compile_path,
            save_path=save_path,
            jason_path=jason_path, topic_id=topic_id
        )
        test1_code_ge.reference_code_ge(
            path2=file_path2,
            compile_path=compile_path,
            save_path=save_path,
            jason_path=jason_path,
            topic_id=topic_id
        )
        # 第三步：suggestion_fix_code
        print("开始第三步：suggestion_fix_code")
        send_to_topic(topic_id, "process", "Starting to check initial code issues...", 4)
        suggestion = test1_code_ge.suggestion_fix_code(
            compile_path + "output.c",
            path1=modular_path,
            path2=structural_path,
            path3=procedural_path,
            json_path=jason_path
        )
        time.sleep(2)
        send_to_topic(topic_id, "finish", "Step five completed, correction suggestions have been generated...", 4)
        # 第四步：test1_fix_with_compile_feedback
        test1_code_ge.test1_fix_with_compile_feedback(
            suggestion,
            compile_path=compile_path,
            save_path=save_path,
            jason_path=jason_path,
            topic_id=topic_id
        )
        send_to_topic(topic_id, "process", "Start generating thinking process...", 7)
        time.sleep(2)
        send_to_topic(topic_id, "finish", "Step eight, thinking process generation completed...", 7)
        send_to_topic_suggestion(topic_id, "Click to open file", "output.c")
        send_to_topic_file(topic_id, file_name="output.c")
        send_to_topic_file(topic_id, file_name="TESToutput.hex")
        print(f"代码生成任务完成，主题ID: {topic_id}")
    except Exception as e:
        print(f"处理错误: {e}")
        error_message = {
            "type": "CODE_GEN",
            "step": 0,
            "message": f"处理失败: {str(e)}",
            "status": "failed",
            "error": str(e)
        }
        websocket_service.send_to_topic(topic_id=topic_id, data=error_message)


# 保持原有的同步函数，以防需要同步调用
def start(file_path1, file_path2, topic_id=''):
    """同步执行函数 - 会阻塞直到完成"""
    return _process_code_generation(file_path1, file_path2, topic_id)


# 可选：获取当前运行的任务信息
def get_running_tasks():
    """获取当前运行的代码生成任务"""
    running_tasks = []
    for thread in threading.enumerate():
        if thread.name.startswith("CodeGen-"):
            running_tasks.append({
                'thread_id': thread.ident,
                'thread_name': thread.name,
                'is_alive': thread.is_alive()
            })
    return running_tasks

def generate_numeric_id(length=10):
    return ''.join(secrets.choice(string.digits) for _ in range(length))