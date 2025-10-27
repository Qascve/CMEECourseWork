library(ggplot2)
library(dplyr)
library(here)  # 用于智能路径管理

# 读取数据
# 使用here包从data目录读取数据文件
# here()会自动定位项目根目录，无论脚本从哪里运行都能正确找到文件
data <- read.csv(here("week4", "data", "EcolArchives-E089-51-D1.csv"), stringsAsFactors = FALSE)

# 数据探索
cat("数据集维度:", dim(data), "\n")
cat("数据集列名:\n")
print(names(data))

# 查看取食类型的唯一值
cat("\n取食类型的唯一值:\n")
print(unique(data$Type.of.feeding.interaction))

# 查看捕食者生命阶段的唯一值
cat("\n捕食者生命阶段的唯一值:\n")
print(unique(data$Predator.lifestage))

# 数据清洗：移除包含NA值的行
data <- data[complete.cases(data[, c("Predator.mass", "Prey.mass", 
                                      "Type.of.feeding.interaction", 
                                      "Predator.lifestage")]), ]

# 过滤掉质量值为0或负数的数据
data <- data[data$Predator.mass > 0 & data$Prey.mass > 0, ]

cat("\n清洗后的数据集维度:", dim(data), "\n")

# ============================================================================
# 创建包含所有取食类型和捕食者生命阶段组合的回归图
# ============================================================================

# 创建ggplot对象，使用对数坐标
p <- ggplot(data, aes(x = Prey.mass, y = Predator.mass, 
                      color = Predator.lifestage)) +
  # 添加散点
  geom_point(alpha = 0.6, size = 1.5) +
  # 分面显示：按取食类型分组
  # 使用scales = "fixed"确保所有分面使用相同的纵坐标范围
  facet_grid(Type.of.feeding.interaction ~ ., 
             scales = "fixed") +
  # 添加回归线和置信区间
  geom_smooth(method = "lm", se = TRUE, size = 0.8, alpha = 0.2) +
  # 使用对数坐标
  scale_x_log10(name = "Prey Mass in grams") +
  scale_y_log10(name = "Predator mass in grams",
                labels = scales::scientific) +  # 使用科学记数法
  # 设置主题
  theme_bw() +
  theme(
    # 调整分面标签
    strip.text.y = element_text(angle = 0, hjust = 0, size = 8),
    strip.background = element_rect(fill = "lightgray"),
    # 调整图例
    legend.position = "bottom",
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 8),
    # 调整坐标轴
    axis.text = element_text(size = 8),
    axis.title = element_text(size = 10)
  ) +
  # 设置图例标题
  labs(color = "Predator.lifestage")

# 保存图形到results目录
# 使用here包构建路径，确保路径的可移植性
pdf(here("week4", "results", "PP_Regress.pdf"), width = 10, height = 12)
print(p)
dev.off()

cat("\n回归图已保存到", here("week4", "results", "PP_Regress.pdf"), "\n")

# ============================================================================
# 计算每个取食类型 × 捕食者生命阶段组合的回归统计结果
# ============================================================================

# 获取所有取食类型和捕食者生命阶段的唯一组合
feeding_types <- unique(data$Type.of.feeding.interaction)
life_stages <- unique(data$Predator.lifestage)

# 初始化结果数据框
results <- data.frame(
  Feeding.Type = character(),
  Predator.Lifestage = character(),
  Slope = numeric(),
  Intercept = numeric(),
  R.squared = numeric(),
  F.statistic = numeric(),
  P.value = numeric(),
  Sample.Size = integer(),
  stringsAsFactors = FALSE
)

# 使用嵌套循环遍历所有组合
# 也可以使用dplyr的group_by和do函数来实现
for (feeding in feeding_types) {
  for (stage in life_stages) {
    # 筛选当前组合的数据子集
    subset_data <- data[data$Type.of.feeding.interaction == feeding & 
                        data$Predator.lifestage == stage, ]
    
    # 检查是否有足够的数据点进行回归（至少需要3个点）
    if (nrow(subset_data) >= 3) {
      # 对对数转换后的数据进行线性回归
      # log(Predator.mass) ~ log(Prey.mass)
      model <- lm(log(Predator.mass) ~ log(Prey.mass), data = subset_data)
      
      # 提取回归统计量
      model_summary <- summary(model)
      
      # 提取系数
      intercept <- coef(model)[1]  # 截距
      slope <- coef(model)[2]      # 斜率
      
      # 提取R平方值
      r_squared <- model_summary$r.squared
      
      # 提取F统计量
      f_statistic <- model_summary$fstatistic[1]
      
      # 提取p值
      p_value <- pf(model_summary$fstatistic[1], 
                   model_summary$fstatistic[2], 
                   model_summary$fstatistic[3], 
                   lower.tail = FALSE)
      
      # 样本量
      n <- nrow(subset_data)
      
      # 将结果添加到数据框
      results <- rbind(results, data.frame(
        Feeding.Type = feeding,
        Predator.Lifestage = stage,
        Slope = slope,
        Intercept = intercept,
        R.squared = r_squared,
        F.statistic = f_statistic,
        P.value = p_value,
        Sample.Size = n,
        stringsAsFactors = FALSE
      ))
    }
  }
}

# 按取食类型和生命阶段排序结果
results <- results[order(results$Feeding.Type, results$Predator.Lifestage), ]

# 重置行名
rownames(results) <- NULL

# 打印结果摘要
cat("\n回归分析结果摘要:\n")
cat("总共分析了", nrow(results), "个取食类型和捕食者生命阶段组合\n\n")
print(results)

# 保存结果到CSV文件
# 使用here包构建路径
write.csv(results, here("week4", "results", "PP_Regress_Results.csv"), row.names = FALSE)

cat("\n回归统计结果已保存到", here("week4", "results", "PP_Regress_Results.csv"), "\n")

# ============================================================================
# 额外分析：使用dplyr实现相同功能（更简洁的替代方法）
# ============================================================================

# 注释掉的代码展示了使用dplyr的替代实现方式
# results_dplyr <- data %>%
#   group_by(Type.of.feeding.interaction, Predator.lifestage) %>%
#   filter(n() >= 3) %>%  # 只保留样本量>=3的组
#   do({
#     model <- lm(log(Predator.mass) ~ log(Prey.mass), data = .)
#     model_summary <- summary(model)
#     data.frame(
#       Slope = coef(model)[2],
#       Intercept = coef(model)[1],
#       R.squared = model_summary$r.squared,
#       F.statistic = model_summary$fstatistic[1],
#       P.value = pf(model_summary$fstatistic[1], 
#                    model_summary$fstatistic[2], 
#                    model_summary$fstatistic[3], 
#                    lower.tail = FALSE),
#       Sample.Size = nrow(.)
#     )
#   }) %>%
#   ungroup()

cat("\n脚本执行完成！\n")
cat("生成的文件:\n")
cat("1.", here("week4", "results", "PP_Regress.pdf"), "- 回归图\n")
cat("2.", here("week4", "results", "PP_Regress_Results.csv"), "- 回归统计结果\n")
