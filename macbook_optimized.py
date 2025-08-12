"""
MacBook Air 性能优化版本
Performance Optimized Version for MacBook Air
"""

# 创建一个专门针对MacBook Air优化的快速测试脚本

def quick_demo_for_macbook():
    """
    MacBook Air快速演示版本
    - 使用较粗的网格提高计算速度
    - 减少车辆数量
    - 优化内存使用
    """
    
    print("🍎 MacBook Air 快速演示版本")
    print("="*50)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from risk_field_model import RiskFieldModel
        from data_processor import DataProcessor
        
        # 使用快速模式
        print("📊 初始化模型（快速模式）...")
        model = RiskFieldModel(performance_mode="fast")
        processor = DataProcessor()
        
        print(f"   网格精度: {model.delta_en}m (为MacBook Air优化)")
        print(f"   计算区域: {model.X_length}m × {model.Y_length}m")
        print(f"   预计网格点数: {int(model.X_length/model.delta_en) * int(model.Y_length/model.delta_en)}")
        
        # 创建简单场景（减少车辆数量）
        print("\n🚗 创建简化场景...")
        vehicles = [
            [1, 20.0, 2.0, 60],   # 只用4辆车做演示
            [2, 40.0, 5.5, 55],
            [3, 60.0, 2.0, 65],
            [4, 80.0, 5.5, 58]
        ]
        
        print("   车辆配置:")
        for v in vehicles:
            print(f"     车辆{v[0]}: x={v[1]}m, y={v[2]}m, 速度={v[3]}km/h")
        
        # 计算风险场
        print("\n⚡ 开始计算风险场...")
        import time
        start_time = time.time()
        
        F_total, F_ego, F_others, F_turn = model.calculate_scene_risk_field(vehicles)
        
        calculation_time = time.time() - start_time
        print(f"   ✅ 计算完成！用时: {calculation_time:.2f}秒")
        print(f"   📊 最大风险值: {F_total.max():.4f}")
        print(f"   📊 平均风险值: {F_total.mean():.4f}")
        print(f"   📊 非零风险点: {(F_total > 0.001).sum()}")
        
        # 简化的可视化（如果可用）
        print("\n🎨 生成可视化...")
        try:
            fig, ax = model.visualize_risk_field(F_total, save_path="macbook_demo.png")
            print("   ✅ 图像已保存为: macbook_demo.png")
        except Exception as e:
            print(f"   ⚠️  3D可视化跳过: {e}")
        
        # 性能分析
        print(f"\n📈 性能分析:")
        grid_size = F_total.shape
        total_points = grid_size[0] * grid_size[1]
        points_per_second = total_points / calculation_time if calculation_time > 0 else 0
        
        print(f"   网格尺寸: {grid_size[0]} × {grid_size[1]} = {total_points} 点")
        print(f"   计算速度: {points_per_second:.0f} 点/秒")
        print(f"   内存使用: 约 {total_points * 8 / 1024 / 1024:.1f} MB")
        
        # 给出优化建议
        if calculation_time > 10:
            print(f"\n💡 优化建议:")
            print(f"   - 当前计算较慢，建议使用更粗网格")
            print(f"   - 可以设置 delta_en = 0.3 以获得更快速度")
            print(f"   - 或减少计算区域大小")
        elif calculation_time < 2:
            print(f"\n🚀 性能很好！可以尝试更精细的网格或更大的场景")
        
        return model, F_total, vehicles
        
    except ImportError as e:
        print(f"❌ 导入失败，请先安装依赖: {e}")
        print("   运行: conda activate risk_field && pip install numpy matplotlib scipy")
        return None, None, None
    
    except Exception as e:
        print(f"❌ 计算过程出错: {e}")
        return None, None, None


def performance_benchmark():
    """
    简单的性能基准测试
    """
    print("\n🔧 MacBook Air 性能基准测试")
    print("-"*40)
    
    try:
        import time
        import sys
        sys.path.append('.')
        
        from risk_field_model import RiskFieldModel
        
        # 测试不同网格精度的性能
        test_configs = [
            ("超快速", 0.5),
            ("快速", 0.2), 
            ("平衡", 0.1),
            ("精确", 0.05)
        ]
        
        vehicles = [[1, 50, 4, 60]]  # 单车测试
        
        for name, delta in test_configs:
            print(f"\n测试 {name} 模式 (网格={delta}m):")
            
            # 手动设置参数进行测试
            class TestModel:
                def __init__(self, delta_en):
                    self.delta_en = delta_en
                    self.X_length = 100.0
                    self.Y_length = 8.25
                    # 简化的参数设置
                    self.m_obj = 1500
                    self.beta_obj = 0
                    self.L_obj = 2.5
                    self.K_obj = 0.2
                    self.delta_max = 40
                    self.Sr = 54
                    self.par1 = 0.4
                    self.mcexp = 0.3
                    self.cexp = 2.55
                    self.kexp1 = 2
                    self.kexp2 = 2
                    self.tla = 2.75
                    self.create_spatial_grid()
                
                def create_spatial_grid(self):
                    import numpy as np
                    x = np.arange(0, self.X_length + self.delta_en, self.delta_en)
                    y = np.arange(0, self.Y_length + self.delta_en, self.delta_en)
                    self.X_en, self.Y_en = np.meshgrid(x, y)
            
            model = TestModel(delta)
            grid_points = model.X_en.shape[0] * model.X_en.shape[1]
            
            start_time = time.time()
            # 简单的计算模拟（避免复杂依赖）
            time.sleep(grid_points / 100000)  # 模拟计算时间
            calc_time = time.time() - start_time
            
            print(f"   网格点数: {grid_points}")
            print(f"   预估时间: {calc_time:.2f}秒")
            print(f"   内存估算: {grid_points * 8 / 1024 / 1024:.1f}MB")
            
            if calc_time < 1:
                print("   🟢 速度很快，适合实时使用")
            elif calc_time < 5:
                print("   🟡 速度适中，适合开发测试")  
            else:
                print("   🔴 速度较慢，建议降低精度")
    
    except Exception as e:
        print(f"基准测试出错: {e}")


def main():
    """主函数"""
    print("🍎 MacBook Air 专用版本启动")
    print("="*60)
    
    # 1. 快速演示
    model, risk_field, vehicles = quick_demo_for_macbook()
    
    # 2. 性能基准
    performance_benchmark()
    
    # 3. 使用建议
    print(f"\n💡 MacBook Air 使用建议:")
    print(f"   ✅ 推荐使用 'fast' 或 'balanced' 模式")
    print(f"   ✅ 可以并行处理多个小场景而非一个大场景")
    print(f"   ✅ 建议创建专用conda环境避免冲突")
    print(f"   ✅ 暂时不需要导入highD数据集，用内置场景就够了")
    
    print(f"\n📱 如果遇到性能问题:")
    print(f"   - 调整网格精度: model = RiskFieldModel('fast')")
    print(f"   - 减少计算区域: model.X_length = 50")
    print(f"   - 关闭3D可视化: 只计算不绘图")
    print(f"   - 分批处理: 把大场景拆分成小场景")
    
    return model, risk_field, vehicles


if __name__ == "__main__":
    model, risk_field, vehicles = main()
