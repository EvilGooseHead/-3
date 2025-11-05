setwd('C:/Users/ZLY/CSBN')
library(readxl)    # 读取Excel数据
library(dplyr)     # 数据处理
library(ggplot2)   # 高级绘图
library(scales)    # 调整坐标轴格式
library(tidyr)

# 2. 读取Excel数据（假设文件名为movie_ratings.xlsx）
data <- read_excel("douban_reviews1.xlsx") %>%
  mutate(
    time = as.Date(time)
  )
data$rank <- as.numeric(data$rank)
data$rank_2 <- data$rank*2
data$rank <- factor(data$rank,         # 将评分转换为带标签的因子
                    levels = 1:5,
                    labels = c("很差", "较差", "一般", "推荐", "力荐")
)

# 计算逐日评论累计量


# 计算每日评论量
daily_counts <- data %>% 
  filter(time >= as.Date("2025-07-25") & time <= as.Date("2025-08-24"))%>% 
  group_by(time) %>%
  summarise(count = n())%>%
  ungroup()

# 绘制逐日电影评论量走势图
ggplot(daily_counts, aes(x = time, y = count)) +
  geom_line(color = "#B54764", size = 2) +          # 蓝色趋势线
  geom_point(color = "#FEA040", size = 4) +         # 橙色数据点
  labs(
    title = "《南京照相馆》上映以来豆瓣单日评论数量逐日走势",
    x = "日期",
    y = "评论数量"
  ) +
  scale_x_date(date_breaks = "3 days", 
               date_labels = "%Y-%m-%d",        # 日期格式
               minor_breaks = "1 day" ) +           # 日期格式
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
    axis.text.x = element_text(angle = 30, hjust = 1, size = 10),
    axis.text.y = element_text(size = 10),
    axis.title.x = element_text(size = 14),
    axis.title.y = element_text(size = 14)
  )
ggsave("daily_avg_plot.png", width = 10, height = 6)  # 保存图像

# 5. 统计每日各评分人数
daily_counts <- data %>% 
  filter(time >= as.Date("2025-07-25") & time <= as.Date("2025-08-24"))%>% 
  count(time, rank) %>%    # 按日期和评分分组计数
  complete(                 # 补全缺失组合（某日无某评分时）
    time = full_seq(time, period = 1),
    rank,
    fill = list(n = 0)
  )

daily_proportions <- data %>%
  filter(time >= as.Date("2025-07-25") & time <= as.Date("2025-08-24"))%>% 
  count(time, rank) %>%          # 按日期和评分分组计数
  complete(                      # 补全缺失组合（某日无某评分时）
    time = full_seq(time, period = 1),
    rank,
    fill = list(n = 0)
  ) %>%
  group_by(time) %>%             # 按日期分组
  mutate(                         # 计算每日各评分的比例
    proportion = n / sum(n)      # 当前评分频数 ÷ 当日总频数
  ) %>% 
  ungroup()                      # 解除分组
daily_proportions <- daily_proportions %>%
  filter(!is.na(rank))
# 6. 绘制每日各评分人数图
ggplot(daily_proportions, aes(x = time, y = proportion, color = rank)) +  # 用color映射评分等级 daily_counts
  geom_line(linewidth = 1) +  # 绘制折线，调整线条粗细
  labs(
    title = "《南京照相馆》上映以来豆瓣评论各分段占比逐日变化趋势",
    x = "日期",
    y = "当日评分比例",
    color = "评分等级"  # 图例标题
  ) +
  scale_x_date(date_labels = "%Y-%m-%d") +
  scale_color_manual(  # 自定义线条颜色（与柱状图配色一致）
    values = c(
      "很差" = "#B54764", 
      "较差" = "#5861AC", 
      "一般" = "#FEA040", 
      "推荐" = "#979998", 
      "力荐" = "#1a9641",
      "NA" = "red"
    )
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
    axis.text.x = element_text(angle = 30, hjust = 1, size = 10),
    axis.text.y = element_text(size = 10),
    axis.title.x = element_text(size = 14),
    axis.title.y = element_text(size = 14),
    legend.text = element_text(size = 14),
    legend.title = element_text(size = 14),
    legend.position = "right"  # 图例置于顶部
  )
ggsave("daily_counts_plot.png", width = 12, height = 7)

