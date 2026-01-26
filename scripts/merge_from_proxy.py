#!/usr/bin/env python3
"""
从两个源下载最新M3U文件并合并
1. BB.m3u: https://raw.githubusercontent.com/sufernnet/joker/main/BB.m3u
2. JULI.m3u: 从代理获取
合并后生成CC.m3u，使用最新的EPG信息
"""

import requests
import re
import os
from datetime import datetime

# 配置
PROXY_URL = "https://smt-proxy.sufern001.workers.dev/"
BB_URL = "https://raw.githubusercontent.com/sufernnet/joker/main/BB.m3u"

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def download_bb_m3u():
    """下载BB.m3u并提取内容和EPG"""
    try:
        log("下载 BB.m3u...")
        response = requests.get(BB_URL, timeout=10)
        response.raise_for_status()
        
        bb_content = response.text
        log(f"✅ BB.m3u 下载成功 ({len(bb_content)} 字符)")
        
        # 提取EPG信息
        epg_url = None
        if 'url-tvg=' in bb_content:
            match = re.search(r'url-tvg="([^"]+)"', bb_content)
            if match:
                epg_url = match.group(1)
                log(f"✅ 提取到BB的EPG: {epg_url}")
        
        return bb_content, epg_url
        
    except Exception as e:
        log(f"❌ BB.m3u 下载失败: {e}")
        return "", None

