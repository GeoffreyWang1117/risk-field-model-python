"""
数据处理模块 - 处理车辆轨迹数据和场景数据
Data Processing Module for Risk Field Model
"""

import numpy as np
import os
import json

class DataProcessor:
    """数据处理类，用于加载和预处理车辆数据"""
    
    def __init__(self):
        self.vehicle_data = None
        self.scenario_data = None
        
    def load_matlab_input_data(self, file_path):
        """
        加载MATLAB格式的输入数据（对应input_data.txt）
        """
        try:
            if os.path.exists(file_path):
                data = []
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip() and not line.strip().startswith('%'):
                            # 解析每行数据
                            values = [float(x) for x in line.strip().split()]
                            data.append(values)
                
                self.vehicle_data = np.array(data)
                print(f"✅ 成功加载数据文件: {file_path}")
                print(f"   数据形状: {self.vehicle_data.shape}")
                return self.vehicle_data
            else:
                print(f"⚠️  数据文件不存在: {file_path}")
                return self.create_default_scenario()
                
        except Exception as e:
            print(f"❌ 加载数据文件失败: {e}")
            return self.create_default_scenario()
    
    def create_default_scenario(self):
        """
        创建默认测试场景
        """
        print("🔄 创建默认测试场景...")
        
        # 创建一个典型的高速公路场景
        default_vehicles = [
            # [vehicle_id, x, y, vx, speed, width, length, class, time, lane, frame_id, ...]
            [1, 10, 2.0, 15, 54, 1.8, 4.5, 1, 0, 1, 4],
            [2, 25, 6.0, 12, 43.2, 1.8, 4.5, 1, 0, 2, 4],
            [3, 40, 3.5, 18, 64.8, 1.8, 4.5, 1, 0, 1, 4],
            [4, 60, 5.0, 16, 57.6, 1.8, 4.5, 1, 0, 2, 4],
            [5, 80, 1.5, 20, 72, 1.8, 4.5, 1, 0, 1, 4],
        ]
        
        self.vehicle_data = np.array(default_vehicles)
        print(f"   创建了 {len(default_vehicles)} 辆车的场景")
        return self.vehicle_data
    
    def extract_vehicles_by_frame(self, frame_id):
        """
        提取指定帧的车辆数据（对应MATLAB中的帧提取逻辑）
        """
        if self.vehicle_data is None:
            return []
        
        # 查找指定帧的车辆（假设最后一列是frame_id）
        if self.vehicle_data.shape[1] > 10:
            frame_vehicles = self.vehicle_data[self.vehicle_data[:, -1] == frame_id]
        else:
            # 如果没有frame信息，返回所有车辆
            frame_vehicles = self.vehicle_data
        
        # 转换为所需格式 [id, x, y, speed]
        vehicles_for_risk_calc = []
        for vehicle in frame_vehicles:
            if len(vehicle) >= 4:
                vehicle_info = [
                    int(vehicle[0]),  # vehicle_id
                    float(vehicle[1]),  # x position
                    float(vehicle[2]),  # y position
                    float(vehicle[4]) if len(vehicle) > 4 else float(vehicle[3])  # speed
                ]
                vehicles_for_risk_calc.append(vehicle_info)
        
        return vehicles_for_risk_calc
    
    def create_highway_scenario(self, num_vehicles=10, road_length=100):
        """
        创建高速公路测试场景
        """
        print(f"🛣️  创建高速公路场景: {num_vehicles}辆车, 道路长度{road_length}m")
        
        np.random.seed(42)  # 确保结果可重复
        
        vehicles = []
        lane_centers = [2.0, 5.5]  # 两条车道的中心位置
        
        for i in range(num_vehicles):
            vehicle_id = i + 1
            
            # 随机分配车道和位置
            lane = np.random.choice(lane_centers)
            x = np.random.uniform(10, road_length - 10)
            y = lane + np.random.uniform(-0.5, 0.5)  # 在车道内小幅度变化
            
            # 随机速度 (50-80 km/h)
            speed = np.random.uniform(50, 80)
            
            vehicles.append([vehicle_id, x, y, speed])
        
        # 按x位置排序
        vehicles.sort(key=lambda x: x[1])
        
        print(f"   生成车辆位置:")
        for v in vehicles[:5]:  # 显示前5辆车
            print(f"     车辆{v[0]}: x={v[1]:.1f}m, y={v[2]:.1f}m, 速度={v[3]:.1f}km/h")
        
        if len(vehicles) > 5:
            print(f"     ... 以及其他 {len(vehicles)-5} 辆车")
        
        return vehicles
    
    def create_overtaking_scenario(self):
        """
        创建超车场景
        """
        print("🚗💨 创建超车场景...")
        
        vehicles = [
            # 前方慢车
            [1, 30, 2.0, 40],    # 慢速车在右车道
            
            # 超车车辆
            [2, 20, 2.0, 65],    # 快速车准备超车，在右车道
            
            # 左车道车辆
            [3, 45, 5.5, 55],    # 左车道车辆
            [4, 60, 5.5, 50],    # 另一辆左车道车辆
            
            # 远处车辆
            [5, 80, 2.0, 45],    # 远方右车道
            [6, 85, 5.5, 60],    # 远方左车道
        ]
        
        print("   超车场景车辆配置:")
        for v in vehicles:
            lane_desc = "右车道" if v[2] < 4 else "左车道"
            print(f"     车辆{v[0]}: x={v[1]}m, {lane_desc}, 速度={v[3]}km/h")
        
        return vehicles
    
    def create_merging_scenario(self):
        """
        创建汇入场景
        """
        print("🛤️  创建汇入场景...")
        
        vehicles = [
            # 主路车辆
            [1, 20, 2.0, 60],    # 主路车辆1
            [2, 40, 2.0, 55],    # 主路车辆2
            [3, 70, 2.0, 58],    # 主路车辆3
            
            # 匝道汇入车辆
            [4, 35, 0.5, 50],    # 汇入车辆，在匝道上
            
            # 左车道车辆
            [5, 30, 5.5, 65],    # 左车道快速车辆
            [6, 60, 5.5, 55],    # 左车道正常车辆
        ]
        
        print("   汇入场景车辆配置:")
        for v in vehicles:
            if v[2] < 1:
                lane_desc = "匝道"
            elif v[2] < 4:
                lane_desc = "右车道"
            else:
                lane_desc = "左车道"
            print(f"     车辆{v[0]}: x={v[1]}m, {lane_desc}, 速度={v[3]}km/h")
        
        return vehicles
    
    def save_scenario(self, vehicles, scenario_name, save_path=None):
        """
        保存场景数据
        """
        if save_path is None:
            save_path = f"scenario_{scenario_name}.json"
        
        scenario_data = {
            "scenario_name": scenario_name,
            "vehicles": vehicles,
            "timestamp": str(np.datetime64('now')),
            "description": f"Generated scenario with {len(vehicles)} vehicles"
        }
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(scenario_data, f, indent=2, ensure_ascii=False)
            print(f"💾 场景已保存到: {save_path}")
        except Exception as e:
            print(f"❌ 保存场景失败: {e}")
    
    def load_scenario(self, file_path):
        """
        加载保存的场景数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                scenario_data = json.load(f)
            
            print(f"📂 已加载场景: {scenario_data.get('scenario_name', 'Unknown')}")
            print(f"   描述: {scenario_data.get('description', 'No description')}")
            
            return scenario_data['vehicles']
        
        except Exception as e:
            print(f"❌ 加载场景失败: {e}")
            return []


def demo_data_processor():
    """
    演示数据处理器的使用
    """
    print("🔧 演示数据处理器...")
    
    processor = DataProcessor()
    
    # 1. 尝试加载MATLAB数据
    matlab_data_path = "/Users/zhaohuiwang/论文/自动驾驶论文相关/field model/input_data.txt"
    processor.load_matlab_input_data(matlab_data_path)
    
    # 2. 创建不同类型的测试场景
    print("\n" + "="*50)
    highway_vehicles = processor.create_highway_scenario(8, 100)
    processor.save_scenario(highway_vehicles, "highway_test")
    
    print("\n" + "="*50)
    overtaking_vehicles = processor.create_overtaking_scenario()
    processor.save_scenario(overtaking_vehicles, "overtaking_test")
    
    print("\n" + "="*50)
    merging_vehicles = processor.create_merging_scenario()
    processor.save_scenario(merging_vehicles, "merging_test")
    
    return processor, highway_vehicles, overtaking_vehicles, merging_vehicles


if __name__ == "__main__":
    processor, highway, overtaking, merging = demo_data_processor()