# 计算逐日累计评论量
daily_counts_a <- daily_counts %>%
  arrange(time) %>%               # 确保按日期升序排列
  mutate(cumulative_count = cumsum(count))  # 计算累计值

# 绘制逐日累计评论量图
ggplot(daily_counts_a, aes(x = time, y = cumulative_count)) +
  geom_line(color = "steelblue", size = 1) +
  labs(title = "《南京照相馆》上映以来每日评论累计数量 ",
       x = "日期", y = "累计评论量") +
  scale_x_date(date_breaks = "2 days", date_labels = "%m/%d") +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
    axis.text.x = element_text(angle = 30, hjust = 1, size = 10),
    axis.text.y = element_text(size = 10),
    axis.title.x = element_text(size = 14),
    axis.title.y = element_text(size = 14),
    legend.text = element_text(size = 14),
    legend.title = element_text(size = 14),
    legend.position = "right"  # 图例置于顶部
  )

#计算各省评论数
region_counts <- data %>%  
  count(region, name = "region_freq")  

valid_regions <- region_counts %>%  
  filter(region_freq >= 5, !region %in% c("澳大利亚", "德国", "加拿大", "美国", "新加坡", "智利")) %>%  
  pull(region)  

data2 <- data %>%  
  filter(region %in% valid_regions)

#绘制前10省份的图
top_10_data <- region_counts %>%
  arrange(desc(region_freq)) %>%         # 按样本量降序排序
  slice_head(n = 10) %>%                 # 取前10行
  mutate(region = factor(region),        # 转换为因子
         region = reorder(region, region_freq))  # 按样本量排序因子水平

# 2. 计算总省份数量
total_provinces <- n_distinct(region_counts$region)

# 3. 创建带标注的柱状图
ggplot(top_10_data, aes(x = region, y = region_freq, 
                        fill = region_freq)) +  # 颜色映射样本量
  geom_bar(stat = "identity", width = 0.8) +    # 固定宽度柱状图
  scale_fill_gradient(low = "#4e79a7", high = "#e15759", 
                      name = paste("总地区数:", total_provinces)) + # 图例标题
  labs(title = "《南京照相馆》豆瓣评论量前10省份（截至8月25日）",
       x = "",
       y = "评论量") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1), # 倾斜标签
    legend.position = "right",   # 图例在右侧
    legend.title = element_text(face = "bold", size = 10), # 图例标题样式
    plot.title = element_text(hjust = 0.5, face = "bold")  # 标题居中
  ) +
  geom_text(aes(label = region_freq), 
            vjust = -0.5, 
            size = 3.5)  # 柱顶添加样本量数值

#绘制部分省份均分
filtered_data <- data2 %>%
  group_by(region)%>%
  filter(n() >= 30) %>%
  ungroup()
# 2.计算每组均分
region_means <- filtered_data %>%
  group_by(region) %>%
  summarise(mean_rank = mean(rank_2, na.rm = TRUE)) %>%
  arrange(desc(mean_rank))

# 3. 获取前10名region
top_10 <- region_means %>%
  slice_head(n = 10)

# 4. 计算总region数量
total_regions <- n_distinct(region_means$region)

# 5. 创建柱状图（带图例标注）
ggplot(top_10, aes(x = reorder(region, mean_rank), y = mean_rank, 
                   fill = mean_rank)) +
  geom_bar(stat = "identity", width = 0.7) +
  geom_text(aes(label = round(mean_rank, 2)), 
            vjust = -0.5, size = 3.5, color = "black") +
  scale_fill_gradient(low = "#4e79a7", high = "#e15759", 
                      name = paste("总地区数:", total_regions)) +
  labs(title = "评分均分TOP 10地区（截至8月25日）",
       x = "地区",
       y = "排名均分") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 10),
    legend.position = "right",
    plot.title = element_text(hjust = 0.5, face = "bold", size = 14)
  ) +
  ylim(0, max(top_10$mean_rank) * 1.15)+ annotate(
    "text", 
    x = -Inf, y = 10,            # 定位在绘图区域左下角
    label = "*仅计算评论量大于30的省份",  # 注释内容
    hjust = -0.05, vjust = -1.5,    # 微调位置（左对齐、向上偏移）
    size = 3.5,                    # 字体大小
    color = "black"             # 支持中文的字体（防乱码）
  )  # 为标签留出空间