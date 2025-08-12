# 风险场模型 Conda 环境配置指南

## 创建独立conda环境的好处：
- 避免包版本冲突
- 保持项目依赖干净
- 便于环境管理和分享
- 不影响其他项目

## 环境设置步骤：

### 1. 创建新环境
```bash
# 创建专用环境（Python 3.8-3.11都可以）
conda create -n risk_field python=3.9 -y

# 激活环境
conda activate risk_field
```

### 2. 安装核心依赖
```bash
# 方式1：使用conda安装（推荐，速度快）
conda install numpy matplotlib scipy pandas -y

# 方式2：或使用pip安装
pip install numpy matplotlib scipy pandas
```

### 3. 验证安装
```bash
python -c "import numpy, matplotlib, scipy, pandas; print('✅ 所有依赖安装成功!')"
```

### 4. 保存环境配置
```bash
# 导出环境配置（便于分享）
conda env export > environment.yml

# 或者生成requirements.txt
pip freeze > requirements.txt
```

### 5. 日常使用
```bash
# 每次使用前激活环境
conda activate risk_field

# 运行代码
python complete_reproduction.py

# 使用完毕后可以退出
conda deactivate
```

### 6. 环境管理
```bash
# 查看所有环境
conda env list

# 删除环境（如果不需要了）
conda env remove -n risk_field

# 从配置文件恢复环境
conda env create -f environment.yml
```

## MacBook Air 优化建议：
- 使用conda-forge频道：`conda install -c conda-forge numpy matplotlib`
- 考虑使用mamba加速：`conda install mamba -y`，然后用`mamba`替代`conda`
- 设置合理的网格精度以平衡速度和精度
