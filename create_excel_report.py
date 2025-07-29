import pandas as pd
import json
from datetime import datetime

def create_excel_from_batch_results():
    """Create Excel file from batch city test results"""
    
    report_file = "industrial_commercial_price_coverage_report_1753776086.md"
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Report file {report_file} not found")
        return
    
    cities_data = []
    lines = content.split('\n')
    
    in_table = False
    for line in lines:
        if line.startswith('| 序号 | 城市 (City)'):
            in_table = True
            continue
        elif line.startswith('|---'):
            continue
        elif in_table and line.startswith('|') and '|' in line:
            clean_line = line[1:]  # Remove leading |
            parts = [part.strip() for part in clean_line.split('|') if part.strip()]
            if len(parts) >= 4:
                try:
                    seq_num = parts[0]
                    city = parts[1]
                    status = parts[2]
                    result = parts[3]
                    
                    success = "✅ 成功" in status
                    price = ""
                    error_msg = ""
                    
                    if success:
                        if "元/千瓦时" in result:
                            price = result
                    else:
                        error_msg = result
                    
                    cities_data.append({
                        '序号': seq_num,
                        '城市名称': city,
                        '查询状态': '成功' if success else '失败',
                        '电价结果': price,
                        '错误信息': error_msg,
                        '备注': result
                    })
                except (IndexError, ValueError):
                    continue
        elif in_table and not line.startswith('|'):
            break
    
    if not cities_data:
        print("No city data found in report")
        return
    
    df = pd.DataFrame(cities_data)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"工商业电价城市覆盖测试结果_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='测试结果', index=False)
        
        total_cities = len(df)
        successful_cities = len(df[df['查询状态'] == '成功'])
        failed_cities = total_cities - successful_cities
        coverage_rate = (successful_cities / total_cities) * 100
        
        summary_data = {
            '统计项目': ['测试城市总数', '成功查询城市数', '失败城市数', '数据覆盖率'],
            '数值': [total_cities, successful_cities, failed_cities, f"{coverage_rate:.1f}%"],
            '备注': ['包含直辖市和省级城市', '返回有效电价数据', 'API未查询到相关结果', '成功率统计']
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
        
        successful_df = df[df['查询状态'] == '成功'].copy()
        if not successful_df.empty:
            successful_df.to_excel(writer, sheet_name='成功城市列表', index=False)
        
        failed_df = df[df['查询状态'] == '失败'].copy()
        if not failed_df.empty:
            failed_df.to_excel(writer, sheet_name='失败城市列表', index=False)
    
    print(f"Excel报告已生成: {excel_filename}")
    print(f"总计测试城市: {total_cities}")
    print(f"成功查询: {successful_cities} ({coverage_rate:.1f}%)")
    print(f"失败查询: {failed_cities}")
    
    return excel_filename

if __name__ == "__main__":
    create_excel_from_batch_results()
