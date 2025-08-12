"""
highD数据集处理模块
HighD Dataset Processing Module for Risk Field Model

这个模块处理highD数据集的加载、预处理和格式转换
This module handles loading, preprocessing and format conversion of highD dataset
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class HighDProcessor:
    """
    highD数据集处理器
    专门用于处理德国高速公路真实轨迹数据
    """
    
    def __init__(self, data_root: str = None):
        """
        初始化highD数据处理器
        
        Parameters:
        data_root: highD数据集根目录路径，默认为 ../HighDdata/
        """
        if data_root is None:
            # 默认数据集路径（与代码目录平行）
            current_dir = Path(__file__).parent
            self.data_root = current_dir.parent / "HighDdata"
        else:
            self.data_root = Path(data_root)
            
        self.recordings_meta = {}
        self.current_recording = None
        
        # 检查数据集是否存在
        self._check_data_availability()
        
    def _check_data_availability(self):
        """检查highD数据集是否可用"""
        print(f"🔍 检查highD数据集路径: {self.data_root}")
        
        if not self.data_root.exists():
            print("⚠️  highD数据集未找到！")
            print("请确保HighDdata文件夹与代码目录平行放置")
            print(f"预期路径: {self.data_root}")
            self.data_available = False
            return
            
        # 查找CSV文件
        csv_files = list(self.data_root.glob("*.csv"))
        if len(csv_files) == 0:
            print("⚠️  未找到highD CSV数据文件")
            self.data_available = False
            return
            
        print(f"✅ 找到 {len(csv_files)} 个highD数据文件")
        self.data_available = True
        
        # 识别录制ID
        self._identify_recordings()
    
    def _identify_recordings(self):
        """识别可用的录制文件"""
        print("📋 识别highD录制文件...")
        
        # 查找轨迹文件（通常命名为XX_tracks.csv）
        tracks_files = list(self.data_root.glob("*_tracks.csv"))
        meta_files = list(self.data_root.glob("*_tracksMeta.csv"))
        
        for tracks_file in tracks_files:
            # 提取录制ID (例如: "01_tracks.csv" -> "01")
            recording_id = tracks_file.stem.replace("_tracks", "")
            
            # 查找对应的meta文件
            meta_file = self.data_root / f"{recording_id}_tracksMeta.csv"
            
            if meta_file.exists():
                self.recordings_meta[recording_id] = {
                    'tracks_file': tracks_file,
                    'meta_file': meta_file,
                    'recording_id': recording_id
                }
                print(f"   ✅ 录制 {recording_id}: {tracks_file.name}")
            else:
                print(f"   ⚠️  录制 {recording_id}: 缺少meta文件")
        
        print(f"📊 总计可用录制: {len(self.recordings_meta)} 个")
    
    def list_available_recordings(self) -> List[str]:
        """列出所有可用的录制ID"""
        if not self.data_available:
            print("❌ 数据集不可用")
            return []
        
        return list(self.recordings_meta.keys())
    
    def load_recording(self, recording_id: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        加载指定录制的数据
        
        Parameters:
        recording_id: 录制ID (例如 "01", "02", ...)
        
        Returns:
        tuple: (tracks_df, meta_df) 轨迹数据和元数据
        """
        if not self.data_available:
            raise ValueError("highD数据集不可用")
        
        if recording_id not in self.recordings_meta:
            available = list(self.recordings_meta.keys())
            raise ValueError(f"录制ID {recording_id} 不存在。可用录制: {available}")
        
        print(f"📂 加载录制 {recording_id}...")
        
        recording_info = self.recordings_meta[recording_id]
        
        # 加载轨迹数据
        print("   读取轨迹数据...")
        tracks_df = pd.read_csv(recording_info['tracks_file'])
        
        # 加载元数据
        print("   读取元数据...")  
        meta_df = pd.read_csv(recording_info['meta_file'])
        
        self.current_recording = recording_id
        
        print(f"✅ 成功加载录制 {recording_id}")
        print(f"   轨迹数据: {len(tracks_df)} 行")
        print(f"   元数据: {len(meta_df)} 条轨迹")
        
        return tracks_df, meta_df
    
    def get_recording_summary(self, recording_id: str) -> Dict:
        """
        获取录制的基本信息摘要
        """
        tracks_df, meta_df = self.load_recording(recording_id)
        
        summary = {
            'recording_id': recording_id,
            'total_frames': tracks_df['frame'].max() - tracks_df['frame'].min() + 1,
            'total_vehicles': len(meta_df),
            'duration_seconds': (tracks_df['frame'].max() - tracks_df['frame'].min()) * 0.04,  # 25Hz
            'frame_rate': 25.0,
            'driving_direction': meta_df['drivingDirection'].value_counts().to_dict(),
            'vehicle_classes': meta_df['class'].value_counts().to_dict()
        }
        
        return summary
    
    def extract_scenario_by_time(self, tracks_df: pd.DataFrame, meta_df: pd.DataFrame, 
                                start_frame: int, duration_frames: int = 125) -> List[Dict]:
        """
        提取指定时间段的场景数据
        
        Parameters:
        start_frame: 开始帧
        duration_frames: 持续帧数 (默认125帧 = 5秒 @ 25Hz)
        
        Returns:
        List[Dict]: 车辆数据列表，格式为 [{'id': 1, 'x': 10.5, 'y': 2.1, 'speed': 60}, ...]
        """
        end_frame = start_frame + duration_frames
        
        # 提取指定时间段的轨迹数据
        scenario_tracks = tracks_df[
            (tracks_df['frame'] >= start_frame) & 
            (tracks_df['frame'] < end_frame)
        ].copy()
        
        if len(scenario_tracks) == 0:
            return []
        
        # 选择中间帧作为快照
        snapshot_frame = start_frame + duration_frames // 2
        snapshot_data = scenario_tracks[scenario_tracks['frame'] == snapshot_frame]
        
        vehicles = []
        for _, vehicle in snapshot_data.iterrows():
            # 计算速度 (m/s 转换为 km/h)
            speed_ms = np.sqrt(vehicle['xVelocity']**2 + vehicle['yVelocity']**2)
            speed_kmh = speed_ms * 3.6
            
            vehicle_data = {
                'id': int(vehicle['id']),
                'x': float(vehicle['x']),
                'y': float(vehicle['y']),
                'speed': float(speed_kmh)
            }
            vehicles.append(vehicle_data)
        
        return vehicles
    
    def find_overtaking_scenarios(self, tracks_df: pd.DataFrame, meta_df: pd.DataFrame, 
                                 min_speed_diff: float = 10.0) -> List[Dict]:
        """
        自动识别超车场景
        
        Parameters:
        min_speed_diff: 最小速度差异 (km/h)
        
        Returns:
        List[Dict]: 超车场景列表
        """
        print("🔍 搜索超车场景...")
        
        overtaking_scenarios = []
        
        # 按帧分组处理
        frames = sorted(tracks_df['frame'].unique())
        
        for i, frame in enumerate(frames[::50]):  # 每2秒检查一次
            frame_data = tracks_df[tracks_df['frame'] == frame]
            
            # 查找相邻车道的车辆对
            for _, vehicle1 in frame_data.iterrows():
                for _, vehicle2 in frame_data.iterrows():
                    if vehicle1['id'] >= vehicle2['id']:
                        continue
                    
                    # 检查是否在相邻车道
                    y_diff = abs(vehicle1['y'] - vehicle2['y'])
                    if not (2.0 < y_diff < 5.0):  # 车道宽度约3.5m
                        continue
                    
                    # 检查速度差异
                    speed1 = np.sqrt(vehicle1['xVelocity']**2 + vehicle1['yVelocity']**2) * 3.6
                    speed2 = np.sqrt(vehicle2['xVelocity']**2 + vehicle2['yVelocity']**2) * 3.6
                    
                    if abs(speed1 - speed2) > min_speed_diff:
                        vehicles = self.extract_scenario_by_time(tracks_df, meta_df, frame, 125)
                        
                        if len(vehicles) >= 3:  # 至少3辆车的场景
                            scenario = {
                                'type': 'overtaking',
                                'frame': frame,
                                'vehicles': vehicles,
                                'description': f'超车场景 - 帧{frame}'
                            }
                            overtaking_scenarios.append(scenario)
                            
                            if len(overtaking_scenarios) >= 5:  # 限制数量
                                break
                
                if len(overtaking_scenarios) >= 5:
                    break
            
            if len(overtaking_scenarios) >= 5:
                break
        
        print(f"✅ 找到 {len(overtaking_scenarios)} 个超车场景")
        return overtaking_scenarios
    
    def convert_to_risk_field_format(self, vehicles: List[Dict]) -> List[List]:
        """
        转换为风险场模型所需的格式
        
        Parameters:
        vehicles: highD格式的车辆数据
        
        Returns:
        List[List]: 风险场模型格式 [[id, x, y, speed], ...]
        """
        risk_field_vehicles = []
        
        for vehicle in vehicles:
            risk_field_vehicle = [
                vehicle['id'],
                vehicle['x'],
                vehicle['y'],  
                vehicle['speed']
            ]
            risk_field_vehicles.append(risk_field_vehicle)
        
        return risk_field_vehicles
    
    def save_scenarios(self, scenarios: List[Dict], output_file: str):
        """
        保存提取的场景数据
        
        Parameters:
        scenarios: 场景数据列表
        output_file: 输出文件路径
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换numpy类型为Python原生类型，确保JSON可序列化
        serializable_scenarios = []
        for scenario in scenarios:
            serializable_scenario = {
                'type': scenario['type'],
                'frame': int(scenario['frame']),
                'description': scenario['description'],
                'vehicles': []
            }
            
            for vehicle in scenario['vehicles']:
                serializable_vehicle = {
                    'id': int(vehicle['id']),
                    'x': float(vehicle['x']),
                    'y': float(vehicle['y']),
                    'speed': float(vehicle['speed'])
                }
                serializable_scenario['vehicles'].append(serializable_vehicle)
            
            serializable_scenarios.append(serializable_scenario)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_scenarios, f, indent=2, ensure_ascii=False)
        
        print(f"💾 场景数据已保存到: {output_path}")
    
    def create_data_usage_guide(self):
        """创建数据使用指南"""
        guide = """
