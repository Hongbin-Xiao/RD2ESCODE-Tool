import subprocess
import re
import shutil
import os
import re
#from i8051emu import simulator


class autotest():
    def __init__(self):
        self.status = True
        self.errorInfo = ''
        self.errorStap = ''
        self.compilingErrors = 0
        self.compilingWarnings = 0
        self.empty_fun_name = []
        self.staticCheckErrors = 0
        self.staticCheckWarnings = 0
        self.staticCheckStyles = 0
        self.staticCheckPerformances = 0
        self.staticCheckPortabilitys = 0
        self.staticCheckInformations = 0

    def read_c_code(self, file_path):
        """读取C语言代码文件"""
        with open(file_path, 'r',encoding='utf-8') as file: #encoding='utf-8'
            return file.read()

    def check_empty_function_implementation(self, file_path, displayEmptyFunction=False):
        """检查函数是否只有声明和花括号，没有实现的代码"""
        code = self.read_c_code(file_path)
        # 匹配函数声明（以;结尾）和函数实现（以{开头）
        func_decl_pattern = r'^\s*(int|void|char|float|double|[\w*]+)\s+([\w]+)\s*\([^)]*\)\s*;\s*$'
        func_impl_pattern = r'^\s*(int|void|char|float|double|[\w*]+)\s+([\w]+)\s*\([^)]*\)\s*\{'

        # 查找所有函数声明
        func_decls = re.findall(func_decl_pattern, code, re.MULTILINE)
        # 查找所有函数实现
        func_impls = re.findall(func_impl_pattern, code, re.MULTILINE)

        # 创建一个集合存储所有实现的函数名
        implemented_funcs = {impl[1] for impl in func_impls}

        # 检查每个函数声明是否有对应的实现
        for decl in func_decls:
            func_name = decl[1]  # 函数名
            if func_name not in implemented_funcs:
                print(f"Function declared but not implemented: {func_name}")

        empty_fun_count = 0
        # 检查实现是否为空
        annotation_line = re.compile(r'^\s*//')  # 注释行正则表达式
        for impl in func_impls:
            UNannotation_line_count = 0
            func_name = impl[1]  # 函数名
            # 查找函数体
            func_body_pattern = rf'^\s*(int|void|char|float|double|[\w*]+)\s+{func_name}\s*\([^)]*\)\s*\{{(.*?)\}}'
            body_match = re.search(func_body_pattern, code, re.DOTALL | re.MULTILINE)
            if body_match:
                func_body = body_match.group(2).strip()  # 获取函数体内容
                if func_body:
                    func_body = func_body.split('\n')
                    for func_body_line in func_body:
                        if not annotation_line.match(func_body_line):
                            UNannotation_line_count = UNannotation_line_count + 1
            if UNannotation_line_count == 0:
                empty_fun_count = empty_fun_count + 1
                self.empty_fun_name.append(func_name)

        if empty_fun_count != 0:
            if displayEmptyFunction:
                print(self.empty_fun_name)
                self.errorInfo = "There are some functions that are only defined but not implemented."+','.join(self.empty_fun_name)
                self.errorStap = "check empty function implementation is error."
            # print("妈的摆烂！")
            self.status = False
        else:
            # print("还行没摆！")
            self.status = True

    def compiling_file(self, path, displayCount=False, diaplayDetailedInformation=False):

        # 定义要执行的SDCC编译命令
        # command = "sdcc C51_codes/SDCCMain.c "
        # E:\Keil_v5\C51\BIN\C51 .\C51_codes\mian.c
        cmdPath = 'D:\Keil_v5\C51\BIN\\'
        command = [cmdPath + "C51 " + path, cmdPath + "BL51 " + path.rsplit('.', 1)[0] + '.obj RAMSIZE(256)',
                   cmdPath + "OH51 " + path.rsplit('.', 1)[0]]
        for i in range(3):
            if self.status == False:
                break
            try:
                # 执行命令并捕获输出和错误
                # print(command[i])
                result = subprocess.run(command[i], shell=True, check=False, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True)

                # # 检查返回码以确定是否编译成功
                # if result.returncode != 0:
                #     print("Compilation failed with return code", result.returncode)
                #     status = False

                # 将错误信息和输出信息打印出来
                if diaplayDetailedInformation:
                    print("STDOUT:", result.stdout)
                    print("STDERR:", result.stderr)

                # 使用正则表达式查找错误和警告
                errors = len(re.findall(r'ERROR', result.stdout))
                warnings = len(re.findall(r'WARNING', result.stdout))
                if errors > 0:
                    self.compilingErrors = errors - 1
                if warnings > 0:
                    self.compilingWarnings = warnings - 1

                # 输出错误和警告的数量
                if displayCount:
                    print(f"Number of errors: {self.compilingErrors}")
                    print(f"Number of warnings: {self.compilingWarnings}")

                # 检查是否存在警告
                if self.compilingWarnings > 0:
                    print("There are warnings in the compilation process.")

                if self.compilingErrors > 0:
                    print("Compilation failed with return code", result.returncode)
                    self.errorInfo = result.stdout
                    self.errorStap = f'compiling file error, command is {command[i]}'
                    self.status = False

            except subprocess.SubprocessError as e:
                print("An error occurred while running the subprocess:", str(e))

    # def compiling_file(path, displayCount=False, diaplayDetailedInformation=False):
    #     errors = 0
    #     warnings = 0
    #     status = True
    #
    #     # 定义要执行的SDCC编译命令
    #     # command = "sdcc -o output_directory/SDCCMain.ihx -c C51_codes/SDCCMain.c "
    #     command = "sdcc " + path
    #
    #     try:
    #         # 执行命令并捕获输出和错误
    #         result = subprocess.run(command, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    #                                 text=True)
    #
    #         # 检查返回码以确定是否编译成功
    #         if result.returncode != 0:
    #             print("Compilation failed with return code", result.returncode)
    #             status = False
    #
    #         # 将错误信息和输出信息打印出来
    #         if diaplayDetailedInformation:
    #             print("STDOUT:", result.stdout)
    #             print("STDERR:", result.stderr)
    #
    #         # 使用正则表达式查找错误和警告
    #         errors = len(re.findall(r'error', result.stderr))
    #         warnings = len(re.findall(r'warning', result.stderr))
    #
    #         # 输出错误和警告的数量
    #         if displayCount:
    #             print(f"Number of errors: {errors}")
    #             print(f"Number of warnings: {warnings}")
    #
    #         # 检查是否存在警告
    #         if warnings > 0:
    #             print("There are warnings in the compilation process.")
    #
    #     except subprocess.SubprocessError as e:
    #         print("An error occurred while running the subprocess:", str(e))
    #
    #     return status, [errors, warnings]

    def check_file(self, path, displayCount=False, diaplayDetailedInformation=False):

        # cppcheck命令
        # command = "cppcheck --enable=all --platform=win64 ./C51_codes/SDCCMain.c "
        command = "cppcheck --enable=all --platform=win64 " + path
        try:
            # 执行命令并捕获输出和错误
            # result = subprocess.run(['cppcheck', '--enable=all', '--platform=win64', 'C51_codes/SDCCMain.c'],
            #                         capture_output=True, text=True, check=True)
            result = subprocess.run(command, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)

            # 将错误信息和输出信息打印出来
            if diaplayDetailedInformation:
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)

            # 使用正则表达式查找错误和警告
            self.staticCheckErrors = len(re.findall(r'error', result.stderr))
            self.staticCheckWarnings = len(re.findall(r'warning', result.stderr))
            self.staticCheckStyles = len(re.findall(r'style', result.stderr))
            self.staticCheckPerformances = len(re.findall(r'performance', result.stderr))
            self.staticCheckPortabilitys = len(re.findall(r'portability', result.stderr))
            self.staticCheckInformations = len(re.findall(r'information', result.stderr))

            if self.staticCheckErrors > 0:
                print("static check failed with info", result.stderr)
                self.errorInfo = result.stderr
                self.errorStap = f'cppcheck is fail, command is {command}'
                self.status = False
            # 输出错误和警告的数量
            if displayCount:
                print(f"Number of errors: {self.staticCheckErrors}")
                print(f"Number of warnings: {self.staticCheckWarnings}")
                print(f"Number of styles: {self.staticCheckStyles}")
                print(f"Number of performances: {self.staticCheckPerformances}")
                print(f"Number of portabilitys: {self.staticCheckPortabilitys}")
                print(f"Number of informations: {self.staticCheckInformations}")

            # 检查是否存在警告
            if self.staticCheckWarnings > 0:
                print("There are warnings in the compilation process.")

        except subprocess.SubprocessError as e:
            print("An error occurred while running the subprocess:", str(e))

    def start(self, fromFile,savePath='./',toPath1 = "./C51_codes/", saveErrorInfo=False, displayCount=False, diaplayDetailedInformation=False,
              displayEmptyFunction=False):
        # fromFile c文件路径，savePath=生成hex文件路径与c路径一致，toPath1 = 杂七杂八生成路径
        # 构建完整的新文件路径
        name = "TEST" + os.path.basename(fromFile)
        #toPath = os.path.dirname(fromPath) + "/" + name
        #toPath1 = "./C51_codes/"
        toPath = toPath1 + name
        shutil.copy(fromFile, toPath)

        self.check_empty_function_implementation(toPath, displayEmptyFunction)  # 检查是否存在空函数，只定义不实现,返回检查结果和具体的空函数
        if self.status == False:
            return self.status
        """
        error：表示代码中存在严重的错误，必须修复才能使代码正常工作。
        warning：表示代码中存在潜在的问题，可能会导致程序出现错误或异常行为。
        style：表示代码中存在一些不规范的写法或风格，不影响程序的正确性，但可能会降低代码的可读性和可维护性。
        performance：表示代码中存在一些性能问题，可能会导致程序运行缓慢或消耗过多的资源。
        portability：表示代码中存在一些与平台相关的问题，可能会导致程序在不同的操作系统或编译器上出现不同的行为。
        information：表示代码中存在一些有用的信息，例如未使用的变量或函数等。
        """
        self.check_file(toPath, displayCount, diaplayDetailedInformation)
        if self.status == False:
            return self.status,self.errorInfo,self.errorStap

        self.compiling_file(toPath, displayCount, diaplayDetailedInformation)
        if self.status == False:
            return self.status,self.errorInfo,self.errorStap
        name=name.split('.')[0]+".hex"
        savePath = savePath + name
        name= toPath1+ name

        shutil.copy(name, savePath)
        return self.status,self.errorInfo,self.errorStap



#autotest = autotest()
#autotest.start('./C51_codes/123.c','./C52_codes/')
