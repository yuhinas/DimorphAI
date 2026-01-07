## ------------------------------------------------------------
## Load packages
## ------------------------------------------------------------
library(dplyr)
library(tidyverse)
library(car)
library(broom)
library(sjPlot)
library(brglm2)
library(DHARMa)
library(ggplot2)

## ------------------------------------------------------------
## Read data
## ------------------------------------------------------------
data <- read.table("female_choice_male_brightness_analyses_DATA.txt", header = TRUE, sep = "\t")

## ------------------------------------------------------------
## Subset males for contingency tests
## ------------------------------------------------------------
df_males <- data %>%
  filter(
    Moth_sex  == "M",
    Treatment %in% c("Rutin", "Control")
  )

## Observed contingency table
tab <- table(df_males$Treatment, df_males$Mating_success)
print(tab)

## Fisher's exact test if any cell of the contingency table counts < 5 
fisher.test(tab)

## Chi-square test if all cells of the contingency table count > 5 
chisq.test(tab, correct = TRUE)

## ------------------------------------------------------------
## Additional factors: prepare male-only dataset
## ------------------------------------------------------------
male_data <- subset(data, Moth_sex == "M")
male_data$Mating_success <- as.numeric(male_data$Mating_success)

## ------------------------------------------------------------
## Logistic regression model
## ------------------------------------------------------------

## Model with Treatment + covariates
model <- glm(Mating_success ~ Treatment + Moth_weight + Marking,
              data = male_data,
              family = binomial)
tab_model(model)

## DHARMa residuals
sim_res <- simulateResiduals(fittedModel = model)
plot(sim_res)

## ------------------------------------------------------------
## Final barplot
## ------------------------------------------------------------

## Compute means + SE
matings_by_treatment <- df_males %>%
  group_by(Treatment) %>%
  summarise(
    Mating_Percent = mean(as.numeric(Mating_success)) * 100,
    SE = sd(as.numeric(Mating_success)) / sqrt(n()) * 100,
    .groups = "drop"
  )

matings_by_treatment$Treatment <- factor(
  matings_by_treatment$Treatment,
  levels = c("Control", "Rutin"),
)

barplot <- ggplot(matings_by_treatment,
                  aes(x = Treatment, y = Mating_Percent)) +
  geom_bar(stat = "identity", width = 0.4,
           fill = "grey70", color = "grey70", linewidth = 0.6) +
  
  geom_errorbar(aes(ymin = Mating_Percent - SE,
                    ymax = Mating_Percent + SE),
                width = 0.1, linewidth = 0.6, color = "black") +
  
  scale_y_continuous(
    breaks = seq(0, 100, 20),
    limits = c(0, 100),
    expand = c(0, 0)
  ) +
  
  labs(x = "Treatment", y = "Mating success (%)") +
  
  theme_minimal() +
  theme(
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    panel.border = element_rect(color = "black", fill = NA, linewidth = 0.8),
    axis.ticks = element_line(color = "black", linewidth = 0.7),
    axis.ticks.length = unit(5, "pt"),
    axis.title.x = element_text(size = 14),
    axis.title.y = element_text(size = 14),
    axis.text.x  = element_text(size = 12),
    axis.text.y  = element_text(size = 12)
  )

barplot

## Add *** significance annotation
barplot +
  annotate("segment", x = 1, xend = 2, y = 93, yend = 93, linewidth = 0.5) +
  annotate("segment", x = 1, xend = 1, y = 93, yend = 91, linewidth = 0.5) +
  annotate("segment", x = 2, xend = 2, y = 93, yend = 91, linewidth = 0.5) +
  annotate("text", x = 1.5, y = 95, label = "***", size = 5, color = "black")
