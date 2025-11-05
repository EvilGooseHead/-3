import time as time_module
import random
from lxml import etree
import requests

# 初始化存储所有评论链接的列表
all_t_list = []  # 使用新变量存储所有链接，备用

# 设置请求头（模拟真实访问设备和登录状态，结合个人设备修改headers和cookies信息）
headers = {
     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
}
cookies = {"bid": "uRAT4HcFvd4",
    "ll": "118159",
    "_vwo_uuid_v2": "DB89F2040BA7DCF2FBDC2ACABE6F325AA|00cc529578c555402055ac2f8aa92c1e",
    "push_noty_num": "0",
    "push_doumail_num": "0",
    "__utmv": "30149280.24939",
    "dbcl2": "249393490:T8A404Ad9iY",
    "ck": "XYX3",
    "__utmc": "30149280",
    "__utmz": "30149280.1755846518.13.6.utmcsr=ntp.msn.cn|utmccn=(referral)|utmcmd=referral|utmcct=/",
    "frodotk_db": "eac05c75729a34ecc041156057ce9ec4",
    "__utma": "30149280.733099250.1754362120.1755846518.1756092695.14"}


# 起始页参数，用于完成翻页
start = 0  #起始页为0
page_size = 20  # 每+20为翻一页，见下文

# 循环处理每一页评论
while True:
     # 构建当前页URL
     url = f'https://movie.douban.com/subject/36809864/reviews?sort=hotest&start={start}'
     # 浏览时注意到每页的链接只有start=后面的内容不同，且每+20为翻页，借助这个规律完成翻页功能
     # 36809864是《南京照相馆》的电影编号，不同电影编号不同
     print(f"\n正在处理第 {start // page_size + 1} 页: {url}") #print()报告运行进度

     delay = random.uniform(5, 10)  #delay在页面上停留，5-10秒，用于模拟真人访问
     print(f"等待 {delay:.2f} 秒后请求页面...")
     time_module.sleep(delay)

     try:
          # 请求当前页
          response = requests.get(url=url, cookies = cookies, headers=headers)
          response.raise_for_status()
          page_text = response.text
     except Exception as e:
          print(f"请求失败: {e}")
          break  # 如果请求失败，退出循环并报告；请求成功则接着往下运行

     # 数据解析
     tree = etree.HTML(page_text)
     div_list = tree.xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/*') #观察发现每页上每条评论的链接的xpath都有相似性，故使用

     # 如果当前页没有评论，退出循环
     if not div_list:
          print("没有更多评论")
          break

     # 收集当前页的评论链接
     t_list = []  # 新建列表t_list,用于储存当前页的链接（临时使用）
     for d in div_list:
          t = d.xpath('.//div/div/h2/a/@href')

          if t:
               full_url = t[0] if t[0].startswith('http') else 'https://movie.douban.com' + t[0]
               t_list.append(full_url)
          else:
               print(f"未找到链接")

     # 添加到总列表，将一个个t_list合并
     all_t_list.extend(t_list)
     print(f"当前页获取到 {len(t_list)} 条评论链接，总链接数: {len(all_t_list)}")

     # 检查是否有下一页
     next_page = tree.xpath('//span[@class="next"]/a')
     if not next_page:
          print("已到达最后一页")
          break

     # 翻页
     start += page_size

     # 随机延迟，模拟真人访问页面（5到8秒）
     delay = random.uniform(5, 8)
     print(f"等待 {delay:.2f} 秒后进入下一页...")
     time_module.sleep(delay)

# 使用原变量名t_list存储所有链接（其实就是改个名）
t_list = all_t_list
print(f"\n成功获取 {len(t_list)} 条评论链接")
#到此就获得了当前每条评论的链接，下面开始访问这些链接并提取评论相关内容

# 初始化存储列表，用于存储每条评论的各种信息
head_list = []
date_list = []
time_list = []
region_list = []
rank_list = []
author_list = []
text_list = []

# 遍历每个评论详情页
for i, link in enumerate(t_list):
     print(f"\n处理第 {i + 1}/{len(t_list)} 条评论: {link}")

     # 随机延迟，模拟真访问
     delay = random.uniform(1, 15)
     print(f"等待 {delay:.2f} 秒...")
     time_module.sleep(delay)

     try:
          # 访问每条评论的详情页
          response2 = requests.get(url=link, cookies=cookies, headers=headers)
          response2.raise_for_status()
          page_text2 = response2.text
     except Exception as e:#将无法访问的评论的各种信息存储为缺失值“请求失败”
          print(f"请求失败: {e}")
          # 为所有字段添加占位符
          head_list.append("请求失败")
          date_list.append('请求失败')
          time_list.append("请求失败")
          region_list.append("请求失败")
          rank_list.append("请求失败")
          author_list.append("请求失败")
          text_list.append("请求失败")
          continue

     # 解析评论详情
     tree2 = etree.HTML(page_text2)

     # 1. 提取标题
     head = tree2.xpath('//h1/span/text()')
     if head:
          head_list.append(head[0].strip())
     else:
          head_list.append("无标题")
          print("未找到标题")

     # 2. 提取日期
     date_comment = tree2.xpath('//span[@property="v:dtreviewed"]/@content') or tree2.xpath(
          '/html/body/div[3]/div[1]/div/div[1]/div[1]/div/header/div/span[1]/@content')
     if date_comment:
          date_list.append(date_comment[0].strip())
     else:
          date_list.append("无日期信息")
          print("未找到日期")

     # 3. 提取时间
     time_comment = tree2.xpath('//span[@property="v:dtreviewed"]') or tree2.xpath(
          '/html/body/div[3]/div[1]/div/div[1]/div[1]/div/header/div/span[1]')
     if time_comment:
          element = time_comment[0]  # 取第一个匹配元素
          full_text = element.text.strip()
          parts = full_text.split()
          time_str = parts[1] if len(parts) > 1 else ""
          time_list.append(time_str)
     else:
          time_list.append("无时间信息")
          print("未找到时间")

     # 4. 提取地区
     region = tree2.xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div/header/div/span[3]/text()')
     if region:
          # 清理地区字符串
          region_str = region[0].replace("来自", "").strip()
          region_list.append(region_str)
     else:
          region_list.append("无地区信息")
          print("未找到地区")

     # 5. 提取评分
     rank = tree2.xpath('//span[@class="allstar50 main-title-rating"]/@title') or tree2.xpath(
          '//span[contains(@class,"main-title-rating")]/@title')
     if rank:
          rank_list.append(rank[0])
     else:
          rank_list.append("无评分")
          print("未找到评分")

     # 6. 提取作者
     author = tree2.xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div/div[1]/div[1]/div[1]/@data-author')
     if author:
          author_list.append(author[0])
     else:
          author_list.append("无作者")
          print("未找到作者")

     # 7. 提取文本
     text = tree2.xpath('string(/html/body/div[3]/div[1]/div/div[1]/div[1]/div/div[1]/div[1]/div[1])')
     if text:
          # 清理多余空格
          clean_text = ' '.join(text.split())
          text_list.append(clean_text)
     else:
          text_list.append("无影评")
          print("未找到影评")
# 打印结果
print("\n标题列表:", head_list)
print("日期列表:", date_list)
print("时间列表:", time_list)
print("地区列表:", region_list)
print("评分列表:", rank_list)
print('作者列表', author_list)
print('影评列表', text_list)

# 检查评论的每个“变量”长度是否一致
if len(head_list) != len(t_list):
     print(f"警告: 标题列表长度({len(head_list)})不等于链接列表长度({len(t_list)})")
if len(date_list) != len(t_list):
     print(f"警告: 日期列表长度({len(date_list)})不等于链接列表长度({len(t_list)})")
if len(time_list) != len(t_list):
     print(f"警告: 时间列表长度({len(time_list)})不等于链接列表长度({len(t_list)})")
if len(region_list) != len(t_list):
     print(f"警告: 地区列表长度({len(region_list)})不等于链接列表长度({len(t_list)})")
if len(rank_list) != len(t_list):
     print(f"警告: 评分列表长度({len(rank_list)})不等于链接列表长度({len(t_list)})")
if len(author_list) != len(t_list):
     print(f"警告: 作者列表长度({len(author_list)})不等于链接列表长度({len(t_list)})")
if len(text_list) != len(t_list):
     print(f"警告: 影评列表长度({len(text_list)})不等于链接列表长度({len(t_list)})")


# 保存为CSV
with open('douban_reviews1.csv', 'w', encoding='utf-8-sig') as f:
     f.write("标题,日期,时间,地区,评分,作者,影评,链接\n")
     for title, date_str, time_str, region, rank, author, text , link  in zip(head_list, date_list, time_list, region_list, rank_list, author_list, text_list, t_list):
          f.write(f'"{title}","{date_str}","{time_str}","{region}","{rank}","{author}","{text}","{link}"\n')
print("\n结果已保存到 douban_reviews1.csv")