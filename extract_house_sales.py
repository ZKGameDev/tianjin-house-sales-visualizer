#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
房屋销售信息提取脚本
从HTML文件中提取房屋销售情况并输出到文件
"""

import sys
import os
import re
from bs4 import BeautifulSoup
import argparse
import json
from datetime import datetime


def extract_house_sales_info(html_file_path):
    """
    从HTML文件中提取房屋销售信息
    
    Args:
        html_file_path (str): HTML文件路径
        
    Returns:
        dict: 包含提取到的房屋销售信息
    """
    try:
        # 读取HTML文件
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取基本信息
        basic_info = {}
        
        # 提取房屋坐落信息
        # 更新选择器以匹配实际的HTML结构
        label_elements = soup.find_all('span', class_=lambda x: x and 'el-descriptions-item__label' in x)
        
        for label in label_elements:
            label_text = label.get_text(strip=True)
            # 查找对应的content元素（下一个兄弟元素）
            content_element = label.find_next_sibling('span', class_=lambda x: x and 'el-descriptions-item__content' in x)
            
            if content_element:
                content_text = content_element.get_text(strip=True)
                
                if '项目名称' in label_text:
                    basic_info['项目名称'] = content_text
                elif '房屋坐落' in label_text:
                    basic_info['房屋坐落'] = content_text
                elif '销售面积' in label_text:
                    basic_info['销售面积'] = content_text
                elif '销售许可证证载用途' in label_text:
                    basic_info['销售许可证证载用途'] = content_text
                elif '许可证号' in label_text:
                    basic_info['许可证号'] = content_text
        
        # 如果仍然没有找到项目名称，尝试备用方法
        if '项目名称' not in basic_info:
            # 从页面标题提取
            title_element = soup.find('title')
            if title_element:
                title_text = title_element.get_text(strip=True)
                # 尝试从标题中提取项目名称
                if '商品房销售许可证信息' in title_text:
                    # 提取标题中的项目名称部分
                    project_name = title_text.replace('商品房销售许可证信息', '').strip()
                    if project_name:
                        basic_info['项目名称'] = project_name
        
        # 提取房屋详细信息
        house_details = []
        
        # 查找表格行
        table_rows = soup.find_all('tr', class_='el-table__row')
        
        for row in table_rows:
            cells = row.find_all('td', class_='el-table__cell')
            if len(cells) >= 5:  # 确保有足够的列
                house_info = {}
                
                # 提取房间号
                room_cell = cells[0]
                room_div = room_cell.find('div', class_='cell')
                if room_div:
                    house_info['房间号'] = room_div.get_text(strip=True)
                
                # 提取建筑面积
                area_cell = cells[1]
                area_div = area_cell.find('div', class_='cell')
                if area_div:
                    house_info['建筑面积'] = area_div.get_text(strip=True)
                
                # 提取申报销售单价
                price_cell = cells[2]
                price_div = price_cell.find('div', class_='cell')
                if price_div:
                    house_info['申报销售单价'] = price_div.get_text(strip=True)
                
                # 提取是否出售
                sold_cell = cells[3]
                sold_div = sold_cell.find('div', class_='cell')
                if sold_div:
                    house_info['是否出售'] = sold_div.get_text(strip=True)
                
                # 提取是否抵押
                mortgage_cell = cells[4]
                mortgage_div = mortgage_cell.find('div', class_='cell')
                if mortgage_div:
                    house_info['是否抵押'] = mortgage_div.get_text(strip=True)
                
                # 只有当房间号不为空时才添加到列表中
                if house_info.get('房间号'):
                    house_details.append(house_info)
        
        # 统计信息
        total_houses = len(house_details)
        sold_houses = len([h for h in house_details if h.get('是否出售') == '已售'])
        mortgaged_houses = len([h for h in house_details if h.get('是否抵押') == '是'])
        
        # 计算总面积
        total_area = 0
        for house in house_details:
            area_text = house.get('建筑面积', '')
            if area_text:
                try:
                    # 如果包含平方米，去掉；否则直接转换
                    if '平方米' in area_text:
                        area_value = float(area_text.replace('平方米', ''))
                    else:
                        area_value = float(area_text)
                    total_area += area_value
                except ValueError:
                    pass
        
        # 构建结果
        result = {
            '基本信息': basic_info,
            '房屋详情': house_details,
            '统计信息': {
                '总房屋数': total_houses,
                '已售房屋数': sold_houses,
                '未售房屋数': total_houses - sold_houses,
                '抵押房屋数': mortgaged_houses,
                '总面积': f"{total_area:.2f}平方米",
                '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return result
        
    except Exception as e:
        print(f"提取过程中发生错误: {str(e)}")
        return None


def save_to_file(data, output_file):
    """
    将提取的数据保存到文件
    
    Args:
        data (dict): 提取的数据
        output_file (str): 输出文件路径
    """
    try:
        # 根据文件扩展名决定输出格式
        if output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif output_file.endswith('.txt'):
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("房屋销售信息提取报告\n")
                f.write("=" * 50 + "\n\n")
                
                # 基本信息
                f.write("基本信息:\n")
                f.write("-" * 20 + "\n")
                for key, value in data['基本信息'].items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
                
                # 统计信息
                f.write("统计信息:\n")
                f.write("-" * 20 + "\n")
                for key, value in data['统计信息'].items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
                
                # 房屋详情
                f.write("房屋详情:\n")
                f.write("-" * 20 + "\n")
                for i, house in enumerate(data['房屋详情'], 1):
                    f.write(f"房屋 {i}:\n")
                    for key, value in house.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
        else:
            # 默认输出为JSON格式
            output_file = output_file + '.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已成功保存到: {output_file}")
        
    except Exception as e:
        print(f"保存文件时发生错误: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='提取HTML文件中的房屋销售信息')
    parser.add_argument('html_file', help='HTML文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径 (可选，默认为输入文件名_销售信息.json)')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.html_file):
        print(f"错误: 文件 '{args.html_file}' 不存在")
        sys.exit(1)
    
    # 确定输出文件路径
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(args.html_file)[0]
        output_file = f"{base_name}_销售信息.json"
    
    print(f"正在处理文件: {args.html_file}")
    
    # 提取数据
    data = extract_house_sales_info(args.html_file)
    
    if data:
        print(f"成功提取到 {data['统计信息']['总房屋数']} 套房屋信息")
        print(f"已售房屋: {data['统计信息']['已售房屋数']} 套")
        print(f"未售房屋: {data['统计信息']['未售房屋数']} 套")
        print(f"抵押房屋: {data['统计信息']['抵押房屋数']} 套")
        
        # 保存数据
        save_to_file(data, output_file)
    else:
        print("提取失败，请检查HTML文件格式")
        sys.exit(1)


if __name__ == "__main__":
    main() 