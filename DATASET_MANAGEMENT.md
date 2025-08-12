# 数据集管理最佳实践指南

## 📁 推荐的目录结构

```
your_project_root/
├── python_reproduction/           # 代码仓库（上传到GitHub）
│   ├── risk_field_model.py
│   ├── highd_processor.py
│   ├── requirements.txt
│   └── ...
├── HighDdata/                     # highD数据集（不上传）
│   ├── 01_tracks.csv
│   ├── 01_tracksMeta.csv
│   └── ...
├── rounDdata/                     # rounD数据集（预留，不上传）
│   └── ...
└── outputs/                       # 输出结果（不上传）
    ├── risk_fields/
    ├── scenarios/
    └── reports/
```

## ✅ 为什么这样组织？

### 1. **代码与数据分离**
- ✅ 代码仓库保持轻量级
- ✅ 数据集不会意外上传到版本控制
- ✅ 不同用户可以使用自己的数据集路径

### 2. **版权合规**
- ✅ highD/rounD数据集需要单独申请许可
- ✅ 避免版权问题
- ✅ 符合学术数据使用规范

### 3. **性能优化**
- ✅ Git仓库克隆速度快
- ✅ 避免大文件影响版本控制性能
- ✅ 本地开发环境清洁

## 🔒 .gitignore 配置

以下文件和目录已自动忽略：

```gitignore
# 数据集目录
HighDdata/
rounDdata/
data/
datasets/

# 输出文件
outputs/
results/
*.png
*.jpg
reproduction_report.txt

# 数据文件
*.csv
*.mat
*.h5
*.hdf5
```

## 📦 数据集获取指南

### highD数据集
1. **官方网站**: https://www.highd-dataset.com/
2. **申请流程**: 
   - 填写申请表格
   - 说明研究用途
   - 等待审核批准
3. **下载后放置**: 解压到 `../HighDdata/` 目录

### rounD数据集（未来支持）
1. **官方网站**: https://www.round-dataset.com/
2. **预留目录**: `../rounDdata/`

## 🛠️ 开发工作流

### 本地开发
```bash
# 1. 克隆代码仓库
git clone https://github.com/your-username/risk-field-model-python.git
cd risk-field-model-python

# 2. 单独获取和放置数据集
# [按照上述指南获取highD数据集]
# 确保目录结构: ../HighDdata/

# 3. 安装依赖
pip install -r requirements.txt

# 4. 测试数据集集成
python test_highd_integration.py
```

### 团队协作
```bash
# 代码同步
git pull origin main

# 数据集各自管理（不共享）
# 每个开发者独立获取和配置数据集

# 结果共享（可选）
# 生成的场景数据可以通过其他方式共享
```

## 📊 数据处理最佳实践

### 1. **分阶段处理**
```python
# 先小样本测试
processor = HighDProcessor()
vehicles = processor.extract_scenario_by_time(tracks_df, meta_df, 1000, 50)

# 再大批量处理  
scenarios = processor.find_overtaking_scenarios(tracks_df, meta_df)
```

### 2. **结果缓存**
```python
# 处理耗时的提取结果应该保存
processor.save_scenarios(scenarios, "extracted_scenarios.json")

# 避免重复处理
if os.path.exists("extracted_scenarios.json"):
    scenarios = processor.load_scenarios("extracted_scenarios.json")
```

### 3. **内存管理**
```python
# 大数据集分批处理
for recording_id in processor.list_available_recordings():
    tracks_df, meta_df = processor.load_recording(recording_id)
    # 处理完释放内存
    del tracks_df, meta_df
```

## 🚀 部署和分发

### 开源发布
- ✅ **包含**: 所有Python代码
- ✅ **包含**: 文档和使用指南  
- ✅ **包含**: 测试脚本和示例
- ❌ **不包含**: 任何数据集文件
- ❌ **不包含**: 生成的大文件

### 使用说明
```markdown
## 数据准备

1. 申请并下载highD数据集
2. 将数据集放置在代码目录的父级: `../HighDdata/`
3. 运行测试: `python test_highd_integration.py`
```

### Docker化（可选）
```dockerfile
# Dockerfile示例
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY *.py .

# 数据集通过volume挂载
VOLUME ["/data"]
```

## 🔍 故障排除

### 常见问题

**Q: 找不到数据集目录？**
```
FileNotFoundError: ../HighDdata/ not found
```
**A**: 确保HighDdata文件夹与python_reproduction文件夹平行放置

**Q: CSV文件格式错误？**
```
pandas.errors.EmptyDataError
```
**A**: 确保下载的是完整的highD数据集，包含所有CSV文件

**Q: 内存不足？**
```
MemoryError: Unable to allocate array
```
**A**: 
- 减少处理的时间窗口
- 使用分批处理
- 增加系统内存

### 验证数据集完整性
```python
# 验证脚本示例
def validate_dataset():
    processor = HighDProcessor()
    
    if not processor.data_available:
        print("❌ 数据集不可用")
        return False
    
    recordings = processor.list_available_recordings()
    print(f"✅ 找到 {len(recordings)} 个录制文件")
    
    # 测试第一个录制
    if len(recordings) > 0:
        tracks_df, meta_df = processor.load_recording(recordings[0])
        print(f"✅ 成功加载测试录制")
        return True
    
    return False
```

## 📝 总结

通过这种组织方式：

- ✅ **代码仓库轻量**: 只包含必要的代码文件
- ✅ **版权合规**: 数据集用户自行获取
- ✅ **易于协作**: 标准化的目录结构
- ✅ **性能优化**: 大文件不影响版本控制
- ✅ **可扩展**: 为未来数据集预留空间

这是学术项目和开源项目的最佳实践！