# highD数据集使用指南

## 数据集结构
```
HighDdata/                    # 与代码目录平行
├── 01_tracks.csv            # 录制01轨迹数据
├── 01_tracksMeta.csv        # 录制01元数据
├── 02_tracks.csv            # 录制02轨迹数据  
├── 02_tracksMeta.csv        # 录制02元数据
└── ...                      # 更多录制文件
```

## 基本使用

```python
from highd_processor import HighDProcessor

# 初始化处理器
processor = HighDProcessor()

# 列出可用录制
recordings = processor.list_available_recordings()
print(f"可用录制: {recordings}")

# 加载数据
tracks_df, meta_df = processor.load_recording("01")

# 提取场景
vehicles = processor.extract_scenario_by_time(tracks_df, meta_df, start_frame=1000)

# 转换格式用于风险场计算
risk_field_vehicles = processor.convert_to_risk_field_format(vehicles)

# 使用风险场模型
from risk_field_model import RiskFieldModel
model = RiskFieldModel()
F_total, *_ = model.calculate_scene_risk_field(risk_field_vehicles)
```

## 注意事项

1. **数据版权**: highD数据集受版权保护，仅用于学术研究
2. **数据大小**: 数据集文件较大，不应上传到版本控制系统
3. **处理速度**: 大数据集处理需要时间，建议从小样本开始
4. **内存使用**: 加载完整录制可能占用大量内存

