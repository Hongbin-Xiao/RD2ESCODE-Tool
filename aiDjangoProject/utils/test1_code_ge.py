import json
import os
import re
import importlib
import time
import chardet
from openai import OpenAI
from utils.testProgrem import autotest
from utils.websocket_service import websocket_service

autotest = autotest()


# ##########初始代码生成
# def test1(path='./需求文档.txt', model_name='gpt-3.5-turbo'):
#     import json
#     import os
#     import re
#     with open(path, 'r', encoding='utf-8') as file:
#         content1 = file.read()
#     model_name = 'gpt-3.5-turbo'
#     from openai import OpenAI
#     os.environ["http_proxy"] = "http://127.0.0.1:7890"  # 指定代理，解决连接问题
#     os.environ["https_proxy"] = "http://127.0.0.1:7890"  # 指定代理，解决连接问题
#
#     # 需求文档提示词写入
#     messages1 = [
#         {"role": "system",
#          "content": "You will act as an experienced embedded systems design engineer, implementing an embedded system through code based on the given requirements document.\n"
#                     "Between the two""---""below is a requirements document，Based on this information, first generate the steps required to build the system and the complete C code, "
#                     "implementing each functional part step by step.The following are the notes for generating the code:"
#                     "\n1.It is forbidden to use data as a parameter.\n2.The code compiler is Keil uVision5.\n3.Assume that there are no known driver files.\n4The designed code must implement all functions.\n5.、The final output of the complete code must be in C language format, specifically:```code your code```，where ""your code"" is the complete C code."}
#     ]
#     userinput1 = 'requirements document：\n---\n' + content1 + '\n---'
#     messages1.append({"role": "user", "content": userinput1})
#
#     # 调用模型生成代码
#     client = OpenAI(api_key="your api")
#     suggestion = ""
#     client.base_url = "https://ai-yyds.com/v1"
#     completion = client.chat.completions.create(model=model_name, messages=messages1)
#
#     # 写入代码
#     text1 = completion.choices[0].message.content
#     messages1.append({"role": "assistant", "content": text1})  # 记录回复
#     # 匹配以```开头和```结尾的代码块，支持可选的语言标识
#     pattern = r"```code(?:\w+)?\n(.*?)```"
#     # re.DOTALL 让 . 匹配换行
#     code_blocks = re.findall(pattern, text1, re.DOTALL)
#     if code_blocks:
#         with open('output.c', 'w', encoding='utf-8') as f:
#             f.write(code_blocks[0])
#         with open('initial_output.c', 'w', encoding='utf-8') as f:
#             f.write(code_blocks[0])
#
#         print('代码已保存为 output_code.c')
#     else:
#         print('未找到代码块')
#
#     with open("chat_history.json", "w", encoding="utf-8") as f:
#         json.dump(messages1, f, ensure_ascii=False, indent=2)
#
#     return messages1


######################################################初始代码生成+编译反馈
def send_to_topic(topic_id, status, message, step):
    data = {
        "type": "CODE_GEN",
        "step": step,
        "content": message,
        "status": status,
        "role": "ai"
    }
    websocket_service.send_to_topic(topic_id=topic_id, data=data)


