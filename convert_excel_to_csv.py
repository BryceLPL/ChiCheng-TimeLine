import pandas as pd
import os
import sys

def convert_excel_to_csv(excel_path, csv_path):
    """
    将Excel文件转换为CSV文件，确保所有列都被保留
    """
    try:
        print(f"正在读取Excel文件: {excel_path}")
        # 直接读取Excel，不做任何假设
        df = pd.read_excel(excel_path)
        
        # 显示读取到的列
        columns = df.columns.tolist()
        print(f"Excel文件中的列 ({len(columns)}个):")
        for i, col in enumerate(columns):
            print(f"  {i+1}. {col}")
        
        # 显示数据维度
        print(f"数据形状: {df.shape} (行数, 列数)")
        
        # 输出前5行数据以检查
        print("\n前5行数据预览:")
        print(df.head())
        
        # 检查是否有空值
        null_counts = df.isnull().sum()
        print("\n各列空值数量:")
        for col in columns:
            print(f"  {col}: {null_counts[col]} 个空值")
        
        # 保存为CSV文件
        print(f"\n正在保存为CSV文件: {csv_path}")
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # 验证CSV是否成功保存
        if os.path.exists(csv_path):
            # 重新读取CSV以验证内容
            csv_df = pd.read_csv(csv_path)
            csv_columns = csv_df.columns.tolist()
            
            print(f"\nCSV文件成功创建!")
            print(f"CSV文件中的列 ({len(csv_columns)}个):")
            for i, col in enumerate(csv_columns):
                print(f"  {i+1}. {col}")
            
            # 验证列数是否一致
            if len(columns) != len(csv_columns):
                print(f"警告: Excel中有{len(columns)}列，但CSV中有{len(csv_columns)}列")
                
                # 显示丢失的列
                missing_cols = set(columns) - set(csv_columns)
                if missing_cols:
                    print(f"丢失的列: {', '.join(missing_cols)}")
            else:
                print(f"✓ 所有列都已成功转换 (共{len(columns)}列)")
            
            print(f"\nCSV文件路径: {os.path.abspath(csv_path)}")
            
            return True
        else:
            print(f"错误: CSV文件没有被创建")
            return False
            
    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 默认文件名
    excel_file = "清末年号大事记.xlsx"
    csv_file = "清末年号大事记.csv"
    
    # 允许命令行指定文件名
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    if len(sys.argv) > 2:
        csv_file = sys.argv[2]
    
    if not os.path.exists(excel_file):
        print(f"错误: Excel文件 '{excel_file}' 不存在")
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]
        
        if excel_files:
            print("\n当前目录下的Excel文件:")
            for i, file in enumerate(excel_files):
                print(f"  {i+1}. {file}")
            
            choice = input("\n请选择要转换的Excel文件编号 (按Enter取消): ")
            if choice.isdigit() and 1 <= int(choice) <= len(excel_files):
                excel_file = excel_files[int(choice)-1]
                print(f"已选择: {excel_file}")
            else:
                print("未选择文件，退出程序")
                sys.exit(1)
        else:
            print("当前目录下没有Excel文件")
            create_sample = input("是否创建示例数据? (y/n): ")
            if create_sample.lower() == 'y':
                try:
                    print("正在运行create_sample_data.py创建示例数据...")
                    import create_sample_data
                    print("示例数据创建完成。")
                    sys.exit(0)
                except Exception as e:
                    print(f"创建示例数据时出错: {e}")
                    sys.exit(1)
            else:
                sys.exit(1)
    
    # 执行转换
    success = convert_excel_to_csv(excel_file, csv_file)
    
    if success:
        print("\n转换完成! 现在您可以运行:")
        print(f"  streamlit run timeline_enhanced.py")
        print("来查看时间轴可视化。") 