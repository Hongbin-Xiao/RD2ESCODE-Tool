# RD2ESCODE: Automated Transformation of Requirements Documents into Embedded System Code Tool

[![Demo Video](https://img.shields.io/badge/Demo-Video-red)](https://youtu.be/5dz5B-s-TAU)
[![License](https://img.shields.io/badge/License-Open%20Source-green)]()

## 🚀 Overview

RD2ESCODE is an innovative LLM-based tool that automatically transforms requirements documents into high-quality embedded system code. By leveraging Large Language Models (specifically Claude 4 Sonnet) and a multi-agent collaborative framework, this tool bridges the gap between natural language requirements and executable embedded code, significantly accelerating the development process.

## 📁 Project Structure

```
RD2ESCODE-Tool/
├── aiDjangoProject/          # 工具后端 (Tool Backend) 
├── project/                  # 工具前端 (Tool Frontend)
└── RD2ESCODE-EVALUATION/     # 工具评估 (Tool Evaluation)
```
## ✨ Key Features

### 🧠 Natural Language Requirement Comprehension
- Direct conversion of natural language requirements into executable code
- Multi-agent framework for accurate interpretation of complex requirements
- Flexible adaptation to rapid changes in agile development environments

### 🔧 Intelligent Reference-Based Code Generation
- Chain-of-thought reasoning combined with multi-agent collaboration
- Intelligent code generation and optimization using historical and reference examples
- Closed-loop verification system ensuring high code quality

### 📚 Interactive Code Explanation and Knowledge Transfer
- Interactive consultation mechanism for detailed code explanations
- Bridges the interpretability gap of traditional tools
- Supports team learning and knowledge sharing

## 🏗️ Architecture

RD2ESCODE employs a sophisticated multi-agent collaborative framework consisting of four specialized agents:

1. **Reference Code Generation Agent**: Learns implementation patterns across different programming paradigms
2. **Requirement Code Generation Agent**: Produces embedded code tailored to system specifications
3. **Compilation Feedback Agent**: Automatically identifies syntax errors and type mismatches
4. **Code Optimization Suggestion Agent**: Analyzes issues and provides targeted remediation strategies
<img width="1525" height="842" alt="1" src="https://github.com/user-attachments/assets/e6d8a375-f47c-4991-ba6f-dca9bdab986f" />
<img width="2046" height="735" alt="2" src="https://github.com/user-attachments/assets/3950c2b7-d317-4751-a393-694064a57641" />




## 🔄 Workflow

### Step 1: Initial Code Generation and Compilation Optimization
- User provides reference code and requirement documents
- Initial code generation based on requirements
- Iterative compilation feedback loop until successful compilation

### Step 2: Multi-Style Reference Code Generation
- Generation of reference code in three programming styles:
- Structured Programming
- Modular Programming
- Procedural Programming
- Compilation optimization for each style

### Step 3: Intelligent Code Correction and Final Optimization
- Code quality analysis using multi-style reference codes
- Implementation of correction recommendations
- Final compilation optimization loop

## 📊 Performance Metrics

### Development Time Efficiency
- **83-88% improvement** over manual development
- **62-74% improvement** over reference code-based development
- Reduces development time from 22-38 hours to 3-5 hours

### Code Quality Metrics
- **Average Test Case Pass Rate (ATCPR)**: 0.81
- **Pass@1 Success Rate**: 0.71
- Competitive performance compared to graduate-level developers

## 🛠️ Tool Comparison

| Feature | STM32CubeMX | MCUXpresso | Simulink | RD2ESCODE |
|---------|-------------|------------|----------|-----------|
| Code Explanation | ❌ | ❌ | ❌ | ✅ |
| Natural Language Requirements | ❌ | ❌ | ❌ | ✅ |
| Automatic Code Generation | ✅ | ✅ | ✅ | ✅ |
| Simulation Testing | ✅ | ✅ | ✅ | ✅ |
| Configuration Type | Interface-only | Interface-only | Model-driven | Natural Language |




### Usage
1. Prepare your requirements document in natural language
2. Provide reference code (if available)
3. Run RD2ESCODE tool through the web interface
4. Review and test the generated embedded code

## 📝 Case Study: PM2.5 Monitoring System

The tool's effectiveness has been validated through the development of a PM2.5 Monitoring System, demonstrating:
- Successful code generation across multiple programming paradigms
- High compilation success rate
- Significant reduction in development time

## 🎯 Use Cases

- **Agile Development**: Rapid prototyping and iteration
- **Educational Purposes**: Learning embedded systems development
- **Industrial Applications**: Accelerating embedded system projects
- **Code Migration**: Adapting existing code to new requirements

## 🔬 Research Background

This tool addresses key challenges in embedded systems development:
- Deep hardware knowledge requirements
- Advanced programming skills needed
- Time-consuming manual code adaptation
- Difficulty in leveraging existing codebases

## 🤝 Contributing

We welcome contributions to improve RD2ESCODE! Please see our contribution guidelines in the repository.

## 📄 Citation

If you use RD2ESCODE in your research, please cite:

```bibtex
@article{tan2024rd2escode,
title={RD2ESCODE: Automated Transformation of Requirements Documents into Embedded System Code Tool},
author={Tan, Shuru and Xiao, Hongbin and Li, Zhi and Xie, Xiaolan and Wu, Tianhao and Tang, Fei},
journal={ASE Tool Demo},
year={2024}
}
```

## 📞 Contact

- **Email**: zhili@gxnu.edu.cn, xie_xiao_lan@foxmail.com
- **GitHub**: [RD2ESCODE Repository](https://github.com/Hongbin-Xiao/RD2ESCODE)
- **Demo Video**: [YouTube](https://youtu.be/5dz5B-s-TAU)

## 🏛️ Affiliations

- Key Lab of Education Blockchain and Intelligent Technology, Ministry of Education, Guangxi Normal University
- Guilin University of Technology
- Huawei Technologies Co., Ltd

## 📜 License

This project is open-sourced to provide an efficient, intelligent solution for the embedded development community.

---

*RD2ESCODE: Transforming the future of embedded systems development through intelligent automation.*