def test1_with_compile_feedback(
        path='./需求文档.txt',
        model_name='claude-sonnet-4-20250514',
        max_retry=3,
        compile_path='./C51_codes/',
        save_path='./C52_codes/',
        jason_path='./',
        topic_id=''
):
    send_to_topic(topic_id, "process", "Okay, let's start processing the code generation task....", 0)
    text2_tag = 0
    import json, os, re
    with open(path, 'r', encoding='utf-8') as file:
        content1 = file.read()
    print("开始执行~test1_with_compile_feedback")
    from openai import OpenAI
    os.environ["http_proxy"] = "http://127.0.0.1:7890"
    os.environ["https_proxy"] = "http://127.0.0.1:7890"

    messages1 = [
        {"role": "system",
         "content": "You will act as an experienced embedded systems design engineer, "
                    "implementing an embedded system through code based on the given requirements document."
                    "Between the two""---""below is a requirements document，Based on this information, "
                    "first generate the steps required to build the system and the complete C code, "
                    "implementing each functional part step by step.The following are the notes for generating the code:\n"
                    "1.It is forbidden to use data as a parameter.\n"
                    "2.The code compiler is Keil uVision5.\n"
                    "3.Assume that there are no known driver files.\n"
                    "4.The designed code must implement all functions.\n"
                    "5.The final output of the complete code must be in C language format, "
                    "specifically:```code your code```，where ""your code"" is the complete C code."}
    ]
    userinput1 = 'Requirements document：\n---\n' + content1 + '\n---'
    messages1.append({"role": "user", "content": userinput1})

    client = OpenAI(api_key="your api")
    client.base_url = "https://ai-yyds.com/v1"

    final_messages = None  # 用于保存最终对话
    # 1. 生成代码
    completion = client.chat.completions.create(model=model_name, messages=messages1)

    text1 = completion.choices[0].message.content
    # messages1.append({"role": "assistant", "content": text1})
    # 2. 提取代码
    pattern = r"```(?:code\w*|c\w*)\n(.*?)```"
    code_blocks = re.findall(pattern, text1, re.DOTALL)



    #messages1.append({"role": "assistant", "content": text1})




    messages2 = messages1.copy()


    if code_blocks:
        os.makedirs(compile_path, exist_ok=True)  # 确保目录存在
        with open(compile_path + "output.c", 'w', encoding='utf-8') as f:
            f.write(code_blocks[0])
        with open(compile_path + "initial_output.c", 'w', encoding='utf-8') as f:
            f.write(code_blocks[0])
        print('代码已保存为' + compile_path + 'output.c')
    ########保存初始生成相关信息（不保存代码）
    else:
        print('未找到代码块')
        return text1
    with open(jason_path + "chat_history.json", "w", encoding="utf-8") as f:
        json.dump(messages1, f, ensure_ascii=False, indent=2)
    send_to_topic(topic_id, "finish", "Step one completed: The initial code has been generated.", 0)
    send_to_topic(topic_id, "process", "Starting compilation feedback and code revision...", 1)
    # 3. 编译并获取反馈
    text2 = ''
    for i in range(max_retry):
        # 3. 编译并获取反馈
        tag, err_inf, _ = autotest.start(compile_path + 'output.c', compile_path, save_path)
        if tag:

            print("Compilation Successful！")
            break
        else:
            print("编译错误，准备反馈给模型修正...")
            new_user_input = (
                    "The C code you generated earlier failed to compile in Keil uVision5. "
                    "Please revise your code according to the following compiler feedback and output as required:"
                    "###\Revised C Code###\n```code your code```\nCompiler feedback：" + err_inf + "\n"
            )
            messages2.append({"role": "user", "content": new_user_input})
            completion = client.chat.completions.create(model=model_name, messages=messages2)
            text2 = completion.choices[0].message.content
            messages2.append({"role": "assistant", "content": text2})
            text2_tag = 1
            # 2. 提取代码
            #####匹配提取代码
            pattern = r"```(?:code\w*|c\w*)\n(.*?)```"
            code_blocks1 = re.findall(pattern, text1, re.DOTALL)
            if code_blocks1:
                os.makedirs(compile_path, exist_ok=True)  # 确保目录存在
                with open(compile_path + "output.c", 'w', encoding='utf-8') as f:
                    f.write(code_blocks1[0])
                print('代码已保存为' + compile_path + 'output.c')
            else:
                print('未找到代码块')
    if text2_tag == 0:
        messages2.append({"role": "user", "content": 'Compilation Successful！'})
    with open(jason_path + "compile_history.json", "w", encoding="utf-8") as f:
        json.dump(messages2, f, ensure_ascii=False, indent=2)
    # 只保存最后一次生成正确代码的对话内容
    if text2_tag==1:
        messages1.append({"role": "assistant", "content": text2})
        with open(jason_path + "chat_history.json", "w", encoding="utf-8") as f:
            json.dump(messages1, f, ensure_ascii=False, indent=2)

    else:
        messages1.append({"role": "assistant", "content": text1})
        print("没有生成通过编译的代码，保存原本对话内容。")
        with open(jason_path + "chat_history.json", "w", encoding="utf-8") as f:
            json.dump(messages1, f, ensure_ascii=False, indent=2)

    print("输出成功！！！！")
    send_to_topic(topic_id, "finish", "Step two correction compilation completed...", 1)
    return messages1