## 常见问题

Q: 数据集路径找不到？
A: 确保HighDdata文件夹与python_reproduction文件夹平行放置

Q: CSV文件格式错误？
A: 确保下载的是官方highD数据集的CSV格式版本

Q: 内存不足？
A: 可以分批处理数据，或使用较小的时间窗口
"""
        
        with open("highd_usage_guide.md", "w", encoding="utf-8") as f:
            f.write(guide)
        
        print("📖 已创建数据使用指南: highd_usage_guide.md")


def demo_highd_processing():
    """
    演示highD数据处理功能
    """
    print("🚗 highD数据集处理演示")
    print("=" * 50)
    
    # 创建处理器
    processor = HighDProcessor()
    
    if not processor.data_available:
        print("⚠️  演示需要highD数据集")
        print("请将HighDdata文件夹放置在代码目录的父级目录中")
        return None
    
    # 列出可用录制
    recordings = processor.list_available_recordings()
    print(f"\n📋 可用录制: {recordings}")
    
    if len(recordings) == 0:
        print("❌ 没有找到可用的录制文件")
        return None
    
    # 使用第一个录制进行演示
    demo_recording = recordings[0]
    print(f"\n🎯 使用录制 {demo_recording} 进行演示")
    
    try:
        # 获取录制摘要
        summary = processor.get_recording_summary(demo_recording)
        print("\n📊 录制摘要:")
        print(f"   录制ID: {summary['recording_id']}")
        print(f"   总帧数: {summary['total_frames']}")
        print(f"   总车辆数: {summary['total_vehicles']}")
        print(f"   持续时间: {summary['duration_seconds']:.1f} 秒")
        print(f"   行驶方向: {summary['driving_direction']}")
        
        # 加载数据
        tracks_df, meta_df = processor.load_recording(demo_recording)
        
        # 提取一个时间段的场景
        print(f"\n🎬 提取场景快照...")
        vehicles = processor.extract_scenario_by_time(tracks_df, meta_df, start_frame=1000, duration_frames=125)
        
        if len(vehicles) > 0:
            print(f"   ✅ 提取到 {len(vehicles)} 辆车的场景")
            
            # 显示前几辆车的信息
            for i, vehicle in enumerate(vehicles[:3]):
                print(f"     车辆{vehicle['id']}: x={vehicle['x']:.1f}m, y={vehicle['y']:.1f}m, 速度={vehicle['speed']:.1f}km/h")
            
            # 转换为风险场格式
            risk_field_vehicles = processor.convert_to_risk_field_format(vehicles)
            print(f"\n🔄 已转换为风险场格式")
            
            return processor, risk_field_vehicles
        else:
            print("   ⚠️  该时间段没有车辆数据")
    
    except Exception as e:
        print(f"❌ 处理过程中出错: {e}")
        return None
    
    return processor


if __name__ == "__main__":
    processor = demo_highd_processing()
