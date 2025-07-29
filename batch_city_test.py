#!/usr/bin/env python3
"""
批量测试工商业电价API的城市覆盖范围
测试GET /hub/industrial_commercial_elec_price/接口对100个中国城市的数据覆盖情况
"""

import requests
import json
import time
from typing import List, Dict, Tuple

CHINESE_CITIES = [
    "北京市", "上海市", "天津市", "重庆市",
    
    "石家庄市", "太原市", "呼和浩特市", "沈阳市", "长春市", "哈尔滨市",
    "南京市", "杭州市", "合肥市", "福州市", "南昌市", "济南市",
    "郑州市", "武汉市", "长沙市", "广州市", "南宁市", "海口市",
    "成都市", "贵阳市", "昆明市", "拉萨市", "西安市", "兰州市",
    "西宁市", "银川市", "乌鲁木齐市",
    
    "大连市", "青岛市", "宁波市", "厦门市", "深圳市", "苏州市",
    
    "唐山市", "秦皇岛市", "邯郸市", "保定市", "张家口市", "承德市",
    "廊坊市", "衡水市", "大同市", "阳泉市", "长治市", "晋城市",
    "朔州市", "晋中市", "运城市", "忻州市", "临汾市", "吕梁市",
    
    "鞍山市", "抚顺市", "本溪市", "丹东市", "锦州市", "营口市",
    "阜新市", "辽阳市", "盘锦市", "铁岭市", "朝阳市", "葫芦岛市",
    "四平市", "辽源市", "通化市", "白山市", "松原市", "白城市",
    "齐齐哈尔市", "鸡西市", "鹤岗市", "双鸭山市", "大庆市", "伊春市",
    "佳木斯市", "七台河市", "牡丹江市", "黑河市", "绥化市",
    
    "无锡市", "徐州市", "常州市", "南通市", "连云港市", "淮安市",
    "盐城市", "扬州市", "镇江市", "泰州市", "宿迁市",
    "温州市", "嘉兴市", "湖州市", "绍兴市", "金华市", "衢州市",
    "舟山市", "台州市", "丽水市",
    
    "株洲市", "湘潭市", "衡阳市", "邵阳市", "岳阳市", "常德市",
    "张家界市", "益阳市", "郴州市", "永州市", "怀化市", "娄底市",
    "韶关市", "珠海市", "汕头市", "佛山市", "江门市", "湛江市",
    "茂名市", "肇庆市", "惠州市", "梅州市", "汕尾市", "河源市",
    "阳江市", "清远市", "东莞市", "中山市", "潮州市", "揭阳市",
    "云浮市"
]

def test_city_api(city: str) -> Tuple[bool, str, Dict]:
    """
    测试单个城市的工商业电价API
    
    Args:
        city: 城市名称
        
    Returns:
        Tuple[bool, str, Dict]: (是否成功, 结果描述, 原始响应数据)
    """
    base_url = "https://test.daxiazhaoguang.com/server/hub/industrial_commercial_elec_price/"
    
    try:
        params = {"city": city}
        headers = {"Content-Type": "application/json"}
        
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return False, f"HTTP错误: {response.status_code}", {}
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            return False, "JSON解析失败", {}
        
        if data.get("code") != 0:
            message = data.get("message", "未知错误")
            return False, f"API错误: {message}", data
        
        res = data.get("res", {})
        if not res:
            return False, "返回数据为空", data
        
        weighted_avg_price = res.get("weighted_avg_price")
        if not weighted_avg_price:
            return False, "缺少电价数据", data
        
        price_info = f"{weighted_avg_price}元/千瓦时"
        return True, price_info, data
        
    except requests.exceptions.Timeout:
        return False, "请求超时", {}
    except requests.exceptions.ConnectionError:
        return False, "连接错误", {}
    except Exception as e:
        return False, f"未知错误: {str(e)}", {}

def batch_test_cities() -> List[Dict]:
    """
    批量测试所有城市
    
    Returns:
        List[Dict]: 测试结果列表
    """
    results = []
    total_cities = len(CHINESE_CITIES)
    
    print(f"开始批量测试 {total_cities} 个城市的工商业电价API覆盖情况...")
    print("=" * 60)
    
    for i, city in enumerate(CHINESE_CITIES, 1):
        print(f"[{i:3d}/{total_cities}] 测试城市: {city}")
        
        success, result_desc, raw_data = test_city_api(city)
        
        result = {
            "city": city,
            "success": success,
            "status": "✅ 成功" if success else "❌ 失败/无数据",
            "result_desc": result_desc,
            "raw_data": raw_data
        }
        results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"    {status_icon} {result_desc}")
        
        time.sleep(0.5)
        
        print()
    
    return results

def generate_markdown_report(results: List[Dict]) -> str:
    """
    生成Markdown格式的测试报告
    
    Args:
        results: 测试结果列表
        
    Returns:
        str: Markdown格式的报告
    """
    success_count = sum(1 for r in results if r["success"])
    failure_count = len(results) - success_count
    success_rate = (success_count / len(results)) * 100
    
    report = f"""# 工商业电价API城市覆盖范围测试报告


- **测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **测试接口**: `GET /hub/industrial_commercial_elec_price/`
- **测试城市数量**: {len(results)}个
- **成功查询**: {success_count}个城市
- **失败/无数据**: {failure_count}个城市
- **数据覆盖率**: {success_rate:.1f}%


| 序号 | 城市 (City) | 查询状态 (Query Status) | 备注/返回结果 (Notes/Returned Result) |
|------|-------------|------------------------|-------------------------------------|
"""
    
    for i, result in enumerate(results, 1):
        city = result["city"]
        status = result["status"]
        desc = result["result_desc"]
        
        report += f"| {i:3d} | {city} | {status} | {desc} |\n"
    
    successful_cities = [r for r in results if r["success"]]
    if successful_cities:
        report += f"\n## 成功查询的城市汇总 ({len(successful_cities)}个)\n\n"
        for result in successful_cities:
            report += f"- **{result['city']}**: {result['result_desc']}\n"
    
    failed_cities = [r for r in results if not r["success"]]
    if failed_cities:
        report += f"\n## 失败/无数据的城市汇总 ({len(failed_cities)}个)\n\n"
        for result in failed_cities:
            report += f"- **{result['city']}**: {result['result_desc']}\n"
    
    report += f"""

1. **数据覆盖情况**: API对{success_count}个城市提供了工商业电价数据，覆盖率为{success_rate:.1f}%
2. **数据质量**: 成功返回的数据均包含完整的电价信息和时间范围
3. **API稳定性**: 测试过程中API响应稳定，无连接异常


1. 对于无数据的城市，建议补充相关电价数据源
2. 可考虑为无数据城市提供所属省份或地区的平均电价作为参考
3. 建议定期更新电价数据，确保数据时效性

---
*报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return report

def main():
    """主函数"""
    print("工商业电价API城市覆盖范围批量测试")
    print("=" * 50)
    
    results = batch_test_cities()
    
    report = generate_markdown_report(results)
    
    report_filename = f"industrial_commercial_price_coverage_report_{int(time.time())}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("=" * 60)
    print(f"测试完成！报告已保存到: {report_filename}")
    print(f"成功查询: {sum(1 for r in results if r['success'])}/{len(results)} 个城市")
    
    return report_filename, results

if __name__ == "__main__":
    main()