#########交互测试用例
def test2(path='./chat_history.json', model_name='gpt-3.5-turbo'):
    import json
    import os
    import re
    with open("chat_history.json", "r", encoding="utf-8") as f:
        loaded_messages = json.load(f)
    print("加载的对话历史：")
    # for msg in loaded_messages:
    # print(f"{msg['role']}: {msg['content']}")
    # 6. 继续对话
    new_user_input = input("请输入你的问题: ")
    loaded_messages.append({"role": "user", "content": new_user_input})
    # 调用模型生成代码
    client = OpenAI(api_key="your api")
    suggestion = ""
    client.base_url = "https://ai-yyds.com/v1"
    completion = client.chat.completions.create(model=model_name, messages=loaded_messages)
    new_reply = completion.choices[0].message.content
    loaded_messages.append({"role": "assistant", "content": new_reply})
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(loaded_messages, f, ensure_ascii=False, indent=2)
    return loaded_messages


##########参考代码生成组件
def extract_structural_code(text):
    """
    提取结构化编程风格参考下的C代码
    """
    pattern = re.compile(
        r'###\s*structured programming style reference\s*###\s*```c(.*?)```', re.DOTALL| re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def extract_modular_code(text):
    """
    提取模块化编程风格参考下的C代码
    """
    pattern = re.compile(
        r'###\s*modular programming style reference\s*###\s*```c(.*?)```', re.DOTALL| re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""

    # def extract_procedural_code(text):
    #"""
    #提取面向过程编程风格参考下的C代码
    #"""


# pattern = re.compile(
#    r'###\s*面向过程(编程)?风格参考\s*###\s*```c(.*?)```', re.DOTALL)
# match = pattern.search(text)
# return match.group(1).strip() if match else ""

def extract_procedural_code(text):
    """
    提取面向过程编程风格参考下的C代码
    """
    pattern = re.compile(
        r'###\s*procedural programming style reference\s*###\s*```c(.*?)```', re.DOTALL| re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def save_code(code, filename, save_path='./C51_codes/'):
    """
    保存代码到 ./C51_codes/ 下指定文件
    """
    os.makedirs(save_path, exist_ok=True)
    with open(save_path + filename, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"{filename} 已保存到 {save_path}{filename}")


# 示例主流程
def extract_and_save_all(text, save_path='./C51_codes/'):
    structural_code = extract_structural_code(text)
    modular_code = extract_modular_code(text)
    procedural_code = extract_procedural_code(text)
    if structural_code:
        save_code(structural_code, "structural.c", save_path)
    else:
        print("未找到结构化编程风格代码")
    if modular_code:
        save_code(modular_code, "modular.c", save_path)
    else:
        print("未找到模块化编程风格代码")
    if procedural_code:
        save_code(procedural_code, "procedural.c", save_path)
    else:
        print("未找到面向过程编程风格代码")


#####参考代码生成
def reference_code_ge(path2='./土壤湿度自动浇花.txt', model_name='gpt-4.1', compile_path='./C51_codes/',
                      save_path='./C52_codes/', jason_path='./', topic_id=''):
    # autotest = autotest()
    send_to_topic(topic_id, "process", "Start generating reference code...", 2)
    messages2 = [
        {"role": "system",
         "content": "You will serve as an experienced embedded system design engineer. "
                    "I will provide you with a requirements document and corresponding code. "
                    "Please analyze the relationship between the requirements document and the reference code, "
                    "then implement three versions of the code.These codes need to maintain the same functional logic as the original code, "
                    "but should be written using the following three programming styles respectively:"
                    "\n1.Structured programming style"
                    "\n2.Modular programming style"
                    "\n3.Procedural programming style.The output must be complete code, requiring C language code."
                    "\nOutput requirements "
                    "1.Output requirement "
                    "1: All code for each style should not be separated into files, but should be implemented in a single file."
                    "\n2.Output requirements in the following format:"
                    "\n###Structured programming style reference###```Your first code```"
                    "\n###Modular programming style reference###```Your second code```"
                    "\n###Procedural programming style reference###```Your third code```。"
                    "\nDo not output any other unnecessary thing"}
    ]
    ##参考代码生成
    with open(path2, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']

    print(f"检测到的编码: {encoding}, 置信度: {confidence}")

    # 使用检测到的编码读取文件
    with open(path2, 'r',encoding=encoding) as file:
        content2 = file.read()
    userinput2 = '参考代码：\n---\n' + content2 + '\n---'
    messages2.append({"role": "user", "content": userinput2})
    # model_name='gpt-4.1-nano-2025-04-14'########################################
    os.environ["http_proxy"] = "http://127.0.0.1:7890"  # 指定代理，解决连接问题
    os.environ["https_proxy"] = "http://127.0.0.1:7890"  # 指定代理，解决连接问题
    client = OpenAI(api_key="your api")
    client.base_url = "https://ai-yyds.com/v1"
    completion = client.chat.completions.create(model=model_name, messages=messages2)
    print("生成完毕,已经访问大模型")
    text1 = completion.choices[0].message.content
    messages2.append({"role": "assistant", "content": text1})  # 记录回复

    with open(jason_path + "chat_history_reference.json", "w", encoding="utf-8") as f:
        json.dump(messages2, f, ensure_ascii=False, indent=2)
    extract_and_save_all(text1, compile_path)  ####保存####################################
    ####结构化

    for i1 in range(3):
        if i1 != 0:
            with open(jason_path + "chat_history_reference1.json", "r", encoding="utf-8") as f:
                loaded_messages1 = json.load(f)
        else:
            with open(jason_path + "chat_history_reference.json", "r", encoding="utf-8") as f:
                loaded_messages1 = json.load(f)
        # autotest.start('./C51_codes/'+file.name,'./C52_codes/')
        tag, err_inf, _ = autotest.start(compile_path + 'structural.c', compile_path, save_path)
        if tag == True:
            loaded_messages1.append({"role": "user", "content": 'structural Compilation successful！'})
            with open(jason_path + "chat_history_reference1.json", "w", encoding="utf-8") as f:
                json.dump(loaded_messages1, f, ensure_ascii=False, indent=2)
            print('structural.c编译通过！')
            break
        else:
            new_user_input = "There are issues with the structured programming style reference code. Please modify the problems based on C51 compiler feedback. Output requirements:###structured programming style reference###```Your modified code, including all specific functional implementations```.\nCompiler feedback:" + err_inf + "\n"
            print('结构化编程风格参考代码存在问题')
            loaded_messages1.append({"role": "user", "content": new_user_input})

            completion = client.chat.completions.create(model=model_name, messages=loaded_messages1)
            new_reply = completion.choices[0].message.content
            loaded_messages1.append({"role": "assistant", "content": new_reply})  # 记录回复

            with open(jason_path + "chat_history_reference1.json", "w", encoding="utf-8") as f:
                json.dump(loaded_messages1, f, ensure_ascii=False, indent=2)
            structural_code = extract_structural_code(new_reply)
            save_code(structural_code, "structural.c", compile_path)

    ####模块化
    for i2 in range(3):
        if i2 != 0:
            with open(jason_path + "chat_history_reference2.json", "r", encoding="utf-8") as f:
                loaded_messages2 = json.load(f)
        else:
            with open(jason_path + "chat_history_reference.json", "r", encoding="utf-8") as f:
                loaded_messages2 = json.load(f)

        # autotest.start('./C51_codes/'+file.name,'./C52_codes/')
        tag, err_inf, _ = autotest.start(compile_path + 'modular.c', compile_path, save_path)
        if tag == True:
            print('modular.c编译通过！')
            loaded_messages2.append({"role": "user", "content": 'modular Compilation successful！'})
            with open(jason_path + "chat_history_reference2.json", "w", encoding="utf-8") as f:
                json.dump(loaded_messages2, f, ensure_ascii=False, indent=2)
            break
        else:
            new_user_input = "There are issues with the modular programming style reference code. Please modify the problems based on C51 compiler feedback. Output requirements:###modular programming style reference###```Your modified code, including all specific functional implementations```.\nCompiler feedback:" + err_inf + "\n"
            print('模块化编程风格参考代码存在问题')
            loaded_messages2.append({"role": "user", "content": new_user_input})

            completion = client.chat.completions.create(model=model_name, messages=loaded_messages2)
            new_reply = completion.choices[0].message.content
            loaded_messages2.append({"role": "assistant", "content": new_reply})  # 记录回复
            with open(jason_path + "chat_history_reference2.json", "w", encoding="utf-8") as f:
                json.dump(loaded_messages2, f, ensure_ascii=False, indent=2)
            structural_code = extract_modular_code(new_reply)
            save_code(structural_code, "modular.c", compile_path)
    send_to_topic(topic_id, "finish", "Step three completed, reference code in three styles has been generated...", 2)
    send_to_topic(topic_id, "process", "Starting to compile feedback", 3)
    ####面向过程
    for i3 in range(5):
        if i3 != 0:
            with open(jason_path + "chat_history_reference3.json", "r", encoding="utf-8") as f:
                loaded_messages3 = json.load(f)
        else:
            with open(jason_path + "chat_history_reference.json", "r", encoding="utf-8") as f:
                loaded_messages3 = json.load(f)
        # autotest.start('./C51_codes/'+file.name,'./C52_codes/')
        tag, err_inf, _ = autotest.start(compile_path + 'procedural.c', compile_path, save_path)
        if tag == True:
            print('procedural.c编译通过！')
            loaded_messages3.append({"role": "user", "content": 'procedural Compilation successful！'})
            with open(jason_path + "chat_history_reference3.json", "w", encoding="utf-8") as f:
                json.dump(loaded_messages3, f, ensure_ascii=False, indent=2)
            break
        else:
            new_user_input = ("There are issues with the procedural programming style reference code. Please modify the problems based on C51 compiler feedback. "
                              "Output requirements:###Procedural programming style reference###```Your modified code, including all specific functional implementations```."
                              "\nCompiler feedback:") + err_inf + "\n"
            print('面向过程编程风格参考代码存在问题')
            loaded_messages3.append({"role": "user", "content": new_user_input})
            completion = client.chat.completions.create(model=model_name, messages=loaded_messages3)
            new_reply = completion.choices[0].message.content
            loaded_messages3.append({"role": "assistant", "content": new_reply})  # 记录回复
            with open(jason_path + "chat_history_reference3.json", "w", encoding="utf-8") as f:
                json.dump(loaded_messages3, f, ensure_ascii=False, indent=2)
            structural_code = extract_procedural_code(new_reply)
            save_code(structural_code, "procedural.c", compile_path)
    send_to_topic(topic_id, "finish", "Step four completed, reference code generation finished...", 3)
    return loaded_messages1


##############提供修正建议
def suggestion_fix_code(
        path4,
        path1='./C51_codes/modular.c',
        path2='./C51_codes/structural.c',
        path3='./C51_codes/procedural.c',
        model_name='claude-sonnet-4-20250514',
        json_path='./'
):
    ##参考代码生成

    # path1 = './C51_codes/modular.c'
    # path2 = './C51_codes/structural.c'
    # path3 = './C51_codes/procedural.c'
    # path4 = './土壤湿度自动浇花.txt'
    # 加载历史对话，如果不存在则新建
    if os.path.exists(json_path + 'chat_history_fix.json'):
        with open(json_path + 'chat_history_fix.json', "r", encoding="utf-8") as f:
            messages2 = json.load(f)
    else:
        messages2 = [
            {
                "role": "system",
                "content": (
                    "You will play the role of an experienced embedded system design engineer guiding the modification of erroneous code and completion of requirements.\n"
                    "I will provide you with the project's requirements document and three correct code references. After that, I will provide you with the erroneous code:\n"
                    "If the code provided to you is erroneous, please provide modification ideas for the erroneous code based on the correct code to make it align with the correct code.\n"
                    "Output requirements: (... represents the content you need to fill in)\n"
                    "Code modification approach:'''...'''\n"
                    "Solution:'''...'''"
                )
            }
        ]

    # 读取参考代码和错误代码
    with open(path1, 'r', encoding='utf-8') as file:
        content1 = file.read()
    with open(path2, 'r', encoding='utf-8') as file:
        content2 = file.read()
    with open(path3, 'r', encoding='utf-8') as file:
        content3 = file.read()
    with open(path4, 'r', encoding='utf-8') as file:
        content4 = file.read()

    # 构建新的用户输入
    userinput2 = (
            '参考代码1：\n---\n' + content1 + '\n---\n'
                                             '参考代码2：\n---\n' + content2 + '\n---\n'
                                                                              '参考代码3：\n---\n' + content3 + '\n---\n'
                                                                                                               '错误代码：\n---\n' + content4 + '\n---'
    )
    messages2.append({"role": "user", "content": userinput2})

    # 设置代理
    os.environ["http_proxy"] = "http://127.0.0.1:7890"
    os.environ["https_proxy"] = "http://127.0.0.1:7890"

    # 调用OpenAI接口
    client = OpenAI(api_key="your api")
    client.base_url = "https://ai-yyds.com/v1"
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages2
    )
    text1 = completion.choices[0].message.content

    # 追加assistant回复并保存历史
    messages2.append({"role": "assistant", "content": text1})
    with open(json_path + 'chat_history_fix.json', "w", encoding="utf-8") as f:
        json.dump(messages2, f, ensure_ascii=False, indent=2)

    return text1


################################代码修正

#########################################修正
# %%
def test1_fix_with_compile_feedback(
        text_change,
        model_name='claude-sonnet-4-20250514',
        max_retry=3,
        compile_path='./C51_codes/',
        save_path='./C52_codes/',
        jason_path='./',
        topic_id='',
):
    send_to_topic(topic_id, "process", "Correcting code based on revision suggestions...", 5)
    text2_tag = 0
    import json, os, re
    from openai import OpenAI
    with open(jason_path + "chat_history.json", "r", encoding="utf-8") as f:
        messages1 = json.load(f)
    print("已加载的对话历史：")
    os.environ["http_proxy"] = "http://127.0.0.1:7890"
    os.environ["https_proxy"] = "http://127.0.0.1:7890"
    userinput1 = "The code has issues, please modify the code according to the correction suggestions, only output the complete modified code is required.\nOutput format:```codeYour modified code, including all functional implementations```\n" + 'Modification suggestions:\n---\n' + text_change + '\n---'

    # userinput1 = '需求文档：\n---\n' + content1 + '\n---'
    messages1.append({"role": "user", "content": userinput1})  # 添加新增内容

    client = OpenAI(api_key="your api")
    client.base_url = "https://ai-yyds.com/v1"

    # final_messages = None  # 用于保存最终对话
    # 1. 生成代码
    completion = client.chat.completions.create(model=model_name, messages=messages1)
    text1 = completion.choices[0].message.content
    # messages1.append({"role": "assistant", "content": text1})
    # 2. 提取代码
    pattern = r"```(?:code\w*|c\w*)\n(.*?)```"
    code_blocks = re.findall(pattern, text1, re.DOTALL)

    messages2 = messages1.copy()
    if code_blocks:
        os.makedirs(compile_path, exist_ok=True)  # 确保目录存在
        with open(compile_path + "output.c", 'w', encoding='utf-8') as f:
            f.write(code_blocks[0])
        print('代码已保存为' + compile_path + 'output.c')
    ########保存初始生成相关信息（不保存代码）
    else:
        print('未找到代码块')
        return text1
    with open(jason_path + "chat_history.json", "w", encoding="utf-8") as f:
        json.dump(messages1, f, ensure_ascii=False, indent=2)
    send_to_topic(topic_id, "finish", "Step six, code correction completed...", 5)
    # 3. 编译并获取反馈
    send_to_topic(topic_id, "process", "Fixing code issues based on compilation feedback...", 6)
    for i in range(max_retry):
        # 3. 编译并获取反馈
        tag, err_inf, _ = autotest.start(compile_path + 'output.c', compile_path, save_path)
        if tag:
            print("编译通过！")
            break



        else:
            print("编译错误，准备反馈给模型修正...")
            new_user_input = (
                    "The C language code you just generated failed to compile in Keil uVision5，Please correct your code based on the compiler feedback information below, output requirements:"
                    "###Corrected C Language Code###\n```code your code```。\nCompiler feedback:" + err_inf + "\n"
            )
            messages2.append({"role": "user", "content": new_user_input})
            completion = client.chat.completions.create(model=model_name, messages=messages2)
            text2 = completion.choices[0].message.content
            messages2.append({"role": "assistant", "content": text2})
            text2_tag = 1
            # 2. 提取代码
            #####匹配提取代码
            pattern = r"```(?:code\w*|c\w*)\n(.*?)```"
            code_blocks1 = re.findall(pattern, text1, re.DOTALL)
            if code_blocks1:
                os.makedirs(compile_path, exist_ok=True)  # 确保目录存在

                with open(compile_path + "output.c", 'w', encoding='utf-8') as f:
                    f.write(code_blocks1[0])
                print('修正代码已保存为' + compile_path + 'output.c')
            else:
                print('未找到代码块')
    # 只保存最后一次生成正确代码的对话内容
    if text2_tag == 0:
        messages2.append({"role": "user", "content": 'Compilation Successful！'})
        with open(jason_path + "compile1_history.json", "w", encoding="utf-8") as f:
            json.dump(messages2, f, ensure_ascii=False, indent=2)


    if text2_tag == 1:
        messages1.append({"role": "assistant", "content": text2})
        with open(jason_path + "chat_history.json", "w", encoding="utf-8") as f:
            json.dump(messages1, f, ensure_ascii=False, indent=2)

    else:
        messages1.append({"role": "assistant", "content": text1})
        print("没有生成通过编译的代码，保存原本对话内容。")
        with open(jason_path + "chat_history.json", "w", encoding="utf-8") as f:
            json.dump(messages1, f, ensure_ascii=False, indent=2)
    send_to_topic(topic_id, "finish", "Step seven, all steps completed...", 6)
    return text1


# %%
def test2_ask_question(jason_path='./', model_name='claude-sonnet-4-20250514', chat_content=''):
    import json
    import os
    import re
    if os.path.exists(jason_path + 'chat_history_reply.json'):
        with open(jason_path + 'chat_history_fix.json', "r", encoding="utf-8") as f:
            loaded_messages = json.load(f)
    elif os.path.exists(jason_path + 'chat_history.json'):
        with open(jason_path + "chat_history.json", "r", encoding="utf-8") as f:
            loaded_messages = json.load(f)
    else:
        loaded_messages = [
            {
                "role": "system",
                "content": (
                    "你将扮演一名智能助手回答用户的各种问题。"
                )
            }
        ]
    print("已加载的对话历史：")
    # for msg in loaded_messages:
    # print(f"{msg['role']}: {msg['content']}")
    # 6. 继续对话
    # new_user_input = input("请输入你的问题: ")
    loaded_messages.append({"role": "user", "content": chat_content})
    # 调用模型回答问题
    client = OpenAI(api_key="your api")
    # suggestion = ""
    client.base_url = "https://ai-yyds.com/v1"
    completion = client.chat.completions.create(model=model_name, messages=loaded_messages)
    new_reply = completion.choices[0].message.content
    loaded_messages.append({"role": "assistant", "content": new_reply})
    with open("chat_history_reply.json", "w", encoding="utf-8") as f:
        json.dump(loaded_messages, f, ensure_ascii=False, indent=2)
    return new_reply
