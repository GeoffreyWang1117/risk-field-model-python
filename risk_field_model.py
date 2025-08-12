"""
Risk Field Model for Autonomous Driving - Python Implementation
基于Nature Communications论文的风险场模型Python复现版本

This module implements the risk field calculation for autonomous driving scenarios,
reproducing the MATLAB code functionality in Python.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings('ignore')

class RiskFieldModel:
    """
    主要的风险场模型类，用于计算和可视化驾驶风险场
    """
    
    def __init__(self, performance_mode="balanced"):
        """
        初始化模型参数
        
        performance_mode: "fast", "balanced", "accurate"
        - fast: 适合MacBook Air等轻量级设备，快速预览
        - balanced: 平衡速度和精度（默认）
        - accurate: 高精度，需要较强计算能力
        """
        # 空间网格参数 - 根据性能模式调整
        self.X_length = 100.0  # 道路长度 [m]
        self.Y_length = 8.25   # 道路宽度 [m]
        
        # 根据性能模式设置网格精度
        if performance_mode == "fast":
            self.delta_en = 0.2    # 粗网格，快速计算
        elif performance_mode == "balanced":
            self.delta_en = 0.1    # 中等网格，平衡速度精度
        else:  # accurate
            self.delta_en = 0.05   # 细网格，高精度
        
        # 车辆基础参数
        self.m_obj = 1500      # 车辆质量 [kg]
        self.beta_obj = 0      # 侧滑角
        self.L_obj = 2.5       # 轴距 [m]
        self.K_obj = 0.2       # 稳定性因子
        self.delta_max = 40    # 最大转向角 [度]
        
        # 风险场参数
        self.Sr = 54
        self.par1 = 0.4
        self.mcexp = 0.3
        self.cexp = 2.55
        self.kexp1 = 2
        self.kexp2 = 2
        self.tla = 2.75
        
        # 创建空间网格
        self.create_spatial_grid()
        
    def create_spatial_grid(self):
        """创建空间网格"""
        x = np.arange(0, self.X_length + self.delta_en, self.delta_en)
        y = np.arange(0, self.Y_length + self.delta_en, self.delta_en)
        self.X_en, self.Y_en = np.meshgrid(x, y)
        
    def gaussian_3d_torus_functions(self):
        """实现高斯3D环面函数集合（与原MATLAB代码对应）"""
        
        def delta_process(delta_a):
            """处理转向角"""
            if abs(delta_a) < 1e-8:
                return 1e-8
            else:
                return delta_a
        
        def phiv_process(phiv_a):
            """处理车辆朝向角"""
            pi2temp = np.ceil(np.abs(phiv_a / (2 * np.pi)))
            phiv = np.abs(np.remainder(2 * np.pi * pi2temp + phiv_a, 2 * np.pi))
            return phiv
        
        def dla_calc(tla, V):
            """计算前瞻距离"""
            dla = tla * V
            if dla < 1:
                dla = 1
            return dla
        
        def R_calc(L, delta):
            """计算转弯半径"""
            return np.abs(L / np.tan(delta))
        
        def xcyc_calc(xv, yv, phiv, delta, R):
            """计算转弯圆心坐标"""
            if delta > 0:
                phil = phiv + np.pi / 2
            else:
                phil = phiv - np.pi / 2
            xc = R * np.cos(phil) + xv
            yc = R * np.sin(phil) + yv
            return xc, yc
        
        def mexp_calc(kexp, mcexp, delta, v=0):
            """计算mexp参数"""
            return mcexp + kexp * abs(delta)
        
        def arclen_calc(x, y, xv, yv, delta, xc, yc, R):
            """计算弧长"""
            mag_u = np.abs(np.sqrt((xv - xc) ** 2 + (yv - yc) ** 2))
            mag_v = np.abs(np.sqrt((x - xc) ** 2 + (y - yc) ** 2))
            dot_pro = (xv - xc) * (x - xc) + (yv - yc) * (y - yc)
            costheta = dot_pro / (mag_u * mag_v)
            costheta_clipped = np.clip(costheta, -1, 1)
            theta_abs = np.arccos(costheta_clipped)
            sign_theta = np.sign((xv - xc) * (y - yc) - (x - xc) * (yv - yc))
            theta_pos_neg = np.sign(delta) * sign_theta * theta_abs
            theta = np.remainder(2 * np.pi + theta_pos_neg, 2 * np.pi)
            arc_len = R * theta
            return arc_len
        
        def a_calc(arc_len, par1, dla):
            """计算a参数"""
            par2 = dla
            a_par = par1 * (arc_len - par2) ** 2
            a_par_sign1 = (np.sign(dla - arc_len) + 1) / 2
            a_par_sign2 = (np.sign(a_par) + 1) / 2
            a_par_sign3 = (np.sign(arc_len) + 1) / 2
            a = a_par_sign1 * a_par_sign2 * a_par_sign3 * a_par
            return a
        
        def sigma_calc(arc_len, prb1, prb2):
            """计算sigma参数"""
            return prb1 * arc_len + prb2
        
        def z_calc(x, y, xc, yc, R, a, sigma1, sigma2):
            """计算高斯分布值"""
            dist_R = np.sqrt((x - xc) ** 2 + (y - yc) ** 2)
            a_inside = (1 - np.sign(dist_R - R)) / 2
            a_outside = (1 + np.sign(dist_R - R)) / 2
            
            num = -((np.sqrt((x - xc) ** 2 + (y - yc) ** 2) - R) ** 2)
            
            den1 = 2 * sigma1 ** 2
            zpure1 = a * a_inside * np.exp(num / den1)
            
            den2 = 2 * sigma2 ** 2
            zpure2 = a * a_outside * np.exp(num / den2)
            
            zpure = zpure1 + zpure2
            return zpure
        
        return {
            'delta_process': delta_process,
            'phiv_process': phiv_process,
            'dla_calc': dla_calc,
            'R_calc': R_calc,
            'xcyc_calc': xcyc_calc,
            'mexp_calc': mexp_calc,
            'arclen_calc': arclen_calc,
            'a_calc': a_calc,
            'sigma_calc': sigma_calc,
            'z_calc': z_calc
        }
    
    def field_straight(self, vehicle_params):
        """
        计算直行车辆的风险场（对应MATLAB中的Field_straight函数）
        
        Parameters:
        vehicle_params: [vehicle_id, x, y, speed, mass, beta, L, K, delta_max]
        """
        funcs = self.gaussian_3d_torus_functions()
        
        # 解析车辆参数
        vehicle_id, x, y, speed, mass, beta, L, K, delta_max = vehicle_params
        
        # 转换速度单位 (假设输入是km/h，转换为m/s)
        if speed > 50:  # 如果速度大于50，假设是km/h
            speed = speed / 3.6
            
        # 计算基础参数
        steering_angle = 0.001  # 微小转向角（直行）
        delta_fut_h = (np.pi / 180) * steering_angle / self.Sr
        phiv_a = 0  # 直行时航向角为0
        
        # 使用高斯函数计算风险场
        delta = funcs['delta_process'](delta_fut_h)
        phiv = funcs['phiv_process'](phiv_a)
        dla = funcs['dla_calc'](self.tla, speed)
        R = funcs['R_calc'](L, delta)
        xc, yc = funcs['xcyc_calc'](x, y, phiv, delta, R)
        
        mexp1 = funcs['mexp_calc'](self.kexp1, self.mcexp, delta, speed)
        mexp2 = funcs['mexp_calc'](self.kexp2, self.mcexp, delta, speed)
        
        arc_len = funcs['arclen_calc'](self.X_en, self.Y_en, x, y, delta, xc, yc, R)
        a = funcs['a_calc'](arc_len, self.par1, dla)
        sigma1 = funcs['sigma_calc'](arc_len, mexp1, self.cexp)
        sigma2 = funcs['sigma_calc'](arc_len, mexp2, self.cexp)
        
        Z = funcs['z_calc'](self.X_en, self.Y_en, xc, yc, R, a, sigma1, sigma2)
        
        return Z
    
    def field_turn(self, vehicle_params):
        """
        计算转弯车辆的风险场（对应MATLAB中的Field函数）
        """
        funcs = self.gaussian_3d_torus_functions()
        
        # 解析车辆参数
        vehicle_id, x, y, speed, mass, beta, L, K, delta_max = vehicle_params
        
        # 转换速度单位
        if speed > 50:
            speed = speed / 3.6
            
        # 转弯参数（可以根据实际情况调整）
        steering_angle = 5.0  # 转向角度
        delta_fut_h = (np.pi / 180) * steering_angle / self.Sr
        phiv_a = (np.pi / 180) * 0  # 可以根据车辆朝向调整
        
        delta = funcs['delta_process'](delta_fut_h)
        phiv = funcs['phiv_process'](phiv_a)
        dla = funcs['dla_calc'](self.tla, speed)
        R = funcs['R_calc'](L, delta)
        xc, yc = funcs['xcyc_calc'](x, y, phiv, delta, R)
        
        mexp1 = funcs['mexp_calc'](self.kexp1, self.mcexp, delta, speed)
        mexp2 = funcs['mexp_calc'](self.kexp2, self.mcexp, delta, speed)
        
        arc_len = funcs['arclen_calc'](self.X_en, self.Y_en, x, y, delta, xc, yc, R)
        a = funcs['a_calc'](arc_len, self.par1, dla)
        sigma1 = funcs['sigma_calc'](arc_len, mexp1, self.cexp)
        sigma2 = funcs['sigma_calc'](arc_len, mexp2, self.cexp)
        
        Z = funcs['z_calc'](self.X_en, self.Y_en, xc, yc, R, a, sigma1, sigma2)
        
        return Z
    
    def calculate_scene_risk_field(self, vehicles_data):
        """
        计算整个场景的风险场（复现MATLAB主函数逻辑）
        
        Parameters:
        vehicles_data: 车辆数据列表，每个元素包含 [id, x, y, speed, ...]
        """
        
        # 定义自车位置（对应MATLAB中的ego vehicles）
        ego_vehicles = [
            [1, 13, 6, 14, self.m_obj, self.beta_obj, self.L_obj, self.K_obj, self.delta_max],
            [1, 22.5, 5.75, 15, self.m_obj, self.beta_obj, self.L_obj, self.K_obj, self.delta_max],
            [1, 28, 2.5, 17.2, self.m_obj, self.beta_obj, self.L_obj, self.K_obj, self.delta_max],
            [1, 65, 6.5, 21, self.m_obj, self.beta_obj, self.L_obj, self.K_obj, self.delta_max]
        ]
        
        # 定义转弯车辆
        turn_vehicles = [
            [1, 25, 6, 19.5, self.m_obj, self.beta_obj, self.L_obj, self.K_obj, self.delta_max]
        ]
        
        # 计算自车风险场
        F_ego_total = np.zeros_like(self.X_en)
        for ego_params in ego_vehicles:
            F_ego = self.field_straight(ego_params)
            F_ego[np.isnan(F_ego)] = 0  # 将NaN值设为0
            F_ego_total += F_ego
        
        # 计算其他车辆风险场
        F_others = np.zeros_like(self.X_en)
        for vehicle in vehicles_data:
            # 确保vehicle参数格式正确
            if len(vehicle) >= 4:
                vehicle_params = [
                    vehicle[0],  # id
                    vehicle[1],  # x
                    vehicle[2],  # y
                    vehicle[3],  # speed
                    self.m_obj, self.beta_obj, self.L_obj, self.K_obj, self.delta_max
                ]
                F_tmp = self.field_straight(vehicle_params)
                F_tmp[np.isnan(F_tmp)] = 0
                F_others += F_tmp
        
        # 计算转弯风险场
        F_turn_total = np.zeros_like(self.X_en)
        for turn_params in turn_vehicles:
            F_turn = self.field_turn(turn_params)
            F_turn[np.isnan(F_turn)] = 0
            F_turn_straight = self.field_straight(turn_params)
            F_turn_straight[np.isnan(F_turn_straight)] = 0
            F_turn_total += 0.6 * F_turn + 0.5 * F_turn_straight
        
        # 合成总风险场（对应MATLAB中的组合逻辑）
        F_total = F_ego_total + F_others + F_turn_total
        
        # 处理小值
        F_total[F_total < 0.001] = 0
        
        return F_total, F_ego_total, F_others, F_turn_total
    
    def visualize_risk_field(self, F_total, save_path=None, show_lanes=True):
        """
        可视化风险场（复现MATLAB的3D可视化）
        
        Parameters:
        F_total: 总风险场矩阵
        save_path: 保存路径（可选）
        show_lanes: 是否显示车道线
        """
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 绘制3D表面
        surf = ax.plot_surface(self.X_en, self.Y_en, F_total, 
                              cmap='jet', alpha=0.8, 
                              linewidth=0, antialiased=True)
        
        # 设置坐标轴
        ax.set_xlim([0, self.X_length])
        ax.set_ylim([0, self.Y_length])
        
        # 设置颜色范围（对应MATLAB中的caxis）
        draw_max_F = 1.2 * self.m_obj * 50.0**2 / 10
        surf.set_clim(0, draw_max_F)
        
        # 添加车道线（如果需要）
        if show_lanes:
            lx = np.linspace(-5, self.X_length, 1000)
            ly1 = np.ones_like(lx) * 0.5
            ly2 = np.ones_like(lx) * (3.5 * 1 + 0.5)
            ly3 = np.ones_like(lx) * (3.5 * 2 + 0.5)
            ly6 = np.ones_like(lx) * (3.5 * 2 + 0.75)
            lz = np.ones_like(lx) * np.max(F_total) * 1.1
            
            ax.plot(lx, ly1, lz, 'w-', linewidth=2)
            ax.plot(lx, ly2, lz, 'w--', linewidth=1.5)
            ax.plot(lx, ly3, lz, 'w-', linewidth=2)
            ax.plot(lx, ly6, lz, 'w-', linewidth=2)
        
        # 设置标签和标题
        ax.set_xlabel('X [m]', fontname='Times New Roman', fontsize=10)
        ax.set_ylabel('Y [m]', fontname='Times New Roman', fontsize=10)
        ax.set_zlabel('F_ki [N]', fontname='Times New Roman', fontsize=10)
        ax.set_title('Risk Field Visualization', fontsize=12)
        
        # 添加颜色条
        fig.colorbar(surf, shrink=0.5, aspect=20)
        
        # 设置网格
        ax.grid(True)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        return fig, ax
    
    def create_demo_scenario(self):
        """
        创建一个演示场景（模拟车辆数据）
        """
        # 创建一些示例车辆数据
        vehicles_data = [
            [4, 6.5, 1.7, 17],     # [id, x, y, speed] - 对应MATLAB中的imp_d
            [2, 20, 3.5, 15],      # 其他车辆
            [3, 45, 6, 18],
            [5, 70, 2, 20]
        ]
        
        return vehicles_data


def main():
    """主函数 - 演示如何使用风险场模型"""
    
    print("🚗 启动风险场模型计算...")
    
    # 创建风险场模型实例
    risk_model = RiskFieldModel()
    
    # 创建演示场景
    vehicles_data = risk_model.create_demo_scenario()
    
    print(f"📊 计算场景风险场，包含 {len(vehicles_data)} 辆车...")
    
    # 计算风险场
    F_total, F_ego, F_others, F_turn = risk_model.calculate_scene_risk_field(vehicles_data)
    
    print(f"✅ 风险场计算完成！")
    print(f"   - 最大风险值: {np.max(F_total):.2f}")
    print(f"   - 平均风险值: {np.mean(F_total):.2f}")
    print(f"   - 网格尺寸: {F_total.shape}")
    
    # 可视化结果
    print("🎨 生成3D可视化图...")
    risk_model.visualize_risk_field(F_total, save_path="risk_field_demo.png")
    
    # 计算特定位置的风险值（对应MATLAB中的F_f计算）
    test_x, test_y = 50, 3.5  # 测试位置
    x_idx = int(test_x / risk_model.delta_en)
    y_idx = int(test_y / risk_model.delta_en)
    
    if 0 <= x_idx < F_total.shape[1] and 0 <= y_idx < F_total.shape[0]:
        risk_at_point = F_total[y_idx, x_idx]
        print(f"📍 位置 ({test_x}, {test_y}) 的风险值: {risk_at_point:.4f}")
    
    print("🎉 演示完成！")
    
    return risk_model, F_total


if __name__ == "__main__":
    model, risk_field = main()