def download_juli_m3u():
    """从代理下载JULI的M3U文件"""
    try:
        log("从代理下载JULI的M3U...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 尝试获取页面内容
        response = requests.get(PROXY_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        html_content = response.text
        
        # 尝试查找M3U链接
        m3u_links = re.findall(r'https?://[^\s"\']+\.m3u(?:\?[^\s"\']*)?', html_content, re.IGNORECASE)
        
        if m3u_links:
            log(f"找到 {len(m3u_links)} 个M3U链接")
            # 尝试下载第一个M3U链接
            for link in m3u_links[:3]:  # 只尝试前3个
                try:
                    log(f"尝试下载: {link}")
                    m3u_response = requests.get(link, headers=headers, timeout=10)
                    if m3u_response.status_code == 200 and m3u_response.text.strip():
                        content = m3u_response.text
                        log(f"✅ JULI M3U下载成功 ({len(content)} 字符)")
                        
                        # 提取EPG信息
                        epg_url = None
                        if 'x-tvg-url=' in content:
                            match = re.search(r'x-tvg-url="([^"]+)"', content)
                            if match:
                                epg_url = match.group(1)
                                log(f"✅ 提取到JULI的EPG: {epg_url}")
                        
                        return content, epg_url
                except Exception as e:
                    log(f"下载链接失败 {link}: {e}")
        
        # 如果没有找到M3U链接，尝试直接提取内容
        log("尝试直接从页面提取M3U内容...")
        
        # 检查页面是否本身就是M3U
        if html_content.startswith('#EXTM3U'):
            log(f"✅ 页面本身就是M3U文件 ({len(html_content)} 字符)")
            
            # 提取EPG信息
            epg_url = None
            if 'x-tvg-url=' in html_content:
                match = re.search(r'x-tvg-url="([^"]+)"', html_content)
                if match:
                    epg_url = match.group(1)
                    log(f"✅ 提取到JULI的EPG: {epg_url}")
            
            return html_content, epg_url
        
        # 尝试提取频道信息
        lines = html_content.split('\n')
        m3u_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith('#EXTINF:') or ('://' in line and not line.startswith('<')):
                m3u_lines.append(line)
        
        if m3u_lines:
            content = '#EXTM3U\n' + '\n'.join(m3u_lines)
            log(f"✅ 从页面提取到M3U内容 ({len(content)} 字符)")
            return content, None
        
        log("❌ 无法获取JULI的M3U内容")
        return None, None
        
    except Exception as e:
        log(f"❌ 下载JULI M3U失败: {e}")
        return None, None

def extract_hk_channels(m3u_content):
    """从JULI的M3U内容中提取频道并改为HK分组"""
    if not m3u_content:
        return []
    
    log("提取JULI频道并改为HK分组...")
    lines = m3u_content.split('\n')
    channels = []
    seen_channels = set()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 寻找包含JULI的行（不区分大小写）
        if line and 'JULI' in line.upper():
            # 向前找EXTINF行
            extinf_line = None
            for j in range(max(0, i-3), i+1):
                if lines[j].strip().startswith('#EXTINF:'):
                    extinf_line = lines[j].strip()
                    break
            
            # 向后找URL行
            url_line = None
            if extinf_line:
                for k in range(i+1, min(len(lines), i+4)):
                    test_line = lines[k].strip()
                    if test_line and not test_line.startswith('#') and '://' in test_line:
                        url_line = test_line
                        break
            
            # 如果找到了EXTINF和URL
            if extinf_line and url_line:
                # 修改频道名称：把JULI改成HK
                new_extinf = extinf_line
                if 'JULI' in new_extinf.upper():
                    # 使用正则替换所有JULI为HK
                    new_extinf = re.sub(r'JULI', 'HK', new_extinf, flags=re.IGNORECASE)
                
                # 创建频道唯一标识（用于去重）
                channel_id = f"{new_extinf}|{url_line}"
                
                if channel_id not in seen_channels:
                    seen_channels.add(channel_id)
                    channels.append((new_extinf, url_line))
        
        i += 1
    
    log(f"✅ 提取到 {len(channels)} 个HK频道（原JULI频道）")
    
    return channels

def choose_epg(bb_epg, juli_epg):
    """选择EPG源（优先使用BB的）"""
    if bb_epg:
        log(f"✅ 使用BB的EPG源: {bb_epg}")
        return bb_epg
    elif juli_epg:
        log(f"✅ 使用JULI的EPG源: {juli_epg}")
        return juli_epg
    else:
        log("⚠️  未找到EPG源")
        return None

def main():
    """主函数"""
    log("开始合并M3U文件...")
    
    # 1. 下载BB.m3u
    bb_content, bb_epg = download_bb_m3u()
    if not bb_content:
        log("❌ BB.m3u下载失败，无法继续")
        return
    
    # 2. 下载JULI的M3U
    juli_content, juli_epg = download_juli_m3u()
    
    # 3. 选择EPG源
    epg_url = choose_epg(bb_epg, juli_epg)
    
    # 4. 从JULI内容中提取HK频道
    hk_channels = []
    if juli_content:
        hk_channels = extract_hk_channels(juli_content)
    
    # 5. 构建合并后的M3U内容
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建M3U头部
    if epg_url:
        output = f'#EXTM3U url-tvg="{epg_url}"\n'
    else:
        output = '#EXTM3U\n'
    
    output += f"""# 自动合并 M3U 文件
# 生成时间: {timestamp}
# 源1: {BB_URL}
# 源2: {PROXY_URL}
# JULI分组已改为HK分组
# EPG源: {epg_url if epg_url else '无'}
# GitHub Actions 自动生成

"""
    
    # 添加BB内容（跳过开头的#EXTM3U行）
    bb_lines = bb_content.split('\n')
    bb_count = 0
    skip_first_line = True
    
    for line in bb_lines:
        line = line.rstrip()
        if not line:
            continue
        
        # 跳过原始的第一行
        if skip_first_line and line.startswith('#EXTM3U'):
            skip_first_line = False
            continue
        
        output += line + '\n'
        if line.startswith('#EXTINF:'):
            bb_count += 1
    
    # 添加HK频道（原JULI频道）
    if hk_channels:
        output += f"\n# HK 频道 (原JULI频道)\n"
        for extinf, url in hk_channels:
            output += extinf + '\n'
            output += url + '\n'
    
    # 添加统计信息
    output += f"""
# 统计信息
# BB 频道数: {bb_count}
# HK 频道数: {len(hk_channels)}
# 总频道数: {bb_count + len(hk_channels)}
# 更新时间: {timestamp}
# 下次更新: 每天 06:00 和 18:00 (北京时间)
"""
    
    # 6. 保存文件
    output_file = "CC.m3u"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)
    
    log(f"\n🎉 合并完成!")
    log(f"📁 文件: {output_file}")
    log(f"📏 大小: {len(output)} 字符")
    if epg_url:
        log(f"📡 EPG地址: {epg_url}")
    log(f"📺 BB频道: {bb_count}")
    log(f"📺 HK频道: {len(hk_channels)}")
    log(f"📺 总计: {bb_count + len(hk_channels)}")
    
    # 7. 保存EPG信息用于下次比较
    with open("last_epg.txt", "w", encoding="utf-8") as f:
        f.write(f"BB_EPG: {bb_epg or '无'}\n")
        f.write(f"JULI_EPG: {juli_epg or '无'}\n")
        f.write(f"使用_EPG: {epg_url or '无'}\n")
        f.write(f"更新时间: {timestamp}\n")

if __name__ == "__main__":
    main()
